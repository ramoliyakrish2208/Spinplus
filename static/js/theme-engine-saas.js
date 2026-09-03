/**
 * SPIN & WIN — DYNAMIC THEME ENGINE SAAS PLATFORM
 * Master Interactive Controller & Real-Time Live Preview Engine
 */

(function () {
    'use strict';

    // Global Registry of Theme Data for the Showcase
    const SHOWCASE_THEMES = {
        'royal_jewellery': {
            title: 'Royal Gold Jewellery',
            campaign: 'Jewellery Special • Spin & Win',
            sub: 'Win Exclusive Diamond & Gold Rewards',
            bg: 'radial-gradient(circle at 50% 30%, #3b1424 0%, #160810 70%, #070305 100%)',
            primary: '#ffd700',
            secondary: '#4a152d',
            accent: '#ffd700',
            font: 'cinzel',
            emoji: '👑',
            prize: 'FREE Diamond Ring'
        },
        'restaurant': {
            title: 'Food & Feast Restaurant',
            campaign: 'Gourmet Feast • Spin & Win',
            sub: 'Get Delicious Dining Rewards',
            bg: 'radial-gradient(circle at 50% 30%, #451a03 0%, #1c0d06 70%, #0a0502 100%)',
            primary: '#f59e0b',
            secondary: '#78350f',
            accent: '#fcd34d',
            font: 'playfair',
            emoji: '🍔',
            prize: 'FREE Gourmet Burger'
        },
        'fashion': {
            title: 'Burgundy Elegance Fashion',
            campaign: 'Haute Couture • Spin & Win',
            sub: 'Style Your Runway Rewards',
            bg: 'radial-gradient(circle at 50% 30%, #4c0519 0%, #1f030a 70%, #0b0104 100%)',
            primary: '#f43f5e',
            secondary: '#881337',
            accent: '#ffd700',
            font: 'cinzel',
            emoji: '👠',
            prize: 'Flat ₹500 OFF Shopping'
        },
        'pearl': {
            title: 'Pearl Beauty Salon',
            campaign: 'Beauty Glow • Spin & Win',
            sub: 'Glow with Luxury Skincare',
            bg: 'radial-gradient(circle at 50% 30%, #ffe4e6 0%, #fecdd3 60%, #fda4af 100%)',
            primary: '#fb7185',
            secondary: '#be123c',
            accent: '#ffffff',
            font: 'playfair',
            emoji: '💄',
            prize: 'FREE Facial & Serum'
        },
        'electronics': {
            title: 'Neon Cyber Electronics',
            campaign: 'Cyber Tech • Spin & Win',
            sub: 'High Voltage Gadget Rewards',
            bg: 'radial-gradient(circle at 50% 30%, #082f49 0%, #031524 70%, #01080e 100%)',
            primary: '#06b6d4',
            secondary: '#0369a1',
            accent: '#38bdf8',
            font: 'space_grotesk',
            emoji: '⚡',
            prize: 'FREE Gaming Headset'
        },
        'kids': {
            title: 'Playful Kids Store',
            campaign: 'Fun Rewards • Spin & Win',
            sub: 'Joyful Toys & Gifts for Kids',
            bg: 'radial-gradient(circle at 50% 30%, #e0f2fe 0%, #bae6fd 60%, #7dd3fc 100%)',
            primary: '#38bdf8',
            secondary: '#0284c7',
            accent: '#facc15',
            font: 'poppins',
            emoji: '🧸',
            prize: 'FREE Teddy Bear'
        },
        'coffee': {
            title: 'Café & Coffee Shop',
            campaign: 'Artisan Café • Sip & Win',
            sub: 'Sip & Win Barista Discounts',
            bg: 'radial-gradient(circle at 50% 30%, #3e1f0e 0%, #1c0d06 70%, #0a0402 100%)',
            primary: '#d97706',
            secondary: '#78350f',
            accent: '#fcd34d',
            font: 'playfair',
            emoji: '☕',
            prize: 'FREE Caramel Latte'
        },
        'sports': {
            title: 'Sporty Red Store',
            campaign: 'Sports Power • Gear Up & Win',
            sub: 'Power Rewards for Athletes',
            bg: 'radial-gradient(circle at 50% 30%, #450a0a 0%, #180505 70%, #080202 100%)',
            primary: '#ef4444',
            secondary: '#991b1b',
            accent: '#ffffff',
            font: 'space_grotesk',
            emoji: '⚽',
            prize: 'FREE Sports Shoes'
        },
        'diwali': {
            title: 'Diwali Grand Festival',
            campaign: 'Diwali Special • Spin & Win',
            sub: 'Light Up Your Festive Rewards',
            bg: 'radial-gradient(circle at 50% 30%, #2e1065 0%, #170733 70%, #080214 100%)',
            primary: '#ffd700',
            secondary: '#6b21a8',
            accent: '#f59e0b',
            font: 'playfair',
            emoji: '🪔',
            prize: '₹1000 Diwali Gold Coin'
        },
        'christmas': {
            title: 'Christmas Winter Magic',
            campaign: 'Holiday Cheer • Spin & Win',
            sub: 'Festive Holiday Discounts',
            bg: 'radial-gradient(circle at 50% 30%, #14532d 0%, #052e16 60%, #450a0a 100%)',
            primary: '#ef4444',
            secondary: '#166534',
            accent: '#fef08a',
            font: 'playfair',
            emoji: '🎄',
            prize: 'FREE Christmas Gift Hamper'
        },
        'new_year': {
            title: 'New Year Golden Celebration',
            campaign: 'New Year 2026 • Spin & Win',
            sub: 'Start the Year with Great Luck',
            bg: 'radial-gradient(circle at 50% 30%, #172554 0%, #091129 70%, #020510 100%)',
            primary: '#ffd700',
            secondary: '#1e40af',
            accent: '#ffffff',
            font: 'cinzel',
            emoji: '🎆',
            prize: '50% OFF New Year Special'
        },
        'holi': {
            title: 'Holi Colors of Joy',
            campaign: 'Holi Dhamaka • Play & Win',
            sub: 'Vibrant Colors of Happiness',
            bg: 'radial-gradient(circle at 50% 30%, #f472b6 0%, #38bdf8 50%, #facc15 100%)',
            primary: '#f43f5e',
            secondary: '#a855f7',
            accent: '#06b6d4',
            font: 'poppins',
            emoji: '🎨',
            prize: 'FREE Organic Color Hamper'
        },
        'valentines': {
            title: 'Valentine’s Day Love & Rewards',
            campaign: 'Love & Romance • Share the Love',
            sub: 'Romantic Surprises for Two',
            bg: 'radial-gradient(circle at 50% 30%, #831843 0%, #4c0519 70%, #1f030a 100%)',
            primary: '#f43f5e',
            secondary: '#9d174d',
            accent: '#fda4af',
            font: 'playfair',
            emoji: '💖',
            prize: 'FREE Romantic Dinner Voucher'
        },
        'eid': {
            title: 'Eid Blessings & Rewards',
            campaign: 'Eid Celebration • Spin & Win',
            sub: 'Celebrate with Warm Blessings',
            bg: 'radial-gradient(circle at 50% 30%, #064e3b 0%, #022c22 70%, #01140f 100%)',
            primary: '#ffd700',
            secondary: '#047857',
            accent: '#fef08a',
            font: 'cinzel',
            emoji: '🌙',
            prize: 'FREE Festive Attire Discount'
        },
        'summer_sale': {
            title: 'Summer Sale Cool Offers',
            campaign: 'Beat the Heat • Cool Offers',
            sub: 'Refreshing Summer Savings',
            bg: 'radial-gradient(circle at 50% 30%, #0284c7 0%, #0369a1 50%, #f59e0b 100%)',
            primary: '#f59e0b',
            secondary: '#0284c7',
            accent: '#10b981',
            font: 'outfit',
            emoji: '🌴',
            prize: 'Flat 40% OFF Summer Gear'
        },
        'halloween': {
            title: 'Halloween Spooky Rewards',
            campaign: 'Trick or Treat • Spooky Spin',
            sub: 'Spooky Treats & Costumes',
            bg: 'radial-gradient(circle at 50% 30%, #581c87 0%, #2e1065 60%, #431407 100%)',
            primary: '#ea580c',
            secondary: '#581c87',
            accent: '#fbbf24',
            font: 'space_grotesk',
            emoji: '🎃',
            prize: 'FREE Halloween Costume Gift'
        },
        'glass': {
            title: 'Glassmorphism Style',
            campaign: 'Glassmorphism • Spin & Win',
            sub: 'Modern • Elegant • Premium',
            bg: 'radial-gradient(circle at 50% 30%, #3b0764 0%, #1e1b4b 50%, #09091b 100%)',
            primary: '#a855f7',
            secondary: '#6366f1',
            accent: '#38bdf8',
            font: 'inter',
            emoji: '🧊',
            prize: '20% OFF Total Bill'
        },
        'aurora': {
            title: 'Aurora Theme Style',
            campaign: 'Aurora Futuristic • Spin & Win',
            sub: 'Dreamy • Vibrant • Futuristic',
            bg: 'radial-gradient(circle at 50% 30%, #0284c7 0%, #064e3b 40%, #090e1f 100%)',
            primary: '#06b6d4',
            secondary: '#a855f7',
            accent: '#34d399',
            font: 'outfit',
            emoji: '🌌',
            prize: 'Flat ₹300 Cyber Voucher'
        },
        'bento': {
            title: 'Bento UI Style',
            campaign: 'Bento UI • TechStore Rewards',
            sub: 'Clean • Organized • Modern',
            bg: 'radial-gradient(circle at 50% 30%, #f8fafc 0%, #e2e8f0 100%)',
            primary: '#2563eb',
            secondary: '#475569',
            accent: '#f59e0b',
            font: 'inter',
            emoji: '📱',
            prize: '15% OFF Gadgets'
        },
        'minimal_luxury': {
            title: 'Minimal Luxury Style',
            campaign: 'Minimal Luxury • Spin & Win',
            sub: 'Simple • Sophisticated • Classy',
            bg: 'radial-gradient(circle at 50% 30%, #27272a 0%, #18181b 50%, #09090b 100%)',
            primary: '#ffd700',
            secondary: '#27272a',
            accent: '#d4af37',
            font: 'playfair',
            emoji: '💎',
            prize: 'Exclusive VIP Access'
        }
    };

    let activeGlobalTheme = 'royal_jewellery';
    let isSpinningLive = false;
    let atmosphereEngine = null;

    /**
     * Initializer when DOM is ready
     */
    document.addEventListener('DOMContentLoaded', () => {
        // 1. Initialize Atmosphere Engine
        initAtmosphere();

        // 2. Render Hero 4 Showcase Wheels
        renderHeroShowcaseWheels();

        // 3. Render 16 Theme Example Wheels
        renderThemeExamplesWheels();

        // 4. Render Live Phone Wheel
        renderLivePhoneWheel();

        // 5. Initialize Lucide Icons if available
        if (window.lucide) {
            window.lucide.createIcons();
        }
    });

    /**
     * Render the 4 Hero Showcase Wheels
     */
    function renderHeroShowcaseWheels() {
        const heroWheels = [
            { id: 'heroWheelGlass', theme: 'glass' },
            { id: 'heroWheelAurora', theme: 'aurora' },
            { id: 'heroWheelBento', theme: 'bento' },
            { id: 'heroWheelLuxury', theme: 'minimal_luxury' }
        ];

        heroWheels.forEach(w => {
            const canvas = document.getElementById(w.id);
            if (canvas) {
                drawStaticShowcaseWheel(canvas, w.theme, 140);
            }
        });
    }

    /**
     * Render the 16 Theme Examples Wheels
     */
    function renderThemeExamplesWheels() {
        const exampleIds = [
            { id: 'miniWheelJewellery', theme: 'royal_jewellery' },
            { id: 'miniWheelRestaurant', theme: 'restaurant' },
            { id: 'miniWheelFashion', theme: 'fashion' },
            { id: 'miniWheelBeauty', theme: 'pearl' },
            { id: 'miniWheelElectronics', theme: 'electronics' },
            { id: 'miniWheelKids', theme: 'kids' },
            { id: 'miniWheelCoffee', theme: 'coffee' },
            { id: 'miniWheelSports', theme: 'sports' },
            { id: 'miniWheelDiwali', theme: 'diwali' },
            { id: 'miniWheelChristmas', theme: 'christmas' },
            { id: 'miniWheelNewYear', theme: 'new_year' },
            { id: 'miniWheelHoli', theme: 'holi' },
            { id: 'miniWheelValentine', theme: 'valentines' },
            { id: 'miniWheelEid', theme: 'eid' },
            { id: 'miniWheelSummer', theme: 'summer_sale' },
            { id: 'miniWheelHalloween', theme: 'halloween' }
        ];

        exampleIds.forEach(item => {
            const canvas = document.getElementById(item.id);
            if (canvas) {
                drawStaticShowcaseWheel(canvas, item.theme, 110);
            }
        });
    }

    /**
     * Draw a high-fidelity themed wheel directly onto a canvas using theme registry
     */
    function drawStaticShowcaseWheel(canvas, themeKey, size) {
        const dpr = window.devicePixelRatio || 1;
        canvas.width = size * dpr;
        canvas.height = size * dpr;
        canvas.style.width = size + 'px';
        canvas.style.height = size + 'px';

        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);

        const cx = size / 2;
        const cy = size / 2;
        const radius = size * 0.44;

        const reg = (window.THEME_SPINNER_REGISTRY && window.THEME_SPINNER_REGISTRY[themeKey]) 
            ? window.THEME_SPINNER_REGISTRY[themeKey]
            : {
                palette: ['#4f46e5', '#f59e0b', '#10b981', '#ec4899', '#8b5cf6', '#64748b'],
                ringStyle: 'gold_filigree',
                studCount: 8
            };

        const palette = reg.palette || ['#4f46e5', '#f59e0b', '#10b981', '#ec4899', '#8b5cf6', '#64748b'];
        const numSlices = 6;
        const sliceAngle = (2 * Math.PI) / numSlices;

        ctx.clearRect(0, 0, size, size);

        // 1. Outer Bezel / Rim
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, radius + 4, 0, Math.PI * 2);
        ctx.fillStyle = '#0f172a';
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 8;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(cx, cy, radius + 2, 0, Math.PI * 2);
        const rimGrad = ctx.createLinearGradient(0, 0, size, size);
        rimGrad.addColorStop(0, '#ffd700');
        rimGrad.addColorStop(0.5, '#b45309');
        rimGrad.addColorStop(1, '#ffd700');
        ctx.fillStyle = rimGrad;
        ctx.fill();
        ctx.restore();

        // 2. Wheel Slices with 3D Radial Depth
        for (let i = 0; i < numSlices; i++) {
            const startAngle = i * sliceAngle - Math.PI / 2;
            const endAngle = startAngle + sliceAngle;
            const color = palette[i % palette.length];

            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, radius, startAngle, endAngle);
            ctx.closePath();

            // Radial shader
            const radGrad = ctx.createRadialGradient(cx, cy, radius * 0.1, cx, cy, radius);
            radGrad.addColorStop(0, adjustBrightness(color, 25));
            radGrad.addColorStop(0.7, color);
            radGrad.addColorStop(1, adjustBrightness(color, -25));
            ctx.fillStyle = radGrad;
            ctx.fill();

            ctx.strokeStyle = 'rgba(255,255,255,0.25)';
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        // 3. Center Hub
        ctx.beginPath();
        ctx.arc(cx, cy, radius * 0.28, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = 'rgba(0,0,0,0.4)';
        ctx.shadowBlur = 6;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(cx, cy, radius * 0.22, 0, Math.PI * 2);
        ctx.fillStyle = '#0f172a';
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.beginPath();
        ctx.arc(cx, cy, radius * 0.12, 0, Math.PI * 2);
        ctx.fillStyle = '#ffd700';
        ctx.fill();

        // 4. Top Pointer
        ctx.save();
        ctx.translate(cx, cy - radius + 2);
        ctx.fillStyle = '#ffd700';
        ctx.shadowColor = 'rgba(0,0,0,0.6)';
        ctx.shadowBlur = 4;
        ctx.beginPath();
        ctx.moveTo(0, 8);
        ctx.lineTo(6, -6);
        ctx.lineTo(-6, -6);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
    }

    /**
     * Render the Live Phone Wheel
     */
    function renderLivePhoneWheel() {
        const canvas = document.getElementById('livePhoneWheelCanvas');
        if (canvas) {
            drawStaticShowcaseWheel(canvas, activeGlobalTheme, 130);
        }
    }

    /**
     * Global Theme Selection Handler
     */
    window.selectThemeGlobally = function (themeKey) {
        if (!SHOWCASE_THEMES[themeKey]) return;
        activeGlobalTheme = themeKey;
        const data = SHOWCASE_THEMES[themeKey];

        // 1. Update Live Phone Preview
        const phoneHeader = document.getElementById('livePhoneCampaignTitle');
        const phoneSub = document.getElementById('livePhoneSubtitle');
        const phoneBrand = document.getElementById('livePhoneBrand');
        const phoneBtn = document.getElementById('livePhoneSpinBtn');
        const phoneContainer = document.getElementById('livePhoneContainer');

        if (phoneHeader) phoneHeader.textContent = data.campaign;
        if (phoneSub) phoneSub.textContent = data.sub;
        if (phoneBrand) phoneBrand.innerHTML = `${data.emoji} ${data.title.split(' ')[0].toUpperCase()}`;
        if (phoneBtn) {
            phoneBtn.style.background = `linear-gradient(135deg, ${data.primary}, ${data.secondary})`;
            phoneBtn.style.color = (data.font === 'inter' || themeKey === 'bento') ? '#ffffff' : '#0f172a';
        }
        if (phoneContainer) {
            phoneContainer.style.background = data.bg;
        }

        // Re-draw phone wheel
        renderLivePhoneWheel();

        // 2. Update Atmosphere Engine
        if (atmosphereEngine && atmosphereEngine.applyTheme) {
            atmosphereEngine.applyTheme(themeKey);
        }

        // 3. Highlight Thumbnail in Customization Panel
        document.querySelectorAll('.theme-thumb-card').forEach(card => card.classList.remove('active'));
        const thumbCard = document.getElementById(`thumb-${themeKey}`);
        if (thumbCard) thumbCard.classList.add('active');

        // 4. Subtle Page Background Shift
        document.body.style.background = data.bg;
    };

    /**
     * Interactive Filtering for Theme Examples Grid
     */
    window.filterThemeGrid = function (filterType) {
        document.querySelectorAll('.filter-tab-btn').forEach(btn => btn.classList.remove('active'));
        if (event && event.target) event.target.classList.add('active');

        const bizRow = document.getElementById('businessThemesRow');
        const festRow = document.getElementById('festivalThemesRow');

        if (filterType === 'all') {
            if (bizRow) bizRow.style.display = 'grid';
            if (festRow) festRow.style.display = 'grid';
        } else if (filterType === 'business') {
            if (bizRow) bizRow.style.display = 'grid';
            if (festRow) festRow.style.display = 'none';
        } else if (filterType === 'festivals') {
            if (bizRow) bizRow.style.display = 'none';
            if (festRow) festRow.style.display = 'grid';
        }
    };

    /**
     * Filter Custom Themes in Bento Panel
     */
    window.filterCustomThemes = function (cat) {
        document.querySelectorAll('.cat-filter-link').forEach(link => link.classList.remove('active'));
        if (event && event.target) event.target.classList.add('active');
    };

    /**
     * Spin Live Mobile Wheel with Real Animation & Celebration
     */
    window.spinLiveMobileWheel = function () {
        if (isSpinningLive) return;
        isSpinningLive = true;

        const canvas = document.getElementById('livePhoneWheelCanvas');
        if (!canvas) return;

        const btn = document.getElementById('livePhoneSpinBtn');
        if (btn) btn.disabled = true;

        let rotation = 0;
        const totalRounds = 5 + Math.random() * 3;
        const targetDeg = totalRounds * 360 + Math.floor(Math.random() * 360);
        const duration = 4000;
        const startTime = performance.now();

        function animate(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const currentDeg = easeProgress * targetDeg;

            const ctx = canvas.getContext('2d');
            const dpr = window.devicePixelRatio || 1;
            const size = 130;

            ctx.save();
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.translate((size * dpr) / 2, (size * dpr) / 2);
            ctx.rotate((currentDeg * Math.PI) / 180);
            ctx.translate(-(size * dpr) / 2, -(size * dpr) / 2);

            drawStaticShowcaseWheel(canvas, activeGlobalTheme, size);
            ctx.restore();

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                isSpinningLive = false;
                if (btn) btn.disabled = false;
                showWinningModal();
            }
        }

        requestAnimationFrame(animate);
    };

    /**
     * Show Winning Reward Modal
     */
    function showWinningModal() {
        const modal = document.getElementById('saasWinModal');
        const prizeEl = document.getElementById('saasWinPrize');
        const emojiEl = document.getElementById('saasWinEmoji');

        const themeData = SHOWCASE_THEMES[activeGlobalTheme] || SHOWCASE_THEMES['royal_jewellery'];

        if (prizeEl) prizeEl.textContent = themeData.prize;
        if (emojiEl) emojiEl.textContent = themeData.emoji;

        if (modal) {
            modal.style.display = 'flex';
        }

        if (atmosphereEngine && atmosphereEngine.triggerWinCelebration) {
            atmosphereEngine.triggerWinCelebration();
        }
    }

    window.closeSaasWinModal = function () {
        const modal = document.getElementById('saasWinModal');
        if (modal) modal.style.display = 'none';
    };

    /**
     * Customization Control Callbacks
     */
    window.setCustomColor = function (hex) {
        document.querySelectorAll('.color-swatch-circle').forEach(sw => sw.classList.remove('active'));
        if (event && event.target) event.target.classList.add('active');
        const phoneBtn = document.getElementById('livePhoneSpinBtn');
        if (phoneBtn) phoneBtn.style.background = hex;
    };

    window.setSpinnerRim = function (rimStyle) {
        renderLivePhoneWheel();
    };

    window.setCustomFont = function (fontKey) {
        document.querySelectorAll('.typo-pill').forEach(pill => pill.classList.remove('active'));
        if (event && event.target) event.target.classList.add('active');
    };

    window.toggleConfetti = function (checked) {};
    window.toggle3DEffects = function (checked) {};

    window.resetToDefaults = function () {
        selectThemeGlobally('royal_jewellery');
    };

    /**
     * Atmosphere Engine Initialization
     */
    function initAtmosphere() {
        if (window.ThemeEngine) {
            atmosphereEngine = new ThemeEngine('saasAtmosphereCanvas', 'royal_jewellery');
            window.activeAtmosphereEngine = atmosphereEngine;
        }
    }

    function adjustBrightness(hex, percent) {
        if (!hex || hex[0] !== '#') return hex || '#6366f1';
        let num = parseInt(hex.slice(1), 16);
        let r = (num >> 16) + percent;
        let g = ((num >> 8) & 0x00ff) + percent;
        let b = (num & 0x0000ff) + percent;
        r = Math.min(255, Math.max(0, r));
        g = Math.min(255, Math.max(0, g));
        b = Math.min(255, Math.max(0, b));
        return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
    }

})();
