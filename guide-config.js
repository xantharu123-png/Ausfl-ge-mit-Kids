(function initGuideConfig(global) {
  'use strict';

  if (!global) {
    return;
  }

  const COUNTRY_LABELS_BY_FILE = Object.freeze({
    'index.html': 'Schweiz',
    'map_deutschland.html': 'Deutschland',
    'map_frankreich.html': 'Frankreich',
    'map_oesterreich.html': 'Oesterreich',
    'map_italien.html': 'Italien',
    'map_spanien.html': 'Spanien',
    'map_portugal.html': 'Portugal',
    'map_niederlande.html': 'Niederlande',
    'map_belgien.html': 'Belgien',
    'map_luxemburg.html': 'Luxemburg',
    'map_norwegen.html': 'Norwegen',
    'map_schweden.html': 'Schweden',
    'map_finnland.html': 'Finnland',
    'map_island.html': 'Island',
    'map_faeroeer.html': 'Faeroeer',
    'map_polen.html': 'Polen',
    'map_tschechien.html': 'Tschechien',
    'map_slowakei.html': 'Slowakei',
    'map_slowenien.html': 'Slowenien',
    'map_kroatien.html': 'Kroatien',
    'map_bosnien.html': 'Bosnien',
    'map_griechenland.html': 'Griechenland',
    'map_zypern.html': 'Zypern',
    'map_vae.html': 'VAE',
    'map_katar.html': 'Katar',
    'map_japan.html': 'Japan',
    'map_kanada_west.html': 'Kanada West',
    'map_kanada_zentral.html': 'Kanada Zentral',
    'map_kanada_ontario.html': 'Kanada Ontario',
    'map_kanada_ost.html': 'Kanada Ost'
  });

  const FREE_COUNTRY_FILES = Object.freeze([
    'index.html',
    'map_deutschland.html',
    'map_frankreich.html',
    'map_oesterreich.html'
  ]);

  function normalizeFileName(value) {
    if (!value) {
      return '';
    }

    return String(value).split(/[?#]/)[0].split('/').pop();
  }

  function getCountryLabel(fileName) {
    const normalized = normalizeFileName(fileName);
    return COUNTRY_LABELS_BY_FILE[normalized] || '';
  }

  function isLockedCountryFile(fileName, userPlan) {
    const normalized = normalizeFileName(fileName);
    if (!normalized) {
      return false;
    }

    if (userPlan === 'premium') {
      return false;
    }

    return FREE_COUNTRY_FILES.indexOf(normalized) === -1;
  }

  function getUpgradeUrl(fileName) {
    const params = new URLSearchParams();
    params.set('upgrade', '1');

    const normalized = normalizeFileName(fileName);
    if (normalized) {
      params.set('from', normalized);
    }

    return 'app.html?' + params.toString();
  }

  global.GuideConfig = Object.freeze({
    PREMIUM_PLAN: 'premium',
    COUNTRY_COUNT: Object.keys(COUNTRY_LABELS_BY_FILE).length,
    COUNTRY_LABELS_BY_FILE: COUNTRY_LABELS_BY_FILE,
    FREE_COUNTRY_FILES: FREE_COUNTRY_FILES,
    normalizeFileName: normalizeFileName,
    getCountryLabel: getCountryLabel,
    isLockedCountryFile: isLockedCountryFile,
    getUpgradeUrl: getUpgradeUrl
  });
})(window);
