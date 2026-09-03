/**
 * Spin & Win SaaS Platform — Complete Themed Spinner Design System 2.0
 * Multi-Layered 3D HTML5 Canvas Wheel Engine with Theme-Specific Geometries,
 * 14 Procedural Center Hubs, 11 Dedicated Pointers, Outer Bezels, & Web Audio Synthesis
 */

const THEME_SPINNER_REGISTRY = {
  // ── 1. ROYAL & JEWELLERY ──
  royal: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.1 },
    palette: ['#6d28d9', '#4c1d95', '#d4af37', '#8b5cf6', '#10b981', '#f59e0b'],
    ringStyle: 'gold_filigree',
    hubType: 'crown',
    pointerType: 'crown',
    fontFamily: 'cinzel',
    studCount: 16,
    audioProfile: 'royal_chime'
  },
  royal_jewellery: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 7, hubRadius: 36, pointerScale: 1.15 },
    palette: ['#1e1b4b', '#d4af37', '#312e81', '#f59e0b', '#065f46', '#ffd700'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'diamond',
    fontFamily: 'cinzel',
    studCount: 16,
    audioProfile: 'royal_chime'
  },
  luxury_black: {
    geometry: { outerRingWidth: 15, innerBezelWidth: 5, hubRadius: 32, pointerScale: 1.0 },
    palette: ['#18181b', '#27272a', '#d4af37', '#3f3f46', '#e4e4e7', '#b8860b'],
    ringStyle: 'champagne_minimal',
    hubType: 'crown',
    pointerType: 'minimal_needle',
    fontFamily: 'cinzel',
    studCount: 12,
    audioProfile: 'royal_chime'
  },
  minimal_luxury: {
    geometry: { outerRingWidth: 12, innerBezelWidth: 4, hubRadius: 30, pointerScale: 0.95 },
    palette: ['#1e293b', '#6366f1', '#334155', '#f59e0b', '#475569', '#4f46e5'],
    ringStyle: 'champagne_minimal',
    hubType: 'minimal_disc',
    pointerType: 'minimal_needle',
    fontFamily: 'playfair',
    studCount: 8,
    audioProfile: 'royal_chime'
  },
  pearl: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.05 },
    palette: ['#0f172a', '#d4af37', '#334155', '#94a3b8', '#64748b', '#b8860b'],
    ringStyle: 'gold_filigree',
    hubType: 'pearl_sphere',
    pointerType: 'diamond',
    fontFamily: 'playfair',
    studCount: 14,
    audioProfile: 'royal_chime'
  },
  fashion: {
    geometry: { outerRingWidth: 15, innerBezelWidth: 5, hubRadius: 32, pointerScale: 1.0 },
    palette: ['#09090b', '#27272a', '#d4af37', '#3f3f46', '#e4e4e7', '#18181b'],
    ringStyle: 'champagne_minimal',
    hubType: 'diamond_crown',
    pointerType: 'minimal_needle',
    fontFamily: 'cinzel',
    studCount: 12,
    audioProfile: 'royal_chime'
  },
  beauty: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.05 },
    palette: ['#831843', '#f472b6', '#db2777', '#fbbf24', '#500724', '#f43f5e'],
    ringStyle: 'gold_filigree',
    hubType: 'pearl_sphere',
    pointerType: 'heart_arrow',
    fontFamily: 'playfair',
    studCount: 14,
    audioProfile: 'royal_chime'
  },

  // ── 2. FESTIVAL THEMES ──
  diwali: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 7, hubRadius: 36, pointerScale: 1.15 },
    palette: ['#581c87', '#d4af37', '#ea580c', '#f59e0b', '#7e22ce', '#b45309'],
    ringStyle: 'gold_filigree',
    hubType: 'diya',
    pointerType: 'flame',
    fontFamily: 'cinzel',
    studCount: 16,
    audioProfile: 'festive_bell'
  },
  uttarayan: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#0284c7', '#f97316', '#10b981', '#ffd700', '#ec4899', '#3b82f6'],
    ringStyle: 'gold_filigree',
    hubType: 'kite',
    pointerType: 'kite',
    fontFamily: 'poppins',
    studCount: 12,
    audioProfile: 'festive_bell'
  },
  makar_sankranti: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#0284c7', '#ea580c', '#facc15', '#075985', '#10b981', '#f97316'],
    ringStyle: 'gold_filigree',
    hubType: 'kite',
    pointerType: 'kite',
    fontFamily: 'poppins',
    studCount: 12,
    audioProfile: 'festive_bell'
  },
  janmashtami: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 7, hubRadius: 38, pointerScale: 1.2 },
    palette: ['#0d1b4a', '#3b185f', '#00a896', '#ffd700', '#047857', '#00b4d8'],
    ringStyle: 'peacock_teal',
    hubType: 'peacock_flute',
    pointerType: 'feather',
    fontFamily: 'cinzel',
    studCount: 16,
    audioProfile: 'bansuri_flute'
  },
  janmashtami_jewellery: {
    geometry: { outerRingWidth: 19, innerBezelWidth: 7, hubRadius: 38, pointerScale: 1.2 },
    palette: ['#1e1b4b', '#d4af37', '#064e3b', '#ffd700', '#3b185f', '#f59e0b'],
    ringStyle: 'gold_filigree',
    hubType: 'peacock_flute',
    pointerType: 'feather',
    fontFamily: 'cinzel',
    studCount: 16,
    audioProfile: 'bansuri_flute'
  },
  janmashtami_sweets: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.15 },
    palette: ['#4c1d95', '#f59e0b', '#00a896', '#fef08a', '#1e1b4b', '#d97706'],
    ringStyle: 'peacock_teal',
    hubType: 'peacock_flute',
    pointerType: 'feather',
    fontFamily: 'poppins',
    studCount: 14,
    audioProfile: 'bansuri_flute'
  },
  janmashtami_clothing: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 7, hubRadius: 37, pointerScale: 1.2 },
    palette: ['#581c87', '#00c49f', '#ffd700', '#0e1436', '#db2777', '#0284c7'],
    ringStyle: 'peacock_teal',
    hubType: 'peacock_flute',
    pointerType: 'feather',
    fontFamily: 'playfair',
    studCount: 16,
    audioProfile: 'bansuri_flute'
  },
  janmashtami_kids: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.15 },
    palette: ['#00f2fe', '#8b5cf6', '#fbbf24', '#ec4899', '#10b981', '#3b82f6'],
    ringStyle: 'peacock_teal',
    hubType: 'peacock_flute',
    pointerType: 'feather',
    fontFamily: 'poppins',
    studCount: 14,
    audioProfile: 'bansuri_flute'
  },
  christmas: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 7, hubRadius: 36, pointerScale: 1.15 },
    palette: ['#991b1b', '#166534', '#ffd700', '#b91c1c', '#15803d', '#ffffff'],
    ringStyle: 'festive_ornament',
    hubType: 'snowflake',
    pointerType: 'snowflake',
    fontFamily: 'playfair',
    studCount: 16,
    audioProfile: 'festive_bell'
  },
  holi: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#f43f5e', '#06b6d4', '#eab308', '#ec4899', '#10b981', '#8b5cf6'],
    ringStyle: 'gold_filigree',
    hubType: 'holi_splash',
    pointerType: 'splash',
    fontFamily: 'poppins',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  navratri: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.15 },
    palette: ['#db2777', '#ea580c', '#7c3aed', '#eab308', '#c026d3', '#f97316'],
    ringStyle: 'gold_filigree',
    hubType: 'diya',
    pointerType: 'flame',
    fontFamily: 'poppins',
    studCount: 16,
    audioProfile: 'festive_bell'
  },
  new_year: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.1 },
    palette: ['#09090b', '#d4af37', '#1e3a8a', '#27272a', '#b8860b', '#38bdf8'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'diamond',
    fontFamily: 'cinzel',
    studCount: 16,
    audioProfile: 'royal_chime'
  },
  eid: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#065f46', '#10b981', '#d4af37', '#047857', '#fef08a', '#022c22'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'diamond',
    fontFamily: 'cinzel',
    studCount: 14,
    audioProfile: 'royal_chime'
  },
  eid_ul_fitr: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#065f46', '#10b981', '#d4af37', '#047857', '#fbbf24', '#01261d'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'diamond',
    fontFamily: 'cinzel',
    studCount: 14,
    audioProfile: 'royal_chime'
  },
  valentines: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#be123c', '#e11d48', '#fda4af', '#831843', '#f43f5e', '#fb7185'],
    ringStyle: 'gold_filigree',
    hubType: 'heart_gem',
    pointerType: 'heart_arrow',
    fontFamily: 'playfair',
    studCount: 14,
    audioProfile: 'royal_chime'
  },
  womens_day: {
    geometry: { outerRingWidth: 15, innerBezelWidth: 5, hubRadius: 33, pointerScale: 1.05 },
    palette: ['#7e22ce', '#c084fc', '#f472b6', '#86198f', '#a855f7', '#fda4af'],
    ringStyle: 'champagne_minimal',
    hubType: 'pearl_sphere',
    pointerType: 'heart_arrow',
    fontFamily: 'playfair',
    studCount: 12,
    audioProfile: 'royal_chime'
  },
  durga_puja: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 7, hubRadius: 36, pointerScale: 1.15 },
    palette: ['#991b1b', '#dc2626', '#facc15', '#7f1d1d', '#b45309', '#ffd700'],
    ringStyle: 'gold_filigree',
    hubType: 'diya',
    pointerType: 'flame',
    fontFamily: 'cinzel',
    studCount: 16,
    audioProfile: 'festive_bell'
  },
  onam: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#eab308', '#15803d', '#f97316', '#0f2918', '#84cc16', '#ffd700'],
    ringStyle: 'gold_filigree',
    hubType: 'diya',
    pointerType: 'flame',
    fontFamily: 'poppins',
    studCount: 14,
    audioProfile: 'festive_bell'
  },
  halloween: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.1 },
    palette: ['#ea580c', '#581c87', '#fbbf24', '#0c0a09', '#c2410c', '#7e22ce'],
    ringStyle: 'gold_filigree',
    hubType: 'diya',
    pointerType: 'flame',
    fontFamily: 'space_grotesk',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  earth_eco: {
    geometry: { outerRingWidth: 15, innerBezelWidth: 5, hubRadius: 32, pointerScale: 1.0 },
    palette: ['#15803d', '#22c55e', '#86efac', '#052e16', '#166534', '#4ade80'],
    ringStyle: 'gold_filigree',
    hubType: 'pearl_sphere',
    pointerType: 'diamond',
    fontFamily: 'outfit',
    studCount: 10,
    audioProfile: 'royal_chime'
  },

  // ── 3. MODERN, CYBER & ATMOSPHERIC ──
  neon: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.2 },
    palette: ['#7c3aed', '#db2777', '#0891b2', '#059669', '#d97706', '#9333ea'],
    ringStyle: 'neon_tube',
    hubType: 'cyber_node',
    pointerType: 'cyber_laser',
    fontFamily: 'space_grotesk',
    studCount: 0,
    audioProfile: 'cyber_synth'
  },
  electronics: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#0284c7', '#1e3a8a', '#38bdf8', '#0369a1', '#7c3aed', '#0f172a'],
    ringStyle: 'neon_tube',
    hubType: 'cyber_node',
    pointerType: 'cyber_laser',
    fontFamily: 'space_grotesk',
    studCount: 0,
    audioProfile: 'cyber_synth'
  },
  aurora: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#7c3aed', '#0284c7', '#059669', '#db2777', '#0891b2', '#8b5cf6'],
    ringStyle: 'aurora_luminous',
    hubType: 'prismatic_gem',
    pointerType: 'diamond',
    fontFamily: 'outfit',
    studCount: 12,
    audioProfile: 'royal_chime'
  },
  glass: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.05 },
    palette: ['#4338ca', '#7c3aed', '#db2777', '#0284c7', '#059669', '#ffd700'],
    ringStyle: 'frosted_glass',
    hubType: 'prismatic_gem',
    pointerType: 'minimal_needle',
    fontFamily: 'outfit',
    studCount: 12,
    audioProfile: 'royal_chime'
  },

  // ── 4. BUSINESS & CATEGORY THEMES ──
  coffee: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.18 },
    palette: ['#2b1207', '#d97706', '#1a0b04', '#b45309', '#f59e0b', '#78350f'],
    ringStyle: 'roasted_brass',
    hubType: 'coffee_cup',
    pointerType: 'copper_bean',
    fontFamily: 'playfair',
    studCount: 14,
    audioProfile: 'coffee_perk'
  },
  restaurant: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.1 },
    palette: ['#78350f', '#d97706', '#b45309', '#f59e0b', '#92400e', '#7c2d12'],
    ringStyle: 'roasted_brass',
    hubType: 'cloche_dome',
    pointerType: 'flame',
    fontFamily: 'playfair',
    studCount: 14,
    audioProfile: 'royal_chime'
  },
  sports: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#b91c1c', '#09090b', '#1d4ed8', '#15803d', '#dc2626', '#1e293b'],
    ringStyle: 'carbon_sport',
    hubType: 'speed_star',
    pointerType: 'cyber_laser',
    fontFamily: 'space_grotesk',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  automotive: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#020617', '#334155', '#dc2626', '#0284c7', '#64748b', '#0f172a'],
    ringStyle: 'carbon_sport',
    hubType: 'speed_star',
    pointerType: 'minimal_needle',
    fontFamily: 'space_grotesk',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  real_estate: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 5, hubRadius: 33, pointerScale: 1.05 },
    palette: ['#0284c7', '#0f172a', '#d4af37', '#0369a1', '#334155', '#1e293b'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'diamond',
    fontFamily: 'outfit',
    studCount: 12,
    audioProfile: 'royal_chime'
  },
  kids: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.2 },
    palette: ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'],
    ringStyle: 'candy_round',
    hubType: 'candy_swirl',
    pointerType: 'star_lollipop',
    fontFamily: 'poppins',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  playful: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'],
    ringStyle: 'candy_round',
    hubType: 'candy_swirl',
    pointerType: 'star_lollipop',
    fontFamily: 'poppins',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  candy: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#ec4899', '#a855f7', '#06b6d4', '#10b981', '#f472b6', '#38bdf8'],
    ringStyle: 'candy_round',
    hubType: 'candy_swirl',
    pointerType: 'star_lollipop',
    fontFamily: 'poppins',
    studCount: 12,
    audioProfile: 'energy_pop'
  },

  // ── 5. PROMOTIONAL & SEASONAL THEMES ──
  flash_sale: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.2 },
    palette: ['#b91c1c', '#ea580c', '#eab308', '#dc2626', '#d97706', '#18181b'],
    ringStyle: 'carbon_sport',
    hubType: 'speed_star',
    pointerType: 'cyber_laser',
    fontFamily: 'space_grotesk',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  mega_sale: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.2 },
    palette: ['#dc2626', '#991b1b', '#facc15', '#b91c1c', '#ea580c', '#09090b'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'flame',
    fontFamily: 'space_grotesk',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  clearance: {
    geometry: { outerRingWidth: 18, innerBezelWidth: 6, hubRadius: 36, pointerScale: 1.2 },
    palette: ['#dc2626', '#facc15', '#991b1b', '#1f2937', '#b91c1c', '#111827'],
    ringStyle: 'carbon_sport',
    hubType: 'speed_star',
    pointerType: 'flame',
    fontFamily: 'space_grotesk',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  grand_opening: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#7c3aed', '#db2777', '#f59e0b', '#059669', '#4f46e5', '#ffd700'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'crown',
    fontFamily: 'outfit',
    studCount: 16,
    audioProfile: 'royal_chime'
  },
  weekend_flash: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#f43f5e', '#6366f1', '#fbbf24', '#0f172a', '#e11d48', '#8b5cf6'],
    ringStyle: 'neon_tube',
    hubType: 'speed_star',
    pointerType: 'cyber_laser',
    fontFamily: 'space_grotesk',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  summer_sale: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.1 },
    palette: ['#f59e0b', '#0284c7', '#10b981', '#d97706', '#0ea5e9', '#059669'],
    ringStyle: 'gold_filigree',
    hubType: 'diamond_crown',
    pointerType: 'star_lollipop',
    fontFamily: 'outfit',
    studCount: 12,
    audioProfile: 'energy_pop'
  },
  winter_sale: {
    geometry: { outerRingWidth: 17, innerBezelWidth: 6, hubRadius: 35, pointerScale: 1.15 },
    palette: ['#0284c7', '#38bdf8', '#1e3a8a', '#e2e8f0', '#0ea5e9', '#60a5fa'],
    ringStyle: 'festive_ornament',
    hubType: 'snowflake',
    pointerType: 'snowflake',
    fontFamily: 'outfit',
    studCount: 14,
    audioProfile: 'festive_bell'
  },
  monsoon_sale: {
    geometry: { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.1 },
    palette: ['#0ea5e9', '#0369a1', '#38bdf8', '#082f49', '#0284c7', '#7dd3fc'],
    ringStyle: 'frosted_glass',
    hubType: 'prismatic_gem',
    pointerType: 'minimal_needle',
    fontFamily: 'inter',
    studCount: 12,
    audioProfile: 'royal_chime'
  }
};

