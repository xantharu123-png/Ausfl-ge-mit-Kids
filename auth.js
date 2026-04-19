// ============================================
// Familienguide 2026 — Auth + Freemium + Sync
// ============================================

// ---- SUPABASE CONFIG ----
// Du musst diese Werte mit deinem eigenen Supabase-Projekt ersetzen!
// 1. Gehe zu https://supabase.com → neues Projekt erstellen
// 2. Unter Settings → API findest du URL und anon key
const SUPABASE_URL = localStorage.getItem('fg_supabase_url') || 'https://DEIN-PROJEKT.supabase.co';
const SUPABASE_ANON_KEY = localStorage.getItem('fg_supabase_key') || 'DEIN-ANON-KEY';

let supabase = null;
let currentUser = null;
let userPlan = 'free'; // 'free' or 'premium'

const fallbackFreeCountryFiles = [
  'index.html',
  'map_deutschland.html',
  'map_frankreich.html',
  'map_oesterreich.html'
];

function normalizeCountryFile(value) {
  if (!value) {
    return '';
  }

  return String(value).split(/[?#]/)[0].split('/').pop();
}

const guideConfig = window.GuideConfig || {
  PREMIUM_PLAN: 'premium',
  FREE_COUNTRY_FILES: fallbackFreeCountryFiles,
  normalizeFileName: normalizeCountryFile,
  isLockedCountryFile(fileName, plan) {
    if (plan === 'premium') {
      return false;
    }

    const normalized = normalizeCountryFile(fileName);
    return !!normalized && fallbackFreeCountryFiles.indexOf(normalized) === -1;
  }
};

// ---- INIT ----
async function initAuth() {
  // Load Supabase client
  if (typeof window.supabase !== 'undefined' && SUPABASE_URL !== 'https://DEIN-PROJEKT.supabase.co') {
    try {
      supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

      // Check existing session
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        currentUser = session.user;
        await loadUserPlan();
        showApp();
        syncUserData();
        return;
      }

      // Listen for auth changes
      supabase.auth.onAuthStateChange(async (event, session) => {
        if (event === 'SIGNED_IN' && session) {
          currentUser = session.user;
          await loadUserPlan();
          showApp();
          syncUserData();
        } else if (event === 'SIGNED_OUT') {
          currentUser = null;
          userPlan = 'free';
          showLogin();
        }
      });
    } catch (e) {
      console.warn('Supabase init failed:', e);
    }
  }

  // Check localStorage fallback (demo mode without Supabase)
  const localUser = localStorage.getItem('fg_user');
  if (localUser) {
    currentUser = JSON.parse(localUser);
    userPlan = localStorage.getItem('fg_plan') || 'free';
    showApp();
    return;
  }

  showLogin();
}

// ---- LOGIN UI ----
function showLogin() {
  document.getElementById('auth-overlay').style.display = 'flex';
  document.getElementById('app-container').style.display = 'none';
}

function showApp() {
  if (currentUser) {
    localStorage.setItem('fg_user', JSON.stringify(currentUser));
  }
  localStorage.setItem('fg_plan', userPlan);

  document.getElementById('auth-overlay').style.display = 'none';
  document.getElementById('app-container').style.display = 'flex';

  // Update user info in UI
  updateUserUI();

  // Apply freemium limits
  if (userPlan === 'free') {
    applyFreemiumLimits();
  }

  // Trigger map resize (important after display change)
  setTimeout(() => {
    if (typeof map !== 'undefined' && map) {
      map.invalidateSize();
    }
  }, 100);
}

function updateUserUI() {
  const badge = document.getElementById('plan-badge');
  const userBtn = document.getElementById('user-menu-btn');

  if (badge) {
    if (userPlan === 'premium') {
      badge.textContent = '⭐ Premium';
      badge.className = 'plan-badge premium';
    } else {
      badge.textContent = 'Free';
      badge.className = 'plan-badge free';
    }
  }

  if (userBtn && currentUser) {
    const name = currentUser.user_metadata?.full_name || currentUser.email?.split('@')[0] || 'User';
    userBtn.textContent = name.charAt(0).toUpperCase();
    userBtn.title = name;
  }
}

// ---- AUTH METHODS ----
async function loginWithEmail() {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errorEl = document.getElementById('login-error');

  if (!email || !password) {
    errorEl.textContent = 'Bitte E-Mail und Passwort eingeben';
    return;
  }

  if (supabase) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      if (error.message.includes('Invalid login')) {
        errorEl.textContent = 'E-Mail oder Passwort falsch';
      } else {
        errorEl.textContent = error.message;
      }
      return;
    }
  } else {
    // Demo mode — local login
    currentUser = { email, user_metadata: { full_name: email.split('@')[0] } };
    localStorage.setItem('fg_user', JSON.stringify(currentUser));
    userPlan = localStorage.getItem('fg_plan') || 'free';
    showApp();
  }
}

async function signupWithEmail() {
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const name = document.getElementById('signup-name').value.trim();
  const errorEl = document.getElementById('signup-error');

  if (!email || !password) {
    errorEl.textContent = 'Bitte alle Felder ausfüllen';
    return;
  }
  if (password.length < 6) {
    errorEl.textContent = 'Passwort muss mindestens 6 Zeichen haben';
    return;
  }

  if (supabase) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: name } }
    });
    if (error) {
      errorEl.textContent = error.message;
      return;
    }
    errorEl.style.color = '#4ecca3';
    errorEl.textContent = '✓ Bestätigungsmail gesendet! Bitte E-Mail prüfen.';
  } else {
    // Demo mode
    currentUser = { email, user_metadata: { full_name: name } };
    localStorage.setItem('fg_user', JSON.stringify(currentUser));
    userPlan = 'free';
    localStorage.setItem('fg_plan', 'free');
    showApp();
  }
}

