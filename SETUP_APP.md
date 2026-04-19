# Familienguide 2026 — App Setup Anleitung

## Was wurde gebaut

Deine Karte ist jetzt eine vollwertige **Progressive Web App (PWA)** mit:

- **Installierbar auf dem Handy** — wird wie eine native App angezeigt (Homescreen-Icon, kein Browser-Chrome)
- **Mobile-responsive** — Sidebar wird auf dem Handy zum unteren Panel, Karte oben
- **Login-System** — E-Mail + Passwort oder Google Login via Supabase
- **Freemium-Modell** — Free-User sehen 3 Regionen (Paris, Normandie, Bretagne), Premium alle 14
- **Cloud-Sync** — Favoriten und besuchte Orte werden in Supabase gespeichert (geräteübergreifend)
- **Offline-fähig** — Service Worker cached Karte, Tiles und Assets
- **Premium-Upgrade Modal** — Vorbereitet für Stripe Checkout

## Neue Dateien

| Datei | Zweck |
|-------|-------|
| `manifest.json` | PWA-Manifest (App-Name, Icons, Startseite) |
| `sw.js` | Service Worker (Offline-Cache, Asset-Caching) |
| `auth.js` | Login, Supabase-Integration, Freemium-Logik |
| `SETUP_APP.md` | Diese Anleitung |

## Schritt 1: Supabase Projekt erstellen

1. Gehe zu **https://supabase.com** → "Start your project"
2. Erstelle ein neues Projekt (z.B. "familienguide")
3. Notiere dir:
   - **Project URL**: `https://abc123.supabase.co`
   - **anon/public Key**: `eyJhbGc...` (unter Settings → API)

## Schritt 2: Datenbank-Tabellen anlegen

Gehe in den Supabase **SQL Editor** und führe aus:

```sql
-- User Profiles mit Abo-Plan
CREATE TABLE user_profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'premium')),
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id)
);

-- Favoriten
CREATE TABLE user_favorites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  poi_id INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, poi_id)
);

-- Besuchte Orte
CREATE TABLE user_visited (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  poi_id INTEGER NOT NULL,
  visited_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, poi_id)
);

-- Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_visited ENABLE ROW LEVEL SECURITY;

-- Policies: User kann nur eigene Daten sehen/ändern
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage own favorites" ON user_favorites FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own visited" ON user_visited FOR ALL USING (auth.uid() = user_id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (user_id, plan) VALUES (new.id, 'free');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

## Schritt 3: Google Login aktivieren (optional)

1. In Supabase → Authentication → Providers → Google aktivieren
2. Du brauchst eine Google Cloud Console OAuth Client ID
3. Redirect URL: `https://abc123.supabase.co/auth/v1/callback`

## Schritt 4: Supabase-Keys in die App eintragen

Öffne `auth.js` und ersetze die Platzhalter:

```js
const SUPABASE_URL = 'https://DEIN-PROJEKT.supabase.co';
const SUPABASE_ANON_KEY = 'DEIN-ANON-KEY';
```

**Oder**: User können die Keys im Browser setzen via Console:
```js
localStorage.setItem('fg_supabase_url', 'https://abc123.supabase.co');
localStorage.setItem('fg_supabase_key', 'eyJ...');
```

## Schritt 5: Stripe Abo einrichten (für Premium)

1. Erstelle einen **Stripe Account** auf https://stripe.com
2. Erstelle ein Produkt "Familienguide Premium" mit 2 Preisen:
   - Monatlich: 4,99€
   - Jährlich: 39,99€
3. Erstelle eine **Supabase Edge Function** für den Checkout:

```ts
// supabase/functions/create-checkout/index.ts
import Stripe from 'https://esm.sh/stripe@14'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!)

Deno.serve(async (req) => {
  const { priceId, userId } = await req.json()
  
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${req.headers.get('origin')}/map_frankreich.html?payment=success`,
    cancel_url: `${req.headers.get('origin')}/map_frankreich.html`,
    metadata: { userId }
  })

  return new Response(JSON.stringify({ url: session.url }))
})
```

4. Webhook einrichten der bei Zahlung `user_profiles.plan = 'premium'` setzt

## Schritt 6: Deploy auf Vercel

```bash
cd Jahresguide
git add manifest.json sw.js auth.js SETUP_APP.md
git add map_frankreich.html
git commit -m "Add PWA + Auth + Freemium"
git push
```

Die App ist dann live unter deiner Vercel-URL und installierbar!

## Schritt 7: App auf dem Handy installieren

1. Öffne die Vercel-URL im Handy-Browser (Chrome/Safari)
2. Chrome: Menü → "Zum Startbildschirm hinzufügen"
3. Safari: Teilen-Button → "Zum Home-Bildschirm"
4. Die App öffnet sich dann vollständig ohne Browser-Leiste

## Wie das Freemium funktioniert

| Feature | Free | Premium |
|---------|------|---------|
| Karte ansehen | ✓ | ✓ |
| 3 Regionen (Paris, Normandie, Bretagne) | ✓ | ✓ |
| Alle 14 Regionen | ✗ | ✓ |
| Favoriten | ✓ (lokal) | ✓ (Cloud-Sync) |
| Offline-Modus | Begrenzt | Voll |
| Routenplaner | ✗ | ✓ |
| Alle Länder-Guides | ✗ | ✓ |

## Demo-Modus

Ohne Supabase-Konfiguration funktioniert die App im **Demo-Modus**:
- Login mit beliebiger E-Mail/Passwort (wird lokal gespeichert)
- Alle Features nutzbar zum Testen
- "Ohne Login weitermachen" für Gast-Zugang