class SpinWheel {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.options = options;
    this.theme = options.theme || null;
    this.prizes = options.prizes || [];
    this.spinButton = options.spinButtonId ? document.getElementById(options.spinButtonId) : null;
    this.soundToggle = options.soundToggleId ? document.getElementById(options.soundToggleId) : null;
    this.onSpinClick = options.onSpinClick || null;

    this.currentAngle = 0;
    this.isSpinning = false;
    this.soundMuted = false;
    this.audioCtx = null;
    this.lastTickSegment = -1;
    this.winningSegment = null;
    this.highlightTimer = 0;

    window.activeSpinWheelInstance = this;

    this.init();
  }

  init() {
    this.setupHighDPI();
    this.draw();

    if (this.spinButton) {
      this.spinButton.addEventListener('click', () => {
        if (!this.isSpinning) {
          this.initAudio();
          if (this.onSpinClick) {
            this.onSpinClick();
          }
        }
      });
    }

    if (this.soundToggle) {
      this.soundToggle.addEventListener('click', () => {
        this.soundMuted = !this.soundMuted;
        this.soundToggle.innerHTML = this.soundMuted ? '🔇' : '🔊';
        this.soundToggle.setAttribute('aria-label', this.soundMuted ? 'Unmute Sound' : 'Mute Sound');
      });
    }

    window.addEventListener('resize', () => {
      this.setupHighDPI();
      this.draw();
    });
  }

  setupHighDPI() {
    if (!this.canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();
    const displayWidth = (rect && rect.width > 50) ? rect.width : (parseInt(this.canvas.getAttribute('width')) || 330);
    const displayHeight = (rect && rect.height > 50) ? rect.height : (parseInt(this.canvas.getAttribute('height')) || 330);

    this.canvas.width = Math.round(displayWidth * dpr);
    this.canvas.height = Math.round(displayHeight * dpr);
    this.canvas.style.width = displayWidth + 'px';
    this.canvas.style.height = displayHeight + 'px';
    this.ctx.resetTransform();
    this.ctx.scale(dpr, dpr);

    this.displayWidth = displayWidth;
    this.displayHeight = displayHeight;
  }

  getThemeConfig() {
    let activeTheme = this.theme || (this.options && this.options.theme) || (this.canvas && this.canvas.closest && this.canvas.closest('[data-theme]') ? this.canvas.closest('[data-theme]').getAttribute('data-theme') : null) || document.body.getAttribute('data-theme') || 'royal';
    return THEME_SPINNER_REGISTRY[activeTheme] || THEME_SPINNER_REGISTRY.royal;
  }

  initAudio() {
    if (!this.audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  playTickSound() {
    if (!this.audioCtx || this.soundMuted) return;
    if (this.audioCtx.state === 'suspended') this.audioCtx.resume();

    const config = this.getThemeConfig();
    const profile = config.audioProfile || 'classic_tick';
    const now = this.audioCtx.currentTime;

    if (profile === 'bansuri_flute') {
      const osc1 = this.audioCtx.createOscillator();
      const osc2 = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(587.33, now);
      osc1.frequency.exponentialRampToValueAtTime(880.00, now + 0.05);
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(1174.66, now);
      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.005, now + 0.05);
      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc1.start();
      osc2.start();
      osc1.stop(now + 0.05);
      osc2.stop(now + 0.05);
    } else if (profile === 'cyber_synth') {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(750, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.04);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.04);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(now + 0.04);
    } else if (profile === 'festive_bell' || profile === 'royal_chime') {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.06);
      gain.gain.setValueAtTime(0.16, now);
      gain.gain.exponentialRampToValueAtTime(0.005, now + 0.06);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(now + 0.06);
    } else {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(480, now);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.04);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.04);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(now + 0.04);
    }
  }

  playWinSound() {
    if (!this.audioCtx || this.soundMuted) return;
    if (this.audioCtx.state === 'suspended') this.audioCtx.resume();

    const config = this.getThemeConfig();
    const profile = config.audioProfile || 'classic_tick';
    const now = this.audioCtx.currentTime;

    if (profile === 'bansuri_flute') {
      const fluteNotes = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.50];
      fluteNotes.forEach((freq, idx) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.18, now + idx * 0.09);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.09 + 0.45);
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(now + idx * 0.09);
        osc.stop(now + idx * 0.09 + 0.45);
      });
    } else if (profile === 'cyber_synth') {
      const notes = [440, 554.37, 659.25, 880, 1108.73];
      notes.forEach((freq, idx) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.12, now + idx * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.3);
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(now + idx * 0.08);
        osc.stop(now + idx * 0.08 + 0.3);
      });
    } else {
      const notes = [523.25, 659.25, 783.99, 1046.50];
      notes.forEach((freq, idx) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.16, now + idx * 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.1 + 0.38);
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(now + idx * 0.1);
        osc.stop(now + idx * 0.1 + 0.38);
      });
    }
  }

  draw() {
    let prizesToDraw = this.prizes;
    if (!prizesToDraw || prizesToDraw.length === 0) {
      prizesToDraw = [
        { name: '10% OFF', display_color: '#6366f1' },
        { name: '20% OFF', display_color: '#4f46e5' },
        { name: 'Special Reward', display_color: '#d4af37' },
        { name: 'Try Again', display_color: '#475569' }
      ];
    }

    const numSlices = prizesToDraw.length;
    const width = this.displayWidth || 330;
    const height = this.displayHeight || 330;
    const centerX = width / 2;
    const centerY = height / 2;
    const config = this.getThemeConfig();
    const geom = config.geometry || { outerRingWidth: 16, innerBezelWidth: 6, hubRadius: 34, pointerScale: 1.1 };
    const radius = Math.min(centerX, centerY) - (geom.outerRingWidth + 4);
    const sliceAngle = (2 * Math.PI) / numSlices;
    const palette = config.palette;

    this.ctx.clearRect(0, 0, width, height);

    // ── 1. LAYER 1: AMBIENT BACK GLOW & 3D DROP SHADOW ──
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY + 5, radius + geom.outerRingWidth + 2, 0, 2 * Math.PI);
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.55)';
    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.7)';
    this.ctx.shadowBlur = 20;
    this.ctx.fill();
    this.ctx.restore();

    // ── 2. LAYER 2: THEMED 3D OUTER BEZEL & METALLIC RIM ──
    this.drawOuterBezel(centerX, centerY, radius, geom, config);

    // ── 3. LAYER 3: DIMENSIONAL SEGMENTS & MULTI-STOP RADIAL SHADING ──
    for (let i = 0; i < numSlices; i++) {
      const prize = prizesToDraw[i];
      const startAngle = this.currentAngle + i * sliceAngle;
      const endAngle = startAngle + sliceAngle;
      const baseColor = palette[i % palette.length];

      this.ctx.save();
      this.ctx.beginPath();
      this.ctx.moveTo(centerX, centerY);
      this.ctx.arc(centerX, centerY, radius, startAngle, endAngle);
      this.ctx.closePath();

      // Multi-stop 3D radial depth gradient for segment
      const segGrad = this.ctx.createRadialGradient(centerX, centerY, geom.hubRadius * 0.5, centerX, centerY, radius);
      segGrad.addColorStop(0, this.adjustHexBrightness(baseColor, 25));
      segGrad.addColorStop(0.7, baseColor);
      segGrad.addColorStop(1, this.adjustHexBrightness(baseColor, -35));
      this.ctx.fillStyle = segGrad;
      this.ctx.fill();

      // Winning slice pulse highlight
      if (this.winningSegment === i) {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
        this.ctx.fill();
      }

      // 3D Specular outer arc bevel
      this.ctx.beginPath();
      this.ctx.arc(centerX, centerY, radius - 2, startAngle, endAngle);
      this.ctx.lineWidth = 2.5;
      this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.28)';
      this.ctx.stroke();

      // Segment Separator Line
      this.ctx.beginPath();
      this.ctx.moveTo(centerX, centerY);
      this.ctx.lineTo(centerX + Math.cos(startAngle) * radius, centerY + Math.sin(startAngle) * radius);
      this.ctx.lineWidth = config.ringStyle === 'neon_tube' ? 2.2 : 1.8;
      this.ctx.strokeStyle = config.ringStyle === 'neon_tube' ? 'rgba(0, 229, 255, 0.85)' : (config.ringStyle === 'champagne_minimal' ? 'rgba(243, 229, 171, 0.5)' : 'rgba(255, 215, 0, 0.75)');
      this.ctx.stroke();

      // ── 4. LAYER 4: INTELLIGENT AUTO-SCALED TYPOGRAPHY ──
      this.drawSegmentText(centerX, centerY, radius, geom.hubRadius, startAngle, sliceAngle, prize.name, config);
      this.ctx.restore();
    }

    // ── 5. LAYER 5: INNER BEZEL 3D INSET SHADOW ──
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    this.ctx.lineWidth = geom.innerBezelWidth;
    this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
    this.ctx.stroke();
    this.ctx.restore();

    // ── 6. LAYER 6: THEME 3D CENTER HUB ──
    this.drawThemeHub(centerX, centerY, geom.hubRadius, config);

    // ── 7. LAYER 7: THEME SPECIFIC POINTER ──
    this.drawThemePointer(centerX, centerY - radius - 2, geom.pointerScale || 1.1, config);
  }

  drawOuterBezel(centerX, centerY, radius, geom, config) {
    const bezelR = radius + geom.outerRingWidth;
    const ringStyle = config.ringStyle || 'gold_filigree';

    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, bezelR, 0, 2 * Math.PI);

    let rimGrad = this.ctx.createLinearGradient(centerX - bezelR, centerY - bezelR, centerX + bezelR, centerY + bezelR);

    if (ringStyle === 'neon_tube') {
      rimGrad.addColorStop(0, '#00e5ff');
      rimGrad.addColorStop(0.35, '#a855f7');
      rimGrad.addColorStop(0.7, '#00e5ff');
      rimGrad.addColorStop(1, '#ec4899');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = '#00e5ff';
      this.ctx.shadowBlur = 18;
      this.ctx.fill();
    } else if (ringStyle === 'frosted_glass') {
      rimGrad.addColorStop(0, 'rgba(255, 255, 255, 0.85)');
      rimGrad.addColorStop(0.3, 'rgba(168, 85, 247, 0.5)');
      rimGrad.addColorStop(0.7, 'rgba(6, 182, 212, 0.5)');
      rimGrad.addColorStop(1, 'rgba(255, 255, 255, 0.75)');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = 'rgba(168, 85, 247, 0.4)';
      this.ctx.shadowBlur = 12;
      this.ctx.fill();
    } else if (ringStyle === 'aurora_luminous') {
      rimGrad.addColorStop(0, '#a855f7');
      rimGrad.addColorStop(0.3, '#06b6d4');
      rimGrad.addColorStop(0.6, '#3b82f6');
      rimGrad.addColorStop(1, '#10b981');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = '#a855f7';
      this.ctx.shadowBlur = 15;
      this.ctx.fill();
    } else if (ringStyle === 'champagne_minimal') {
      rimGrad.addColorStop(0, '#f3e5ab');
      rimGrad.addColorStop(0.25, '#d4af37');
      rimGrad.addColorStop(0.5, '#27272a');
      rimGrad.addColorStop(0.75, '#e5c158');
      rimGrad.addColorStop(1, '#18181b');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = 'rgba(212, 175, 55, 0.3)';
      this.ctx.shadowBlur = 8;
      this.ctx.fill();
    } else if (ringStyle === 'roasted_brass') {
      rimGrad.addColorStop(0, '#d97706');
      rimGrad.addColorStop(0.3, '#fcd34d');
      rimGrad.addColorStop(0.6, '#78350f');
      rimGrad.addColorStop(0.85, '#b45309');
      rimGrad.addColorStop(1, '#451a03');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = 'rgba(217, 119, 6, 0.4)';
      this.ctx.shadowBlur = 10;
      this.ctx.fill();
    } else if (ringStyle === 'carbon_sport') {
      rimGrad.addColorStop(0, '#ef4444');
      rimGrad.addColorStop(0.3, '#fbbf24');
      rimGrad.addColorStop(0.7, '#dc2626');
      rimGrad.addColorStop(1, '#18181b');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = '#ef4444';
      this.ctx.shadowBlur = 12;
      this.ctx.fill();
    } else if (ringStyle === 'peacock_teal') {
      rimGrad.addColorStop(0, '#ffd700');
      rimGrad.addColorStop(0.25, '#00e5ff');
      rimGrad.addColorStop(0.5, '#3b185f');
      rimGrad.addColorStop(0.75, '#00c49f');
      rimGrad.addColorStop(1, '#ffd700');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = '#00e5ff';
      this.ctx.shadowBlur = 16;
      this.ctx.fill();
    } else if (ringStyle === 'festive_ornament') {
      rimGrad.addColorStop(0, '#ffd700');
      rimGrad.addColorStop(0.3, '#dc2626');
      rimGrad.addColorStop(0.6, '#15803d');
      rimGrad.addColorStop(0.85, '#ffd700');
      rimGrad.addColorStop(1, '#991b1b');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = 'rgba(255, 215, 0, 0.5)';
      this.ctx.shadowBlur = 12;
      this.ctx.fill();
    } else if (ringStyle === 'candy_round') {
      rimGrad.addColorStop(0, '#f43f5e');
      rimGrad.addColorStop(0.25, '#38bdf8');
      rimGrad.addColorStop(0.5, '#fbbf24');
      rimGrad.addColorStop(0.75, '#a855f7');
      rimGrad.addColorStop(1, '#f43f5e');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = '#ec4899';
      this.ctx.shadowBlur = 12;
      this.ctx.fill();
    } else {
      // Default gold filigree
      rimGrad.addColorStop(0, '#ffd700');
      rimGrad.addColorStop(0.25, '#ffffff');
      rimGrad.addColorStop(0.5, '#d4af37');
      rimGrad.addColorStop(0.75, '#fef08a');
      rimGrad.addColorStop(1, '#946b00');
      this.ctx.fillStyle = rimGrad;
      this.ctx.shadowColor = 'rgba(212, 175, 55, 0.5)';
      this.ctx.shadowBlur = 10;
      this.ctx.fill();
    }

    // Outer Decorative Studs / Gems on Bezel
    const numStuds = config.studCount || 0;
    if (numStuds > 0) {
      const studR = radius + geom.outerRingWidth * 0.5;
      for (let s = 0; s < numStuds; s++) {
        const sAngle = (s * 2 * Math.PI) / numStuds;
        const sx = centerX + Math.cos(sAngle) * studR;
        const sy = centerY + Math.sin(sAngle) * studR;

        this.ctx.beginPath();
        this.ctx.arc(sx, sy, 2.8, 0, 2 * Math.PI);
        const studGrad = this.ctx.createRadialGradient(sx - 1, sy - 1, 0.5, sx, sy, 3);
        studGrad.addColorStop(0, '#ffffff');
        studGrad.addColorStop(0.5, '#ffd700');
        studGrad.addColorStop(1, '#854d0e');
        this.ctx.fillStyle = studGrad;
        this.ctx.shadowColor = 'rgba(0,0,0,0.5)';
        this.ctx.shadowBlur = 3;
        this.ctx.fill();
      }
    }

    this.ctx.restore();
  }

  drawSegmentText(centerX, centerY, radius, hubRadius, startAngle, sliceAngle, rawText, config) {
    const text = rawText || 'Reward';
    const midAngle = startAngle + sliceAngle / 2;
    const textRadius = hubRadius + (radius - hubRadius) * 0.65;

    this.ctx.save();
    this.ctx.translate(centerX, centerY);
    this.ctx.rotate(midAngle);
    this.ctx.textAlign = 'right';
    this.ctx.textBaseline = 'middle';

    // Theme-specific typography font selection
    let fontName = 'sans-serif';
    if (config.fontFamily === 'cinzel') fontName = "'Cinzel', serif";
    else if (config.fontFamily === 'playfair') fontName = "'Playfair Display', serif";
    else if (config.fontFamily === 'space_grotesk') fontName = "'Space Grotesk', monospace";
    else if (config.fontFamily === 'poppins') fontName = "'Poppins', sans-serif";
    else if (config.fontFamily === 'outfit') fontName = "'Outfit', sans-serif";
    else fontName = "'Inter', sans-serif";

    // Auto-scale font size based on text length and radius
    let fontSize = 13.5;
    if (text.length > 15) fontSize = 11;
    if (text.length > 20) fontSize = 9.5;
    if (radius < 130) fontSize = Math.max(fontSize - 2, 8.5);

    this.ctx.font = `bold ${fontSize}px ${fontName}`;
    this.ctx.fillStyle = '#ffffff';
    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.85)';
    this.ctx.shadowBlur = 5;

    let displayText = text;
    if (text.length > 22) displayText = text.substring(0, 20) + '...';
    this.ctx.fillText(displayText, radius - 14, 0);

    this.ctx.restore();
  }

  drawThemeHub(centerX, centerY, hubRadius, config) {
    const hubType = config.hubType || 'crown';

    this.ctx.save();

    // 1. Outer Hub Ring with drop shadow
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, hubRadius, 0, 2 * Math.PI);
    const rimGrad = this.ctx.createLinearGradient(centerX - hubRadius, centerY - hubRadius, centerX + hubRadius, centerY + hubRadius);
    rimGrad.addColorStop(0, '#ffd700');
    rimGrad.addColorStop(0.35, '#ffffff');
    rimGrad.addColorStop(0.7, '#d4af37');
    rimGrad.addColorStop(1, '#854d0e');
    this.ctx.fillStyle = rimGrad;
    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
    this.ctx.shadowBlur = 10;
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    // 2. Inner Hub Base Surface
    const innerR = hubRadius * 0.75;
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, innerR, 0, 2 * Math.PI);
    const innerGrad = this.ctx.createRadialGradient(centerX - 4, centerY - 4, 2, centerX, centerY, innerR);
    innerGrad.addColorStop(0, '#1e1324');
    innerGrad.addColorStop(1, '#09050d');
    this.ctx.fillStyle = innerGrad;
    this.ctx.lineWidth = 2;
    this.ctx.strokeStyle = '#ffd700';
    this.ctx.fill();
    this.ctx.stroke();

    // 3. Theme-Specific 3D Procedural Center Motif
    switch (hubType) {
      case 'peacock_flute':
        this.drawPeacockFluteMotif(centerX, centerY, innerR);
        break;
      case 'diya':
        this.drawDiyaMotif(centerX, centerY, innerR);
        break;
      case 'kite':
        this.drawKiteMotif(centerX, centerY, innerR);
        break;
      case 'snowflake':
        this.drawSnowflakeMotif(centerX, centerY, innerR);
        break;
      case 'holi_splash':
        this.drawHoliSplashMotif(centerX, centerY, innerR);
        break;
      case 'heart_gem':
        this.drawHeartGemMotif(centerX, centerY, innerR);
        break;
      case 'cyber_node':
        this.drawCyberNodeMotif(centerX, centerY, innerR);
        break;
      case 'coffee_cup':
        this.drawCoffeeCupMotif(centerX, centerY, innerR);
        break;
      case 'cloche_dome':
        this.drawClocheMotif(centerX, centerY, innerR);
        break;
      case 'speed_star':
        this.drawSpeedStarMotif(centerX, centerY, innerR);
        break;
      case 'pearl_sphere':
        this.drawPearlMotif(centerX, centerY, innerR);
        break;
      case 'prismatic_gem':
        this.drawPrismaticGemMotif(centerX, centerY, innerR);
        break;
      case 'candy_swirl':
        this.drawCandySwirlMotif(centerX, centerY, innerR);
        break;
      case 'diamond_crown':
      case 'crown':
      default:
        this.drawCrownMotif(centerX, centerY, innerR);
        break;
    }

    this.ctx.restore();
  }

  // ── PROCEDURAL HUB MOTIF DRAWERS ──
  drawPeacockFluteMotif(cx, cy, r) {
    // 1. Golden Krishna Flute
    this.ctx.strokeStyle = '#ffd700';
    this.ctx.lineWidth = 2.4;
    this.ctx.beginPath();
    this.ctx.moveTo(cx - r * 0.7, cy - r * 0.2);
    this.ctx.lineTo(cx + r * 0.7, cy + r * 0.2);
    this.ctx.stroke();

    // Finger holes
    this.ctx.fillStyle = '#060b1e';
    [-0.35, 0, 0.35].forEach(pos => {
      this.ctx.beginPath();
      this.ctx.arc(cx + r * pos, cy + r * pos * (0.4 / 1.4), 1.3, 0, 2 * Math.PI);
      this.ctx.fill();
    });

    // 2. Peacock Feather Eye Center Jewel
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.42, 0, 2 * Math.PI);
    const eyeGrad = this.ctx.createRadialGradient(cx - 2, cy - 2, 1, cx, cy, r * 0.42);
    eyeGrad.addColorStop(0, '#ffffff');
    eyeGrad.addColorStop(0.3, '#00e5ff');
    eyeGrad.addColorStop(0.65, '#3b185f');
    eyeGrad.addColorStop(1, '#060b1e');
    this.ctx.fillStyle = eyeGrad;
    this.ctx.fill();
  }

  drawDiyaMotif(cx, cy, r) {
    // Terracotta Diya Base
    this.ctx.fillStyle = '#ea580c';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy + r * 0.15, r * 0.48, 0, Math.PI, false);
    this.ctx.closePath();
    this.ctx.fill();

    // Sacred Flame with Golden Glow
    this.ctx.fillStyle = '#ffd700';
    this.ctx.shadowColor = '#f59e0b';
    this.ctx.shadowBlur = 10;
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy - r * 0.6);
    this.ctx.bezierCurveTo(cx + r * 0.3, cy - r * 0.1, cx + r * 0.2, cy + r * 0.1, cx, cy + r * 0.15);
    this.ctx.bezierCurveTo(cx - r * 0.2, cy + r * 0.1, cx - r * 0.3, cy - r * 0.1, cx, cy - r * 0.6);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
  }

  drawKiteMotif(cx, cy, r) {
    // 3D Diamond Kite
    const ks = r * 0.65;
    this.ctx.fillStyle = '#0284c7';
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy - ks);
    this.ctx.lineTo(cx + ks * 0.8, cy);
    this.ctx.lineTo(cx, cy + ks * 0.9);
    this.ctx.lineTo(cx - ks * 0.8, cy);
    this.ctx.closePath();
    this.ctx.fill();

    // Cross struts & Kite tail
    this.ctx.strokeStyle = '#ffd700';
    this.ctx.lineWidth = 1.4;
    this.ctx.stroke();
    this.ctx.fillStyle = '#ea580c';
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy + ks * 0.9);
    this.ctx.lineTo(cx - ks * 0.25, cy + ks * 1.3);
    this.ctx.lineTo(cx + ks * 0.25, cy + ks * 1.3);
    this.ctx.closePath();
    this.ctx.fill();
  }

  drawSnowflakeMotif(cx, cy, r) {
    const s = r * 0.65;
    this.ctx.strokeStyle = '#ffffff';
    this.ctx.lineWidth = 1.8;
    this.ctx.shadowColor = '#38bdf8';
    this.ctx.shadowBlur = 8;
    for (let a = 0; a < 6; a++) {
      const angle = (a * Math.PI) / 3;
      this.ctx.beginPath();
      this.ctx.moveTo(cx, cy);
      const ex = cx + Math.cos(angle) * s;
      const ey = cy + Math.sin(angle) * s;
      this.ctx.lineTo(ex, ey);
      // Side branches
      const bx = cx + Math.cos(angle) * s * 0.6;
      const by = cy + Math.sin(angle) * s * 0.6;
      this.ctx.moveTo(bx, by);
      this.ctx.lineTo(bx + Math.cos(angle + 0.5) * s * 0.3, by + Math.sin(angle + 0.5) * s * 0.3);
      this.ctx.moveTo(bx, by);
      this.ctx.lineTo(bx + Math.cos(angle - 0.5) * s * 0.3, by + Math.sin(angle - 0.5) * s * 0.3);
      this.ctx.stroke();
    }
    this.ctx.shadowBlur = 0;
  }

  drawHoliSplashMotif(cx, cy, r) {
    const colors = ['#f43f5e', '#06b6d4', '#eab308', '#ec4899', '#10b981'];
    for (let i = 0; i < 5; i++) {
      const angle = (i * 2 * Math.PI) / 5;
      const dist = r * 0.38;
      this.ctx.fillStyle = colors[i];
      this.ctx.beginPath();
      this.ctx.arc(cx + Math.cos(angle) * dist, cy + Math.sin(angle) * dist, r * 0.28, 0, 2 * Math.PI);
      this.ctx.fill();
    }
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.2, 0, 2 * Math.PI);
    this.ctx.fill();
  }

  drawHeartGemMotif(cx, cy, r) {
    const s = r * 0.55;
    this.ctx.fillStyle = '#f43f5e';
    this.ctx.shadowColor = 'rgba(244, 63, 94, 0.7)';
    this.ctx.shadowBlur = 10;
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy + s * 0.8);
    this.ctx.bezierCurveTo(cx - s * 1.3, cy + s * 0.2, cx - s * 1.1, cy - s * 0.9, cx, cy - s * 0.35);
    this.ctx.bezierCurveTo(cx + s * 1.1, cy - s * 0.9, cx + s * 1.3, cy + s * 0.2, cx, cy + s * 0.8);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
  }

  drawCyberNodeMotif(cx, cy, r) {
    this.ctx.strokeStyle = '#00e5ff';
    this.ctx.lineWidth = 1.8;
    this.ctx.shadowColor = '#00e5ff';
    this.ctx.shadowBlur = 12;
    // Hexagonal cyber core
    this.ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const angle = (i * Math.PI) / 3;
      const px = cx + Math.cos(angle) * r * 0.6;
      const py = cy + Math.sin(angle) * r * 0.6;
      if (i === 0) this.ctx.moveTo(px, py);
      else this.ctx.lineTo(px, py);
    }
    this.ctx.closePath();
    this.ctx.stroke();

    this.ctx.fillStyle = '#00e5ff';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r * 0.25, 0, 2 * Math.PI);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
  }

  drawCoffeeCupMotif(cx, cy, r) {
    // 1. 3D Porcelain Saucer
    this.ctx.fillStyle = '#ffffff';
    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.4)';
    this.ctx.shadowBlur = 6;
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + r * 0.45, r * 0.85, r * 0.28, 0, 0, 2 * Math.PI);
    this.ctx.fill();
    this.ctx.strokeStyle = '#d4af37';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();
    this.ctx.shadowBlur = 0;

    // 2. 3D Porcelain Cup Body
    const cs = r * 0.62;
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy + r * 0.1, cs, 0, Math.PI, false);
    this.ctx.lineTo(cx + cs, cy + r * 0.1);
    this.ctx.lineTo(cx - cs, cy + r * 0.1);
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.strokeStyle = '#d4af37';
    this.ctx.lineWidth = 1.2;
    this.ctx.stroke();

    // Cup handle
    this.ctx.beginPath();
    this.ctx.arc(cx + cs * 0.95, cy + r * 0.2, cs * 0.35, -Math.PI / 2, Math.PI / 2);
    this.ctx.strokeStyle = '#ffffff';
    this.ctx.lineWidth = 2.5;
    this.ctx.stroke();
    this.ctx.strokeStyle = '#d4af37';
    this.ctx.lineWidth = 0.8;
    this.ctx.stroke();

    // 3. Rich Dark Espresso Coffee Surface
    this.ctx.fillStyle = '#2b1207';
    this.ctx.beginPath();
    this.ctx.ellipse(cx, cy + r * 0.1, cs * 0.92, cs * 0.36, 0, 0, 2 * Math.PI);
    this.ctx.fill();

    // Golden-brown crema ring
    this.ctx.strokeStyle = '#d97706';
    this.ctx.lineWidth = 1.5;
    this.ctx.stroke();

    // 4. Creamy Heart Latte Art Foam
    const hs = cs * 0.38;
    const hy = cy + r * 0.1;
    this.ctx.fillStyle = '#fffbeb';
    this.ctx.shadowColor = 'rgba(255, 255, 255, 0.6)';
    this.ctx.shadowBlur = 4;
    this.ctx.beginPath();
    this.ctx.moveTo(cx, hy + hs * 0.7);
    this.ctx.bezierCurveTo(cx - hs * 1.2, hy + hs * 0.2, cx - hs * 1.1, hy - hs * 0.8, cx, hy - hs * 0.3);
    this.ctx.bezierCurveTo(cx + hs * 1.1, hy - hs * 0.8, cx + hs * 1.2, hy + hs * 0.2, cx, hy + hs * 0.7);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    // 5. Rising Steam Wisps from Cup
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
    this.ctx.lineWidth = 1.2;
    this.ctx.beginPath();
    this.ctx.moveTo(cx - 5, cy - r * 0.2);
    this.ctx.quadraticCurveTo(cx - 10, cy - r * 0.5, cx - 4, cy - r * 0.8);
    this.ctx.moveTo(cx + 5, cy - r * 0.2);
    this.ctx.quadraticCurveTo(cx + 10, cy - r * 0.5, cx + 4, cy - r * 0.8);
    this.ctx.stroke();
  }

  drawClocheMotif(cx, cy, r) {
    const s = r * 0.55;
    this.ctx.fillStyle = '#d4af37';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy + s * 0.2, s, Math.PI, 0, false);
    this.ctx.lineTo(cx + s, cy + s * 0.4);
    this.ctx.lineTo(cx - s, cy + s * 0.4);
    this.ctx.closePath();
    this.ctx.fill();

    // Handle knob
    this.ctx.fillStyle = '#ffd700';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy - s * 0.85, s * 0.22, 0, 2 * Math.PI);
    this.ctx.fill();
  }

  drawSpeedStarMotif(cx, cy, r) {
    const s = r * 0.65;
    this.ctx.fillStyle = '#ef4444';
    this.ctx.shadowColor = '#ef4444';
    this.ctx.shadowBlur = 8;
    this.ctx.beginPath();
    for (let i = 0; i < 5; i++) {
      const outerA = (i * 2 * Math.PI) / 5 - Math.PI / 2;
      const innerA = outerA + Math.PI / 5;
      this.ctx.lineTo(cx + Math.cos(outerA) * s, cy + Math.sin(outerA) * s);
      this.ctx.lineTo(cx + Math.cos(innerA) * s * 0.45, cy + Math.sin(innerA) * s * 0.45);
    }
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
  }

  drawPearlMotif(cx, cy, r) {
    const pearlR = r * 0.52;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, pearlR, 0, 2 * Math.PI);
    const grad = this.ctx.createRadialGradient(cx - pearlR * 0.3, cy - pearlR * 0.3, pearlR * 0.1, cx, cy, pearlR);
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.5, '#f1f5f9');
    grad.addColorStop(1, '#cbd5e1');
    this.ctx.fillStyle = grad;
    this.ctx.shadowColor = 'rgba(212, 175, 55, 0.4)';
    this.ctx.shadowBlur = 8;
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
  }

  drawPrismaticGemMotif(cx, cy, r) {
    const s = r * 0.55;
    this.ctx.fillStyle = '#a855f7';
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy - s);
    this.ctx.lineTo(cx + s * 0.86, cy + s * 0.5);
    this.ctx.lineTo(cx - s * 0.86, cy + s * 0.5);
    this.ctx.closePath();
    this.ctx.fill();

    this.ctx.fillStyle = '#38bdf8';
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy + s);
    this.ctx.lineTo(cx + s * 0.86, cy - s * 0.5);
    this.ctx.lineTo(cx - s * 0.86, cy - s * 0.5);
    this.ctx.closePath();
    this.ctx.fill();
  }

  drawCandySwirlMotif(cx, cy, r) {
    const s = r * 0.55;
    const colors = ['#f43f5e', '#ffffff', '#38bdf8', '#ffffff'];
    for (let i = 0; i < 4; i++) {
      this.ctx.fillStyle = colors[i];
      this.ctx.beginPath();
      this.ctx.moveTo(cx, cy);
      this.ctx.arc(cx, cy, s, (i * Math.PI) / 2, ((i + 1) * Math.PI) / 2);
      this.ctx.closePath();
      this.ctx.fill();
    }
  }

  drawCrownMotif(cx, cy, r) {
    const s = r * 0.6;
    this.ctx.fillStyle = '#ffd700';
    this.ctx.shadowColor = 'rgba(255, 215, 0, 0.6)';
    this.ctx.shadowBlur = 8;
    this.ctx.beginPath();
    this.ctx.moveTo(cx - s, cy + s * 0.5);
    this.ctx.lineTo(cx - s * 0.8, cy - s * 0.5);
    this.ctx.lineTo(cx - s * 0.3, cy);
    this.ctx.lineTo(cx, cy - s * 0.8);
    this.ctx.lineTo(cx + s * 0.3, cy);
    this.ctx.lineTo(cx + s * 0.8, cy - s * 0.5);
    this.ctx.lineTo(cx + s, cy + s * 0.5);
    this.ctx.closePath();
    this.ctx.fill();

    // Center Jewel Solitaire on Crown
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy - s * 0.8, 2, 0, 2 * Math.PI);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
  }

  // ── THEME-SPECIFIC POINTER DRAWERS ──
  drawThemePointer(cx, topY, scale, config) {
    const pType = config.pointerType || 'crown';
    this.ctx.save();
    this.ctx.translate(cx, topY);
    this.ctx.scale(scale, scale);

    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
    this.ctx.shadowBlur = 6;

    switch (pType) {
      case 'feather':
        // Peacock Plume Pointer
        this.ctx.fillStyle = '#ffd700';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.bezierCurveTo(9, 4, 11, -12, 0, -18);
        this.ctx.bezierCurveTo(-11, -12, -9, 4, 0, 18);
        this.ctx.fill();
        // Peacock Eye Dot
        this.ctx.fillStyle = '#00e5ff';
        this.ctx.beginPath();
        this.ctx.arc(0, -6, 4, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.fillStyle = '#3b185f';
        this.ctx.beginPath();
        this.ctx.arc(0, -6, 2, 0, 2 * Math.PI);
        this.ctx.fill();
        break;

      case 'flame':
        // Golden Diya Flame Pointer
        this.ctx.fillStyle = '#ffd700';
        this.ctx.shadowColor = '#ea580c';
        this.ctx.shadowBlur = 10;
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.quadraticCurveTo(12, 4, 0, -16);
        this.ctx.quadraticCurveTo(-12, 4, 0, 18);
        this.ctx.fill();
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(0, 4, 2.5, 0, 2 * Math.PI);
        this.ctx.fill();
        break;

      case 'kite':
        // Miniature Kite Pointer
        this.ctx.fillStyle = '#ea580c';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(10, 0);
        this.ctx.lineTo(0, -16);
        this.ctx.lineTo(-10, 0);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.strokeStyle = '#ffd700';
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();
        break;

      case 'snowflake':
        // Snowflake Ice Dart Pointer
        this.ctx.fillStyle = '#38bdf8';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(10, -8);
        this.ctx.lineTo(0, -16);
        this.ctx.lineTo(-10, -8);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(0, -4, 3, 0, 2 * Math.PI);
        this.ctx.fill();
        break;

      case 'heart_arrow':
        // Valentine Heart Arrow Pointer
        this.ctx.fillStyle = '#f43f5e';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(10, 2);
        this.ctx.bezierCurveTo(12, -8, 2, -14, 0, -8);
        this.ctx.bezierCurveTo(-2, -14, -12, -8, -10, 2);
        this.ctx.closePath();
        this.ctx.fill();
        break;

      case 'cyber_laser':
        // Neon High-Voltage Arrow Pointer
        this.ctx.fillStyle = '#00e5ff';
        this.ctx.shadowColor = '#00e5ff';
        this.ctx.shadowBlur = 12;
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(8, -14);
        this.ctx.lineTo(0, -10);
        this.ctx.lineTo(-8, -14);
        this.ctx.closePath();
        this.ctx.fill();
        break;

      case 'diamond':
        // Faceted Diamond Pointer
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(9, 0);
        this.ctx.lineTo(6, -14);
        this.ctx.lineTo(-6, -14);
        this.ctx.lineTo(-9, 0);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.strokeStyle = '#d4af37';
        this.ctx.lineWidth = 1.2;
        this.ctx.stroke();
        break;

      case 'minimal_needle':
        // Ultra-thin Surgical Needle Pointer
        this.ctx.fillStyle = '#f3e5ab';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(4, -14);
        this.ctx.lineTo(-4, -14);
        this.ctx.closePath();
        this.ctx.fill();
        break;

      case 'copper_bean':
        // Stylized Roasted Copper Coffee Bean Pointer
        this.ctx.fillStyle = '#d97706';
        this.ctx.shadowColor = 'rgba(217, 119, 6, 0.7)';
        this.ctx.shadowBlur = 8;
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(8, 0);
        this.ctx.bezierCurveTo(10, -12, -10, -12, -8, 0);
        this.ctx.closePath();
        this.ctx.fill();

        // Inner Roasted Coffee Bean with S-Crease
        this.ctx.fillStyle = '#3e1d0d';
        this.ctx.beginPath();
        this.ctx.ellipse(0, -3, 6, 8, 0, 0, 2 * Math.PI);
        this.ctx.fill();

        this.ctx.strokeStyle = '#fcd34d';
        this.ctx.lineWidth = 1.2;
        this.ctx.beginPath();
        this.ctx.moveTo(0, -9);
        this.ctx.quadraticCurveTo(2, -3, 0, 3);
        this.ctx.stroke();

        this.ctx.strokeStyle = '#ffd700';
        this.ctx.lineWidth = 1.4;
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(8, 0);
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(-8, 0);
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;
        break;

      case 'star_lollipop':
        // Playful Candy Pointer
        this.ctx.fillStyle = '#fbbf24';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(9, -2);
        this.ctx.lineTo(0, -14);
        this.ctx.lineTo(-9, -2);
        this.ctx.closePath();
        this.ctx.fill();
        break;

      case 'crown':
      default:
        // Royal Gold Crown Pointer
        this.ctx.fillStyle = '#ffd700';
        this.ctx.beginPath();
        this.ctx.moveTo(0, 18);
        this.ctx.lineTo(11, -4);
        this.ctx.lineTo(8, -16);
        this.ctx.lineTo(0, -10);
        this.ctx.lineTo(-8, -16);
        this.ctx.lineTo(-11, -4);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.strokeStyle = '#854d0e';
        this.ctx.lineWidth = 1.2;
        this.ctx.stroke();
        break;
    }

    this.ctx.restore();
  }

  adjustHexBrightness(hex, percent) {
    if (!hex || hex[0] !== '#') return hex || '#6366f1';
    let num = parseInt(hex.slice(1), 16);
    let r = (num >> 16) + percent;
    let g = ((num >> 8) & 0x00FF) + percent;
    let b = (num & 0x0000FF) + percent;
    r = Math.min(255, Math.max(0, r));
    g = Math.min(255, Math.max(0, g));
    b = Math.min(255, Math.max(0, b));
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  }

  destroy() {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
    }
    if (this.audioCtx) {
      try {
        this.audioCtx.close();
      } catch (e) {}
    }
    window.removeEventListener('resize', this.boundResize);
  }

  spinToSegment(targetIndex, onComplete) {
    if (this.isSpinning) return;
    this.isSpinning = true;
    this.winningSegment = null;
    if (this.spinButton) this.spinButton.disabled = true;

    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const numSlices = this.prizes.length || 6;
    const sliceAngle = (2 * Math.PI) / numSlices;
    const targetSliceCenter = targetIndex * sliceAngle + sliceAngle / 2;
    const fullSpins = prefersReducedMotion ? 2 : (6 + Math.floor(Math.random() * 3));

    // Pointer is at Top (-PI/2)
    const targetEndAngle = fullSpins * (2 * Math.PI) + (1.5 * Math.PI - targetSliceCenter);
    const startAngle = this.currentAngle;
    const totalRotation = targetEndAngle - (startAngle % (2 * Math.PI));
    const duration = prefersReducedMotion ? 1200 : 4800;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Smooth Ease-out Cubic with Natural Deceleration
      const ease = 1 - Math.pow(1 - progress, 3);
      this.currentAngle = startAngle + totalRotation * ease;

      const currentEffectiveAngle = (1.5 * Math.PI - (this.currentAngle % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
      const currentSegment = Math.floor(currentEffectiveAngle / sliceAngle);

      if (currentSegment !== this.lastTickSegment) {
        this.playTickSound();
        this.lastTickSegment = currentSegment;
      }

      this.draw();

      if (progress < 1) {
        this.animFrameId = requestAnimationFrame(animate);
      } else {
        this.isSpinning = false;
        this.winningSegment = targetIndex;
        this.draw(); // Highlight winning segment
        this.playWinSound();

        // Trigger celebratory particles in ThemeEngine if present
        if (window.ThemeEngineInstance) {
          const rect = this.canvas.getBoundingClientRect();
          window.ThemeEngineInstance.triggerWinCelebration(rect.left + rect.width / 2, rect.top + rect.height / 2);
        }

        if (onComplete) onComplete();
      }
    };

    this.animFrameId = requestAnimationFrame(animate);
  }
}

window.SpinWheel = SpinWheel;
window.THEME_SPINNER_REGISTRY = THEME_SPINNER_REGISTRY;