async function loginWithGoogle() {
  if (!supabase) {
    document.getElementById('login-error').textContent = 'Supabase nicht konfiguriert. Bitte E-Mail verwenden.';
    return;
  }
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: window.location.origin + window.location.pathname }
  });
  if (error) {
    document.getElementById('login-error').textContent = error.message;
  }
}

async function loginWithApple() {
  if (!supabase) {
    document.getElementById('login-error').textContent = 'Supabase nicht konfiguriert. Bitte E-Mail verwenden.';
    return;
  }
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'apple',
    options: { redirectTo: window.location.origin + window.location.pathname }
  });
  if (error) {
    document.getElementById('login-error').textContent = error.message;
  }
}

async function logout() {
  if (supabase) {
    await supabase.auth.signOut();
  }
  localStorage.removeItem('fg_user');
  localStorage.removeItem('fg_plan');
  currentUser = null;
  userPlan = 'free';
  showLogin();
}

function skipLogin() {
  // Guest mode — limited features
  currentUser = { email: 'guest', user_metadata: { full_name: 'Gast' } };
  userPlan = 'free';
  localStorage.setItem('fg_user', JSON.stringify(currentUser));
  localStorage.setItem('fg_plan', 'free');
  showApp();
}

// ---- FREEMIUM ----
function applyFreemiumLimits() {
  // Show upgrade banner
  const banner = document.getElementById('upgrade-banner');
  if (banner) banner.style.display = 'block';
}

function isRegionLocked(region) {
  const fileName = region && String(region).endsWith('.html') ? region : window.location.pathname;
  return guideConfig.isLockedCountryFile(fileName, userPlan);
}

function isPOILocked(poi) {
  if (userPlan === guideConfig.PREMIUM_PLAN) return false;
  if (poi && poi.file) return guideConfig.isLockedCountryFile(poi.file, userPlan);
  return guideConfig.isLockedCountryFile(window.location.pathname, userPlan);
}

// ---- USER DATA SYNC ----
async function loadUserPlan() {
  if (!supabase || !currentUser) return;
  try {
    const { data } = await supabase
      .from('user_profiles')
      .select('plan, stripe_customer_id')
      .eq('user_id', currentUser.id)
      .single();
    if (data) {
      userPlan = data.plan || 'free';
    }
  } catch (e) {
    console.warn('Could not load user plan:', e);
    userPlan = localStorage.getItem('fg_plan') || 'free';
  }
}

async function syncUserData() {
  if (!supabase || !currentUser) return;

  try {
    // Load favorites from Supabase
    const { data: favs } = await supabase
      .from('user_favorites')
      .select('poi_id')
      .eq('user_id', currentUser.id);

    if (favs && favs.length) {
      window.favoritePOIs = favs.map(f => f.poi_id);
      localStorage.setItem('favPOIsFR', JSON.stringify(window.favoritePOIs));
    }

    // Load visited from Supabase
    const { data: visited } = await supabase
      .from('user_visited')
      .select('poi_id')
      .eq('user_id', currentUser.id);

    if (visited && visited.length) {
      window.visitedPOIs = visited.map(v => v.poi_id);
      localStorage.setItem('visitedPOIsFR', JSON.stringify(window.visitedPOIs));
    }
  } catch (e) {
    console.warn('Sync failed, using local data:', e);
  }
}

async function saveFavoriteToCloud(poiId, isFav) {
  if (!supabase || !currentUser) return;
  try {
    if (isFav) {
      await supabase.from('user_favorites').upsert({
        user_id: currentUser.id,
        poi_id: poiId
      });
    } else {
      await supabase.from('user_favorites')
        .delete()
        .eq('user_id', currentUser.id)
        .eq('poi_id', poiId);
    }
  } catch (e) { console.warn('Favorite sync failed:', e); }
}

async function saveVisitedToCloud(poiId, isVisited) {
  if (!supabase || !currentUser) return;
  try {
    if (isVisited) {
      await supabase.from('user_visited').upsert({
        user_id: currentUser.id,
        poi_id: poiId
      });
    } else {
      await supabase.from('user_visited')
        .delete()
        .eq('user_id', currentUser.id)
        .eq('poi_id', poiId);
    }
  } catch (e) { console.warn('Visited sync failed:', e); }
}

// ---- STRIPE CHECKOUT ----
async function openCheckout() {
  if (!supabase || !currentUser) {
    alert('Bitte zuerst einloggen');
    return;
  }

  // This would call your Supabase Edge Function that creates a Stripe Checkout Session
  // For now, show a placeholder
  const modal = document.getElementById('premium-modal');
  if (modal) modal.style.display = 'flex';
}

function closePremiumModal() {
  const modal = document.getElementById('premium-modal');
  if (modal) modal.style.display = 'none';
}

// ---- AUTH FORM TOGGLE ----
function showSignupForm() {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('signup-form').style.display = 'block';
}

function showLoginForm() {
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('signup-form').style.display = 'none';
}

// ---- PWA INSTALL PROMPT ----
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.getElementById('install-btn');
  if (btn) btn.style.display = 'flex';
});

async function installPWA() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  deferredPrompt = null;
  const btn = document.getElementById('install-btn');
  if (btn) btn.style.display = 'none';
}

// Init on load
document.addEventListener('DOMContentLoaded', initAuth);
