// ============================================
// Familienguide 2026 — Auth Guard für Map-Seiten
// Leichtgewichtiger Check: Login erfolgt zentral in app.html
// ============================================

(function() {
  'use strict';

  const fallbackFreeCountryFiles = [
    'index.html',
    'map_deutschland.html',
    'map_frankreich.html',
    'map_oesterreich.html'
  ];

  function normalizeFileName(value) {
    if (!value) {
      return '';
    }

    return String(value).split(/[?#]/)[0].split('/').pop();
  }

  const guideConfig = window.GuideConfig || {
    PREMIUM_PLAN: 'premium',
    FREE_COUNTRY_FILES: fallbackFreeCountryFiles,
    normalizeFileName: normalizeFileName,
    isLockedCountryFile(fileName, userPlan) {
      if (userPlan === 'premium') {
        return false;
      }

      const normalized = normalizeFileName(fileName);
      return !!normalized && fallbackFreeCountryFiles.indexOf(normalized) === -1;
    },
    getUpgradeUrl(fileName) {
      const params = new URLSearchParams();
      params.set('upgrade', '1');

      const normalized = normalizeFileName(fileName);
      if (normalized) {
        params.set('from', normalized);
      }

      return 'app.html?' + params.toString();
    }
  };

  const currentCountryFile = guideConfig.normalizeFileName(window.location.pathname);

  // --- Auth Check: Redirect to app.html if not logged in ---
  const userRaw = localStorage.getItem('fg_user');
  if (!userRaw) {
    window.location.replace('app.html');
    return;
  }

  let currentUser;
  try {
    currentUser = JSON.parse(userRaw);
  } catch(e) {
    window.location.replace('app.html');
    return;
  }

  const userPlan = localStorage.getItem('fg_plan') || 'free';

  if (guideConfig.isLockedCountryFile(currentCountryFile, userPlan)) {
    window.location.replace(guideConfig.getUpgradeUrl(currentCountryFile));
    return;
  }

  // --- Update UI elements ---
  document.addEventListener('DOMContentLoaded', function() {
    // Plan badge
    const badge = document.getElementById('plan-badge');
    if (badge) {
      if (userPlan === 'premium') {
        badge.textContent = '\u2B50 Premium';
        badge.className = 'plan-badge premium';
      } else {
        badge.textContent = 'Free';
        badge.className = 'plan-badge free';
      }
    }

    // User initial button
    const userBtn = document.getElementById('user-menu-btn');
    if (userBtn && currentUser) {
      const name = (currentUser.user_metadata && currentUser.user_metadata.full_name)
                   || (currentUser.email && currentUser.email.split('@')[0])
                   || 'User';
      userBtn.textContent = name.charAt(0).toUpperCase();
      userBtn.title = name;
    }

    // Show upgrade banner for free users
    if (userPlan === 'free') {
      const banner = document.getElementById('upgrade-banner');
      if (banner) banner.style.display = 'block';
    }
  });

  // --- Global functions for UI buttons ---

  window.logout = function() {
    localStorage.removeItem('fg_user');
    localStorage.removeItem('fg_plan');
    window.location.replace('app.html');
  };

  window.openCheckout = function() {
    window.location.href = guideConfig.getUpgradeUrl(currentCountryFile);
  };

  // PWA Install
  let deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', function(e) {
    e.preventDefault();
    deferredPrompt = e;
    const btn = document.getElementById('install-btn');
    if (btn) btn.style.display = 'flex';
    const menuItem = document.getElementById('install-menu-item') || document.getElementById('install-menu');
    if (menuItem) menuItem.style.display = 'flex';
  });

  window.installPWA = async function() {
    if (!deferredPrompt) {
      // Fallback: show instructions
      alert('Tippe im Browser-Menü auf "Zum Startbildschirm hinzufügen" um die App zu installieren.');
      return;
    }
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    const btn = document.getElementById('install-btn');
    if (btn) btn.style.display = 'none';
  };

  // Expose for other scripts
  window.currentUser = currentUser;
  window.userPlan = userPlan;
  window.currentCountryFile = currentCountryFile;
  window.isCountryLocked = function(fileName) {
    return guideConfig.isLockedCountryFile(fileName || currentCountryFile, userPlan);
  };
  window.isRegionLocked = window.isCountryLocked;

})();
