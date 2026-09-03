/**
 * Spin & Win SaaS Platform — Theme 3.0 Engine
 * Complete Procedural 3D Shop Theme System (Visual Atmospheres, 3D Objects, Particles, Win Celebrations & Mobile Fallbacks)
 */

class ThemeEngine {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.particles = [];
        this.blobs = [];
        this.celebrationParticles = [];
        this.animId = null;
        this.theme = 'royal';
        this.intensity = 'balanced'; // subtle, balanced, dynamic
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.isMobile = window.innerWidth <= 768;

        this.init();
    }

    init() {
        this.theme = document.body.getAttribute('data-theme') || 'royal';
        this.setupAtmosphereCanvas();
        this.createDecorations();
        this.startAnimation();

        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth <= 768;
            this.resizeCanvas();
        });
    }

    setupAtmosphereCanvas() {
        let existing = document.getElementById('themeAtmosphereCanvas');
        if (existing) existing.remove();

        this.canvas = document.createElement('canvas');
        this.canvas.id = 'themeAtmosphereCanvas';
        this.canvas.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 0;
      opacity: 0.92;
    `;
        document.body.insertBefore(this.canvas, document.body.firstChild);
        this.ctx = this.canvas.getContext('2d');
        this.resizeCanvas();
    }

    resizeCanvas() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.createDecorations();
    }

    createDecorations() {
        this.particles = [];
        this.blobs = [];
        this.celebrationParticles = [];
        if (this.isReducedMotion) return;

        let count = this.isMobile ? 18 : 45;
        if (this.intensity === 'subtle') count = Math.floor(count * 0.4);
        if (this.intensity === 'dynamic') count = Math.floor(count * 1.5);

        const w = this.canvas ? this.canvas.width : window.innerWidth;
        const h = this.canvas ? this.canvas.height : window.innerHeight;

        // Special Atmosphere: Aurora Blobs
        if (this.theme === 'aurora') {
            const blobColors = [
                'rgba(168, 85, 247, 0.25)', // purple
                'rgba(6, 182, 212, 0.25)',  // cyan
                'rgba(59, 130, 246, 0.22)',  // blue
                'rgba(16, 185, 129, 0.20)'  // emerald
            ];
            const blobCount = this.isMobile ? 3 : 5;
            for (let b = 0; b < blobCount; b++) {
                this.blobs.push({
                    x: Math.random() * w,
                    y: Math.random() * (h * 0.7),
                    radius: Math.random() * (this.isMobile ? 120 : 260) + 120,
                    color: blobColors[b % blobColors.length],
                    vx: (Math.random() - 0.5) * 0.6,
                    vy: (Math.random() - 0.5) * 0.4,
                    pulse: Math.random() * Math.PI * 2,
                    pulseSpeed: 0.015
                });
            }
        }

        // Special Atmosphere: Janmashtami Celestial Moon & Divine Atmosphere
        const isJanmashtami = ['janmashtami', 'janmashtami_jewellery', 'janmashtami_sweets', 'janmashtami_clothing', 'janmashtami_kids'].includes(this.theme);
        if (isJanmashtami) {
            this.janmashtamiMoon = {
                x: w * (this.isMobile ? 0.82 : 0.86),
                y: h * (this.isMobile ? 0.12 : 0.16),
                radius: this.isMobile ? 34 : 58,
                pulse: 0,
                pulseSpeed: 0.018
            };
        } else {
            this.janmashtamiMoon = null;
        }

        // Special Atmosphere: Coffee Theme 3D Porcelain Cup & Ambient Mocha Glow
        if (this.theme === 'coffee') {
            this.coffeeCup = {
                x: w * (this.isMobile ? 0.18 : 0.14),
                y: h * (this.isMobile ? 0.88 : 0.84),
                radius: this.isMobile ? 32 : 48,
                steamPhase: 0
            };
        } else {
            this.coffeeCup = null;
        }

        for (let i = 0; i < count; i++) {
            this.particles.push(this.generateParticle(w, h));
        }
    }

    generateParticle(w, h) {
        const base = {
            x: Math.random() * w,
            y: Math.random() * h,
            size: Math.random() * 4 + 1.5,
            speedX: (Math.random() - 0.5) * 0.8,
            speedY: (Math.random() - 0.5) * 0.8,
            opacity: Math.random() * 0.7 + 0.3,
            pulse: Math.random() * 0.05 + 0.01,
            angle: Math.random() * Math.PI * 2,
            spinSpeed: (Math.random() - 0.5) * 0.03
        };

        switch (this.theme) {
            case 'luxury_black': {
                const geomTypes = ['cube_edge', 'diamond_facet', 'champagne_bokeh', 'light_beam'];
                const geomType = geomTypes[Math.floor(Math.random() * geomTypes.length)];
                return {
                    ...base,
                    type: geomType,
                    color: ['#f3e5ab', '#d4af37', '#e5c158', '#ffffff', '#a1a1aa'][Math.floor(Math.random() * 5)],
                    size: geomType === 'champagne_bokeh' ? (Math.random() * 5 + 2) : (Math.random() * 8 + 4),
                    speedY: (Math.random() - 0.5) * 0.35,
                    speedX: (Math.random() - 0.5) * 0.35,
                    spinSpeed: (Math.random() - 0.5) * 0.02
                };
            }

            case 'pearl': {
                const isPearl = Math.random() > 0.4;
                return {
                    ...base,
                    type: isPearl ? 'pearl_sphere' : 'pearl_bloom',
                    color: ['#ffffff', '#f8fafc', '#fef08a', '#d4af37', '#e2e8f0'][Math.floor(Math.random() * 5)],
                    size: isPearl ? (Math.random() * 7 + 4) : (Math.random() * 4 + 1.5),
                    speedY: -Math.random() * 0.5 - 0.1,
                    speedX: (Math.random() - 0.5) * 0.3,
                    spinSpeed: (Math.random() - 0.5) * 0.02
                };
            }

            case 'aurora': {
                const isSphere = Math.random() > 0.45;
                return {
                    ...base,
                    type: isSphere ? 'aurora_sphere' : 'aurora_particle',
                    color: ['#a855f7', '#06b6d4', '#3b82f6', '#10b981', '#ec4899'][Math.floor(Math.random() * 5)],
                    size: isSphere ? (Math.random() * 9 + 4) : (Math.random() * 4 + 1.5),
                    speedX: (Math.random() - 0.5) * 0.5,
                    speedY: -Math.random() * 0.6 - 0.15,
                    spinSpeed: (Math.random() - 0.5) * 0.025
                };
            }

            case 'glass': {
                const prismTypes = ['glass_prism', 'glass_disc', 'glass_particle'];
                const pType = prismTypes[Math.floor(Math.random() * prismTypes.length)];
                return {
                    ...base,
                    type: pType,
                    color: ['rgba(255, 255, 255, 0.85)', 'rgba(99, 102, 241, 0.7)', 'rgba(56, 189, 248, 0.7)'][Math.floor(Math.random() * 3)],
                    size: pType === 'glass_particle' ? (Math.random() * 3.5 + 1.5) : (Math.random() * 8 + 5),
                    speedY: -Math.random() * 0.45 - 0.1,
                    speedX: (Math.random() - 0.5) * 0.4,
                    spinSpeed: (Math.random() - 0.5) * 0.02
                };
            }

            case 'neon':
            case 'electronics': {
                const cyberTypes = ['cyber_hex', 'microchip', 'energy_particle', 'digital_pulse'];
                const cType = cyberTypes[Math.floor(Math.random() * cyberTypes.length)];
                return {
                    ...base,
                    type: cType,
                    color: ['#06b6d4', '#a855f7', '#3b82f6', '#f43f5e', '#38bdf8'][Math.floor(Math.random() * 5)],
                    size: cType === 'cyber_hex' || cType === 'microchip' ? (Math.random() * 8 + 4) : (Math.random() * 3 + 1.5),
                    speedX: (Math.random() - 0.5) * 1.2,
                    speedY: (Math.random() - 0.5) * 1.2,
                    spinSpeed: (Math.random() - 0.5) * 0.04
                };
            }

            case 'restaurant': {
                const restTypes = ['cloche_dome', 'wine_bubble', 'warm_glow'];
                const rType = restTypes[Math.floor(Math.random() * restTypes.length)];
                return {
                    ...base,
                    type: rType,
                    color: ['#f59e0b', '#d97706', '#fef3c7', '#fbbf24'][Math.floor(Math.random() * 4)],
                    size: rType === 'cloche_dome' ? (Math.random() * 7 + 4) : (Math.random() * 4 + 1.5),
                    speedY: -Math.random() * 0.5 - 0.1,
                    speedX: (Math.random() - 0.5) * 0.3
                };
            }

            case 'coffee': {
                const cTypes = ['coffee_bean', 'steam_curl', 'caramel_drop'];
                const cType = cTypes[Math.floor(Math.random() * cTypes.length)];
                return {
                    ...base,
                    type: cType,
                    color: ['#b45309', '#78350f', '#fcd34d', '#fffbeb'][Math.floor(Math.random() * 4)],
                    size: cType === 'coffee_bean' ? (Math.random() * 7 + 4) : (Math.random() * 5 + 2),
                    speedY: -Math.random() * 0.6 - 0.15,
                    speedX: (Math.random() - 0.5) * 0.25,
                    spinSpeed: (Math.random() - 0.5) * 0.02
                };
            }

            case 'fashion': {
                const fTypes = ['runway_facet', 'metallic_shard', 'luxury_glint'];
                const fType = fTypes[Math.floor(Math.random() * fTypes.length)];
                return {
                    ...base,
                    type: fType,
                    color: ['#fafafa', '#d4af37', '#e4e4e7', '#a1a1aa'][Math.floor(Math.random() * 4)],
                    size: Math.random() * 6 + 3,
                    speedY: (Math.random() - 0.5) * 0.4,
                    speedX: (Math.random() - 0.5) * 0.4
                };
            }

            case 'diwali':
            case 'royal':
                return {
                    ...base,
                    type: 'diya_sparkle',
                    color: ['#fbbf24', '#f59e0b', '#d4af37', '#ffd700'][Math.floor(Math.random() * 4)],
                    speedY: -Math.random() * 0.8 - 0.2, // rising warm diya ember
                    size: Math.random() * 4 + 2
                };

            case 'navratri':
                return {
                    ...base,
                    type: 'garba_disc',
                    color: ['#ec4899', '#f59e0b', '#8b5cf6', '#3b82f6'][Math.floor(Math.random() * 4)],
                    speedX: Math.cos(base.angle) * 0.7,
                    speedY: Math.sin(base.angle) * 0.7,
                    size: Math.random() * 7 + 3
                };

            case 'holi':
                return {
                    ...base,
                    type: 'color_splash',
                    color: ['#f43f5e', '#06b6d4', '#eab308', '#ec4899', '#10b981', '#a855f7'][Math.floor(Math.random() * 6)],
                    size: Math.random() * 9 + 3,
                    speedY: (Math.random() - 0.5) * 1.2,
                    speedX: (Math.random() - 0.5) * 1.2
                };

            case 'christmas':
            case 'winter_sale':
                return {
                    ...base,
                    type: 'snowflake',
                    color: 'rgba(255, 255, 255, 0.9)',
                    speedY: Math.random() * 1.2 + 0.5,
                    speedX: Math.sin(Math.random() * Math.PI) * 0.5,
                    size: Math.random() * 4.5 + 2
                };

            case 'new_year':
                return {
                    ...base,
                    type: 'firework_star',
                    color: ['#d4af37', '#60a5fa', '#f8fafc', '#fbbf24', '#e2e8f0'][Math.floor(Math.random() * 5)],
                    speedY: (Math.random() - 0.5) * 1.5,
                    speedX: (Math.random() - 0.5) * 1.5,
                    size: Math.random() * 5 + 2
                };

            case 'eid':
                return {
                    ...base,
                    type: 'crescent_star',
                    color: ['#10b981', '#34d399', '#d4af37', '#fef08a'][Math.floor(Math.random() * 4)],
                    speedY: -Math.random() * 0.4 - 0.1,
                    size: Math.random() * 5 + 2.5
                };

            case 'valentines':
                return {
                    ...base,
                    type: 'heart_spark',
                    color: ['#f43f5e', '#fb7185', '#fda4af', '#f472b6'][Math.floor(Math.random() * 4)],
                    speedY: -Math.random() * 0.8 - 0.2,
                    size: Math.random() * 6 + 3
                };

            case 'summer_sale':
                return {
                    ...base,
                    type: 'tropical_sun',
                    color: ['#f59e0b', '#fbbf24', '#38bdf8', '#10b981'][Math.floor(Math.random() * 4)],
                    speedY: -Math.random() * 0.6 - 0.1,
                    size: Math.random() * 6 + 3
                };

            case 'monsoon_sale':
                return {
                    ...base,
                    type: 'raindrop',
                    color: '#38bdf8',
                    speedY: Math.random() * 3 + 3,
                    speedX: -0.5,
                    size: Math.random() * 2.5 + 1
                };

            case 'flash_sale':
            case 'clearance':
                return {
                    ...base,
                    type: 'energy_spark',
                    color: ['#ef4444', '#f59e0b', '#eab308', '#dc2626'][Math.floor(Math.random() * 4)],
                    speedX: (Math.random() - 0.5) * 3,
                    speedY: (Math.random() - 0.5) * 3,
                    size: Math.random() * 4 + 1.5
                };

            case 'coffee': {
                const rand = Math.random();
                if (rand < 0.45) {
                    // 3D Roasted Whole Coffee Bean (Natural tumble, S-crease, realistic shading)
                    return {
                        ...base,
                        type: 'coffee_bean_3d',
                        size: Math.random() * 9 + 8,
                        speedY: Math.random() * 0.45 + 0.1,
                        speedX: (Math.random() - 0.5) * 0.35,
                        swayAngle: Math.random() * Math.PI * 2,
                        swaySpeed: Math.random() * 0.02 + 0.01,
                        spinSpeed: (Math.random() - 0.5) * 0.025,
                        opacity: Math.random() * 0.4 + 0.6,
                        color: ['#451a03', '#6b3310', '#321405', '#854316'][Math.floor(Math.random() * 4)]
                    };
                } else if (rand < 0.78) {
                    // Curving Rising Steam Wisp
                    return {
                        ...base,
                        type: 'steam_wisp_3d',
                        size: Math.random() * 24 + 18,
                        speedY: -Math.random() * 0.65 - 0.25,
                        speedX: (Math.random() - 0.5) * 0.25,
                        swayAngle: Math.random() * Math.PI * 2,
                        swaySpeed: Math.random() * 0.03 + 0.015,
                        opacity: Math.random() * 0.35 + 0.18
                    };
                } else {
                    // Golden Aroma Sparkle / Cocoa Dust
                    return {
                        ...base,
                        type: 'aroma_sparkle',
                        color: ['#fcd34d', '#f59e0b', '#ffd700', '#d97706'][Math.floor(Math.random() * 4)],
                        size: Math.random() * 3 + 1.5,
                        speedY: -Math.random() * 0.4 - 0.1,
                        speedX: (Math.random() - 0.5) * 0.2,
                        pulseSpeed: Math.random() * 0.04 + 0.02,
                        opacity: Math.random() * 0.5 + 0.4
                    };
                }
            }

            case 'janmashtami':
            case 'janmashtami_jewellery':
            case 'janmashtami_sweets':
            case 'janmashtami_clothing':
            case 'janmashtami_kids': {
                const rand = Math.random();
                if (rand < 0.45) {
                    // Primary Particle: Peacock Feather (Depth-aware, wind drift, multi-tone ocellus eye)
                    return {
                        ...base,
                        type: 'peacock_feather',
                        size: Math.random() * 12 + 10,
                        speedY: Math.random() * 0.45 + 0.15,
                        speedX: (Math.random() - 0.5) * 0.35,
                        swayAngle: Math.random() * Math.PI * 2,
                        swaySpeed: Math.random() * 0.02 + 0.01,
                        spinSpeed: (Math.random() - 0.5) * 0.015,
                        opacity: Math.random() * 0.45 + 0.5,
                        depth: Math.random() * 0.5 + 0.5
                    };
                } else if (rand < 0.75) {
                    // Secondary Particle: Lotus Flower Petal (Fluttering pink/cream drift)
                    return {
                        ...base,
                        type: 'lotus_petal',
                        color: ['#f472b6', '#fda4af', '#fbcfe8', '#fff1f2', '#f43f5e'][Math.floor(Math.random() * 5)],
                        size: Math.random() * 6 + 4,
                        speedY: Math.random() * 0.55 + 0.2,
                        speedX: (Math.random() - 0.5) * 0.4,
                        swayAngle: Math.random() * Math.PI * 2,
                        swaySpeed: Math.random() * 0.03 + 0.015,
                        spinSpeed: (Math.random() - 0.5) * 0.025,
                        opacity: Math.random() * 0.4 + 0.5
                    };
                } else if (rand < 0.90) {
                    // Ambient Particle: Golden Divine Light Particle (Soft slow glowing aura)
                    return {
                        ...base,
                        type: 'divine_sparkle',
                        color: ['#ffd700', '#fef08a', '#00e5ff', '#ffffff', '#e5c158'][Math.floor(Math.random() * 5)],
                        size: Math.random() * 3.5 + 1.5,
                        speedY: -Math.random() * 0.4 - 0.1,
                        speedX: (Math.random() - 0.5) * 0.25,
                        pulseSpeed: Math.random() * 0.04 + 0.02,
                        opacity: Math.random() * 0.5 + 0.4
                    };
                } else {
                    // Category-adapted specialized particles
                    if (this.theme === 'janmashtami_sweets') {
                        return {
                            ...base,
                            type: 'butter_drop',
                            color: '#fffdf0',
                            size: Math.random() * 4 + 2,
                            speedY: Math.random() * 0.6 + 0.2,
                            speedX: (Math.random() - 0.5) * 0.2
                        };
                    } else {
                        return {
                            ...base,
                            type: 'flute_glint',
                            color: ['#ffd700', '#00e5ff', '#ffffff'][Math.floor(Math.random() * 3)],
                            size: Math.random() * 4 + 2,
                            speedY: -Math.random() * 0.35 - 0.05,
                            speedX: (Math.random() - 0.5) * 0.2
                        };
                    }
                }
            }

            default:
                return {
                    ...base,
                    type: 'jewel_sparkle',
                    color: ['#ffd700', '#fef08a', '#d4af37', '#e5c158', '#b8860b'][Math.floor(Math.random() * 5)],
                    size: Math.random() * 3.5 + 1.5,
                    speedY: -Math.random() * 0.5 - 0.15
                };
        }
    }

    triggerWinCelebration(x, y) {
        if (this.isReducedMotion) return;
        const count = this.isMobile ? 40 : 80;
        const originX = x || (this.canvas ? this.canvas.width / 2 : window.innerWidth / 2);
        const originY = y || (this.canvas ? this.canvas.height / 2 : window.innerHeight / 2);

        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 8 + 3;
            this.celebrationParticles.push({
                x: originX,
                y: originY,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 2,
                gravity: 0.18,
                size: Math.random() * 6 + 2,
                color: this.getCelebrationColor(),
                alpha: 1,
                decay: Math.random() * 0.02 + 0.015,
                rotation: Math.random() * Math.PI * 2,
                spin: (Math.random() - 0.5) * 0.1
            });
        }
    }

    getCelebrationColor() {
        switch (this.theme) {
            case 'janmashtami':
            case 'janmashtami_jewellery':
            case 'janmashtami_sweets':
            case 'janmashtami_clothing':
            case 'janmashtami_kids':
                return ['#00e5ff', '#ffd700', '#3b185f', '#f472b6', '#00c49f', '#fef08a', '#ffffff'][Math.floor(Math.random() * 7)];
            case 'diwali':
            case 'royal':
            case 'luxury_black':
                return ['#ffd700', '#fef08a', '#d4af37', '#ffffff', '#f59e0b'][Math.floor(Math.random() * 5)];
            case 'holi':
                return ['#f43f5e', '#06b6d4', '#eab308', '#ec4899', '#10b981', '#8b5cf6'][Math.floor(Math.random() * 6)];
            case 'christmas':
                return ['#dc2626', '#16a34a', '#fef08a', '#ffffff', '#22c55e'][Math.floor(Math.random() * 5)];
            case 'new_year':
                return ['#d4af37', '#38bdf8', '#ffffff', '#f43f5e', '#a855f7'][Math.floor(Math.random() * 5)];
            case 'valentines':
                return ['#f43f5e', '#fda4af', '#fb7185', '#ffffff'][Math.floor(Math.random() * 4)];
            case 'neon':
            case 'electronics':
                return ['#06b6d4', '#a855f7', '#f43f5e', '#38bdf8', '#3b82f6'][Math.floor(Math.random() * 5)];
            case 'coffee':
                return ['#fcd34d', '#d97706', '#f59e0b', '#78350f', '#ffd700', '#ffffff', '#451a03'][Math.floor(Math.random() * 7)];
            default:
                return ['#f59e0b', '#10b981', '#3b82f6', '#ec4899', '#ffd700'][Math.floor(Math.random() * 5)];
        }
    }

    startAnimation() {
        if (this.animId) cancelAnimationFrame(this.animId);

        const render = () => {
            if (!this.ctx || !this.canvas) return;
            const w = this.canvas.width;
            const h = this.canvas.height;

            this.ctx.clearRect(0, 0, w, h);

            // Render Janmashtami Celestial Moon & Night Sky Atmosphere
            if (this.janmashtamiMoon) {
                const m = this.janmashtamiMoon;
                m.pulse += m.pulseSpeed;
                const currentRadius = m.radius + Math.sin(m.pulse) * 3;

                // 1. Wide Outer Ambient Lunar Aura
                const ambientGrad = this.ctx.createRadialGradient(m.x, m.y, currentRadius * 0.4, m.x, m.y, currentRadius * 3.5);
                ambientGrad.addColorStop(0, 'rgba(0, 229, 255, 0.18)');
                ambientGrad.addColorStop(0.4, 'rgba(59, 24, 95, 0.12)');
                ambientGrad.addColorStop(0.8, 'rgba(255, 215, 0, 0.05)');
                ambientGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
                this.ctx.fillStyle = ambientGrad;
                this.ctx.beginPath();
                this.ctx.arc(m.x, m.y, currentRadius * 3.5, 0, Math.PI * 2);
                this.ctx.fill();

                // 2. Glowing Moon Orb
                const moonGrad = this.ctx.createRadialGradient(m.x - currentRadius * 0.25, m.y - currentRadius * 0.25, currentRadius * 0.05, m.x, m.y, currentRadius);
                moonGrad.addColorStop(0, '#ffffff');
                moonGrad.addColorStop(0.45, '#fef9c3');
                moonGrad.addColorStop(0.85, '#e0f2fe');
                moonGrad.addColorStop(1, '#67e8f9');
                this.ctx.fillStyle = moonGrad;
                this.ctx.shadowBlur = 24;
                this.ctx.shadowColor = 'rgba(0, 229, 255, 0.65)';
                this.ctx.beginPath();
                this.ctx.arc(m.x, m.y, currentRadius, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.shadowBlur = 0;

                // 3. Subtle Distant Vrindavan Silhouette Landscape along the bottom
                this.ctx.fillStyle = 'rgba(4, 7, 24, 0.45)';
                this.ctx.beginPath();
                this.ctx.moveTo(0, h);
                this.ctx.lineTo(0, h - 35);
                this.ctx.quadraticCurveTo(w * 0.15, h - 55, w * 0.3, h - 30);
                this.ctx.quadraticCurveTo(w * 0.45, h - 60, w * 0.6, h - 35);
                this.ctx.quadraticCurveTo(w * 0.75, h - 50, w * 0.9, h - 30);
                this.ctx.lineTo(w, h - 40);
                this.ctx.lineTo(w, h);
                this.ctx.closePath();
                this.ctx.fill();
            }

            // Render Coffee Theme 3D Coffee Cup & Warm Ambient Backlighting
            if (this.coffeeCup) {
                const cup = this.coffeeCup;
                cup.steamPhase += 0.025;
                const cr = cup.radius;

                // 1. Warm Ambient Mocha Glow behind the wheel & hero
                const mochaAura = this.ctx.createRadialGradient(w * 0.5, h * 0.35, 10, w * 0.5, h * 0.35, Math.min(w, h) * 0.7);
                mochaAura.addColorStop(0, 'rgba(217, 119, 6, 0.18)');
                mochaAura.addColorStop(0.45, 'rgba(120, 53, 15, 0.12)');
                mochaAura.addColorStop(0.85, 'rgba(43, 18, 7, 0.06)');
                mochaAura.addColorStop(1, 'rgba(0, 0, 0, 0)');
                this.ctx.fillStyle = mochaAura;
                this.ctx.fillRect(0, 0, w, h);

                // 2. 3D Porcelain Saucer with Drop Shadow
                this.ctx.save();
                this.ctx.fillStyle = '#ffffff';
                this.ctx.shadowColor = 'rgba(0, 0, 0, 0.65)';
                this.ctx.shadowBlur = 14;
                this.ctx.beginPath();
                this.ctx.ellipse(cup.x, cup.y + cr * 0.44, cr * 0.92, cr * 0.32, 0, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.strokeStyle = '#d4af37';
                this.ctx.lineWidth = 1.4;
                this.ctx.stroke();
                this.ctx.shadowBlur = 0;

                // 3. 3D Porcelain Cup Body
                const cs = cr * 0.7;
                this.ctx.fillStyle = '#ffffff';
                this.ctx.beginPath();
                this.ctx.arc(cup.x, cup.y + cr * 0.08, cs, 0, Math.PI, false);
                this.ctx.lineTo(cup.x + cs, cup.y + cr * 0.08);
                this.ctx.lineTo(cup.x - cs, cup.y + cr * 0.08);
                this.ctx.closePath();
                this.ctx.fill();
                this.ctx.strokeStyle = '#d4af37';
                this.ctx.lineWidth = 1.4;
                this.ctx.stroke();

                // Cup Handle
                this.ctx.beginPath();
                this.ctx.arc(cup.x + cs * 0.95, cup.y + cr * 0.18, cs * 0.36, -Math.PI / 2, Math.PI / 2);
                this.ctx.strokeStyle = '#ffffff';
                this.ctx.lineWidth = 3.2;
                this.ctx.stroke();
                this.ctx.strokeStyle = '#d4af37';
                this.ctx.lineWidth = 1;
                this.ctx.stroke();

                // 4. Rich Dark Roast Espresso Surface
                this.ctx.fillStyle = '#2b1207';
                this.ctx.beginPath();
                this.ctx.ellipse(cup.x, cup.y + cr * 0.08, cs * 0.92, cs * 0.36, 0, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.strokeStyle = '#d97706';
                this.ctx.lineWidth = 1.8;
                this.ctx.stroke();

                // 5. Heart Latte Art Foam
                const hs = cs * 0.42;
                const hy = cup.y + cr * 0.08;
                this.ctx.fillStyle = '#fffbeb';
                this.ctx.shadowColor = 'rgba(255, 255, 255, 0.75)';
                this.ctx.shadowBlur = 6;
                this.ctx.beginPath();
                this.ctx.moveTo(cup.x, hy + hs * 0.75);
                this.ctx.bezierCurveTo(cup.x - hs * 1.2, hy + hs * 0.2, cup.x - hs * 1.1, hy - hs * 0.8, cup.x, hy - hs * 0.3);
                this.ctx.bezierCurveTo(cup.x + hs * 1.1, hy - hs * 0.8, cup.x + hs * 1.2, hy + hs * 0.2, cup.x, hy + hs * 0.75);
                this.ctx.fill();
                this.ctx.shadowBlur = 0;

                // 6. Rising Steam Trails
                for (let st = 0; st < 3; st++) {
                    const stX = cup.x + (st - 1) * 12;
                    const stPhase = cup.steamPhase + st * 1.2;
                    this.ctx.strokeStyle = `rgba(255, 255, 255, ${0.35 + Math.sin(stPhase) * 0.15})`;
                    this.ctx.lineWidth = 1.6;
                    this.ctx.shadowColor = 'rgba(252, 211, 77, 0.4)';
                    this.ctx.shadowBlur = 8;
                    this.ctx.beginPath();
                    this.ctx.moveTo(stX, hy - 4);
                    this.ctx.bezierCurveTo(stX + Math.sin(stPhase) * 10, hy - 25, stX - Math.cos(stPhase) * 10, hy - 50, stX + Math.sin(stPhase) * 14, hy - 75);
                    this.ctx.stroke();
                    this.ctx.shadowBlur = 0;
                }
                this.ctx.restore();
            }

            // Render Aurora Blobs
            if (this.theme === 'aurora' && this.blobs.length > 0) {
                for (let b of this.blobs) {
                    b.x += b.vx;
                    b.y += b.vy;
                    b.pulse += b.pulseSpeed;

                    if (b.x < -b.radius) b.x = w + b.radius;
                    if (b.x > w + b.radius) b.x = -b.radius;
                    if (b.y < -b.radius) b.y = h * 0.7;
                    if (b.y > h * 0.7) b.y = -b.radius;

                    const currentR = b.radius + Math.sin(b.pulse) * 25;
                    const grad = this.ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, currentR);
                    grad.addColorStop(0, b.color);
                    grad.addColorStop(1, 'rgba(0,0,0,0)');

                    this.ctx.fillStyle = grad;
                    this.ctx.beginPath();
                    this.ctx.arc(b.x, b.y, currentR, 0, Math.PI * 2);
                    this.ctx.fill();
                }
            }

            // Render Active Background Particles & 3D Shapes
            for (let p of this.particles) {
                p.x += p.speedX;
                p.y += p.speedY;
                p.angle += p.spinSpeed;

                if (p.x < 0) p.x = w;
                if (p.x > w) p.x = 0;
                if (p.y < 0) p.y = h;
                if (p.y > h) p.y = 0;

                this.ctx.save();
                this.ctx.translate(p.x, p.y);
                this.ctx.rotate(p.angle);
                this.ctx.globalAlpha = p.opacity;

                if (p.type === 'peacock_feather') {
                    // Procedural 3D Peacock Feather with Ocellus Eye & Vane Barbs
                    const s = p.size;
                    if (p.swayAngle !== undefined) {
                        p.swayAngle += p.swaySpeed || 0.02;
                        p.x += Math.sin(p.swayAngle) * 0.45;
                    }

                    // 1. Central Quill Shaft
                    this.ctx.strokeStyle = 'rgba(212, 175, 55, 0.85)';
                    this.ctx.lineWidth = 1.2;
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, s * 1.3);
                    this.ctx.quadraticCurveTo(s * 0.15, 0, 0, -s * 1.3);
                    this.ctx.stroke();

                    // 2. Lateral Vane Barbs (Peacock Green & Royal Blue wisps)
                    const numBarbs = 7;
                    for (let b = 1; b <= numBarbs; b++) {
                        const by = -s * 1.1 + (b * s * 2.1) / numBarbs;
                        const bw = Math.sin((b / numBarbs) * Math.PI) * s * 0.7;

                        this.ctx.strokeStyle = b % 2 === 0 ? 'rgba(0, 229, 255, 0.65)' : 'rgba(16, 185, 129, 0.65)';
                        this.ctx.lineWidth = 0.9;
                        this.ctx.beginPath();
                        this.ctx.moveTo(0, by);
                        this.ctx.quadraticCurveTo(bw * 0.6, by - s * 0.12, bw, by - s * 0.05);
                        this.ctx.moveTo(0, by);
                        this.ctx.quadraticCurveTo(-bw * 0.6, by - s * 0.12, -bw, by - s * 0.05);
                        this.ctx.stroke();
                    }

                    // 3. Peacock Feather Eye (Ocellus)
                    const eyeY = -s * 0.45;
                    const eyeR = s * 0.42;

                    // Bronze Gold outer ring
                    this.ctx.fillStyle = '#b45309';
                    this.ctx.beginPath();
                    this.ctx.ellipse(0, eyeY, eyeR * 1.1, eyeR * 1.25, 0, 0, Math.PI * 2);
                    this.ctx.fill();

                    // Peacock Teal / Cyan ring
                    this.ctx.fillStyle = '#00e5ff';
                    this.ctx.beginPath();
                    this.ctx.ellipse(0, eyeY, eyeR * 0.85, eyeR * 1.0, 0, 0, Math.PI * 2);
                    this.ctx.fill();

                    // Royal Violet ring
                    this.ctx.fillStyle = '#3b185f';
                    this.ctx.beginPath();
                    this.ctx.ellipse(0, eyeY, eyeR * 0.6, eyeR * 0.75, 0, 0, Math.PI * 2);
                    this.ctx.fill();

                    // Center Deep Indigo Pupil
                    this.ctx.fillStyle = '#060b1e';
                    this.ctx.beginPath();
                    this.ctx.ellipse(0, eyeY, eyeR * 0.35, eyeR * 0.48, 0, 0, Math.PI * 2);
                    this.ctx.fill();

                    // Specular Gold Glint
                    this.ctx.fillStyle = '#ffd700';
                    this.ctx.beginPath();
                    this.ctx.arc(eyeR * 0.08, eyeY - eyeR * 0.12, eyeR * 0.14, 0, Math.PI * 2);
                    this.ctx.fill();

                } else if (p.type === 'lotus_petal') {
                    // Soft Curved Lotus Flower Petal with Flutter
                    const ps = p.size;
                    if (p.swayAngle !== undefined) {
                        p.swayAngle += p.swaySpeed || 0.02;
                        p.x += Math.sin(p.swayAngle) * 0.4;
                    }
                    const grad = this.ctx.createLinearGradient(0, -ps, 0, ps);
                    grad.addColorStop(0, '#f43f5e');
                    grad.addColorStop(0.5, '#fda4af');
                    grad.addColorStop(1, '#ffffff');
                    this.ctx.fillStyle = grad;
                    this.ctx.shadowBlur = 8;
                    this.ctx.shadowColor = 'rgba(244, 63, 94, 0.4)';
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -ps);
                    this.ctx.bezierCurveTo(ps * 0.65, -ps * 0.35, ps * 0.65, ps * 0.55, 0, ps);
                    this.ctx.bezierCurveTo(-ps * 0.65, ps * 0.55, -ps * 0.65, -ps * 0.35, 0, -ps);
                    this.ctx.closePath();
                    this.ctx.fill();

                } else if (p.type === 'divine_sparkle') {
                    // 4-Point Golden Celestial Starflare
                    const ds = p.size;
                    this.ctx.fillStyle = p.color;
                    this.ctx.shadowBlur = 12;
                    this.ctx.shadowColor = '#00e5ff';
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -ds * 1.8);
                    this.ctx.lineTo(ds * 0.3, -ds * 0.3);
                    this.ctx.lineTo(ds * 1.8, 0);
                    this.ctx.lineTo(ds * 0.3, ds * 0.3);
                    this.ctx.lineTo(0, ds * 1.8);
                    this.ctx.lineTo(-ds * 0.3, ds * 0.3);
                    this.ctx.lineTo(-ds * 1.8, 0);
                    this.ctx.lineTo(-ds * 0.3, -ds * 0.3);
                    this.ctx.closePath();
                    this.ctx.fill();

                } else if (p.type === 'butter_drop') {
                    // 3D Butter Droplet
                    const bs = p.size;
                    this.ctx.fillStyle = '#fffdf0';
                    this.ctx.shadowBlur = 8;
                    this.ctx.shadowColor = 'rgba(255, 255, 255, 0.7)';
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -bs * 1.2);
                    this.ctx.bezierCurveTo(bs * 0.75, 0, bs * 0.75, bs, 0, bs);
                    this.ctx.bezierCurveTo(-bs * 0.75, bs, -bs * 0.75, 0, 0, -bs * 1.2);
                    this.ctx.closePath();
                    this.ctx.fill();

                } else if (p.type === 'flute_glint') {
                    // Stylized Golden Flute glint
                    const fs = p.size;
                    this.ctx.strokeStyle = '#ffd700';
                    this.ctx.lineWidth = 1.4;
                    this.ctx.shadowBlur = 10;
                    this.ctx.shadowColor = '#ffd700';
                    this.ctx.beginPath();
                    this.ctx.moveTo(-fs * 1.4, 0);
                    this.ctx.lineTo(fs * 1.4, 0);
                    this.ctx.stroke();
                    this.ctx.fillStyle = '#ffffff';
                    this.ctx.beginPath();
                    this.ctx.arc(-fs * 0.5, 0, 1.2, 0, Math.PI * 2);
                    this.ctx.arc(0, 0, 1.2, 0, Math.PI * 2);
                    this.ctx.arc(fs * 0.5, 0, 1.2, 0, Math.PI * 2);
                    this.ctx.fill();

                } else if (p.type === 'cube_edge') {
                    // 3D Metallic Isometric Cube Wireframe
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 1.3;
                    this.ctx.shadowBlur = 8;
                    this.ctx.shadowColor = 'rgba(243, 229, 171, 0.5)';
                    const s = p.size;
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -s);
                    this.ctx.lineTo(s * 0.86, -s * 0.5);
                    this.ctx.lineTo(0, 0);
                    this.ctx.lineTo(-s * 0.86, -s * 0.5);
                    this.ctx.closePath();
                    this.ctx.stroke();

                    this.ctx.beginPath();
                    this.ctx.moveTo(-s * 0.86, -s * 0.5);
                    this.ctx.lineTo(0, 0);
                    this.ctx.lineTo(0, s);
                    this.ctx.lineTo(-s * 0.86, s * 0.5);
                    this.ctx.closePath();
                    this.ctx.stroke();

                    this.ctx.beginPath();
                    this.ctx.moveTo(0, 0);
                    this.ctx.lineTo(s * 0.86, -s * 0.5);
                    this.ctx.lineTo(s * 0.86, s * 0.5);
                    this.ctx.lineTo(0, s);
                    this.ctx.closePath();
                    this.ctx.stroke();
                } else if (p.type === 'diamond_facet' || p.type === 'runway_facet') {
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 1.4;
                    this.ctx.shadowBlur = 8;
                    this.ctx.shadowColor = p.color;
                    this.ctx.strokeRect(-p.size / 2, -p.size / 2, p.size, p.size);
                } else if (p.type === 'pearl_sphere') {
                    // 3D Pearl Sphere with radial gradient
                    const grad = this.ctx.createRadialGradient(-p.size * 0.3, -p.size * 0.3, p.size * 0.1, 0, 0, p.size);
                    grad.addColorStop(0, '#ffffff');
                    grad.addColorStop(0.6, '#f1f5f9');
                    grad.addColorStop(1, '#cbd5e1');
                    this.ctx.fillStyle = grad;
                    this.ctx.shadowBlur = 10;
                    this.ctx.shadowColor = 'rgba(212, 175, 55, 0.35)';
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, p.size, 0, Math.PI * 2);
                    this.ctx.fill();
                } else if (p.type === 'coffee_bean_3d' || p.type === 'coffee_bean') {
                    // 3D Roasted Whole Coffee Bean with Natural Tumble, Radial Shading, & S-Crease
                    const s = p.size;
                    if (p.swayAngle !== undefined) {
                        p.swayAngle += p.swaySpeed || 0.02;
                        p.x += Math.sin(p.swayAngle) * 0.35;
                    }

                    // 1. 3D Bean Body with Radial Depth Shading
                    const grad = this.ctx.createRadialGradient(-s * 0.25, -s * 0.25, s * 0.1, 0, 0, s);
                    grad.addColorStop(0, '#78350f');
                    grad.addColorStop(0.38, p.color || '#451a03');
                    grad.addColorStop(0.85, '#2b1207');
                    grad.addColorStop(1, '#140803');
                    this.ctx.fillStyle = grad;
                    this.ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
                    this.ctx.shadowBlur = 8;
                    this.ctx.beginPath();
                    this.ctx.ellipse(0, 0, s, s * 0.68, 0, 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.shadowBlur = 0;

                    // 2. Specular Golden Rim
                    this.ctx.strokeStyle = 'rgba(217, 119, 6, 0.5)';
                    this.ctx.lineWidth = 1.0;
                    this.ctx.stroke();

                    // 3. Center S-Curve Roasted Crease Groove
                    this.ctx.strokeStyle = '#0d0401';
                    this.ctx.lineWidth = 1.6;
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -s * 0.55);
                    this.ctx.bezierCurveTo(s * 0.2, -s * 0.18, -s * 0.2, s * 0.18, 0, s * 0.55);
                    this.ctx.stroke();

                    // 4. Crease Golden Highlight Edge
                    this.ctx.strokeStyle = 'rgba(252, 211, 77, 0.5)';
                    this.ctx.lineWidth = 0.8;
                    this.ctx.beginPath();
                    this.ctx.moveTo(1, -s * 0.5);
                    this.ctx.bezierCurveTo(s * 0.2 + 1, -s * 0.18, -s * 0.2 + 1, s * 0.18, 1, s * 0.5);
                    this.ctx.stroke();

                } else if (p.type === 'steam_wisp_3d') {
                    // Rising Translucent Steam Wisp
                    const sw = p.size;
                    if (p.swayAngle !== undefined) {
                        p.swayAngle += p.swaySpeed || 0.025;
                        p.x += Math.sin(p.swayAngle) * 0.45;
                    }
                    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
                    this.ctx.lineWidth = 1.6;
                    this.ctx.shadowColor = 'rgba(252, 211, 77, 0.3)';
                    this.ctx.shadowBlur = 6;
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, sw * 0.6);
                    this.ctx.bezierCurveTo(sw * 0.4, 0, -sw * 0.4, -sw * 0.4, 0, -sw * 0.8);
                    this.ctx.stroke();
                    this.ctx.shadowBlur = 0;

                } else if (p.type === 'aroma_sparkle') {
                    // Golden Aroma Sparkle
                    const as = p.size;
                    this.ctx.fillStyle = p.color || '#fcd34d';
                    this.ctx.shadowColor = '#d97706';
                    this.ctx.shadowBlur = 8;
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, as, 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.shadowBlur = 0;
                } else if (p.type === 'cloche_dome') {
                    // 3D Gourmet Cloche Dome
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 1.5;
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, p.size, Math.PI, 0, false);
                    this.ctx.lineTo(p.size, 0);
                    this.ctx.lineTo(-p.size, 0);
                    this.ctx.stroke();
                } else if (p.type === 'microchip') {
                    // 3D Microchip Geometry
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 1.4;
                    this.ctx.strokeRect(-p.size, -p.size, p.size * 2, p.size * 2);
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -p.size);
                    this.ctx.lineTo(0, p.size);
                    this.ctx.moveTo(-p.size, 0);
                    this.ctx.lineTo(p.size, 0);
                    this.ctx.stroke();
                } else if (p.type === 'crescent_star') {
                    // 3D Crescent Moon
                    this.ctx.fillStyle = p.color;
                    this.ctx.shadowBlur = 10;
                    this.ctx.shadowColor = p.color;
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, p.size, 0, Math.PI * 2, false);
                    this.ctx.arc(p.size * 0.4, -p.size * 0.3, p.size * 0.85, 0, Math.PI * 2, true);
                    this.ctx.fill();
                } else if (p.type === 'aurora_sphere') {
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 1.5;
                    this.ctx.shadowBlur = 12;
                    this.ctx.shadowColor = p.color;
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, p.size, 0, Math.PI * 2);
                    this.ctx.stroke();
                    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
                    this.ctx.fill();
                } else if (p.type === 'glass_prism' || p.type === 'cyber_hex') {
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 1.4;
                    this.ctx.shadowBlur = 10;
                    this.ctx.shadowColor = p.color;
                    this.ctx.beginPath();
                    for (let a = 0; a < 6; a++) {
                        const angle = (a * Math.PI) / 3;
                        const px = Math.cos(angle) * p.size;
                        const py = Math.sin(angle) * p.size;
                        if (a === 0) this.ctx.moveTo(px, py);
                        else this.ctx.lineTo(px, py);
                    }
                    this.ctx.closePath();
                    this.ctx.stroke();
                } else if (p.type === 'raindrop') {
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 1.5;
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, 0);
                    this.ctx.lineTo(-2, 10);
                    this.ctx.stroke();
                } else if (p.type === 'heart_spark') {
                    this.ctx.fillStyle = p.color;
                    this.ctx.beginPath();
                    this.ctx.arc(-2, -2, p.size / 2, 0, Math.PI * 2);
                    this.ctx.arc(2, -2, p.size / 2, 0, Math.PI * 2);
                    this.ctx.lineTo(0, p.size);
                    this.ctx.closePath();
                    this.ctx.fill();
                } else if (p.type === 'garba_disc') {
                    this.ctx.strokeStyle = p.color;
                    this.ctx.lineWidth = 2;
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, p.size, 0, Math.PI * 2);
                    this.ctx.stroke();
                } else if (p.type === 'jewel_sparkle' || p.type === 'diya_sparkle') {
                    this.ctx.fillStyle = p.color;
                    this.ctx.shadowBlur = 12;
                    this.ctx.shadowColor = '#ffd700';
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, -p.size * 1.8);
                    this.ctx.lineTo(p.size * 0.4, -p.size * 0.4);
                    this.ctx.lineTo(p.size * 1.8, 0);
                    this.ctx.lineTo(p.size * 0.4, p.size * 0.4);
                    this.ctx.lineTo(0, p.size * 1.8);
                    this.ctx.lineTo(-p.size * 0.4, p.size * 0.4);
                    this.ctx.lineTo(-p.size * 1.8, 0);
                    this.ctx.lineTo(-p.size * 0.4, -p.size * 0.4);
                    this.ctx.closePath();
                    this.ctx.fill();
                } else {
                    this.ctx.fillStyle = p.color;
                    this.ctx.shadowBlur = 8;
                    this.ctx.shadowColor = p.color;
                    this.ctx.beginPath();
                    this.ctx.arc(0, 0, p.size, 0, Math.PI * 2);
                    this.ctx.fill();
                }

                this.ctx.restore();
            }

            // Render Celebration Particles
            for (let i = this.celebrationParticles.length - 1; i >= 0; i--) {
                const cp = this.celebrationParticles[i];
                cp.x += cp.vx;
                cp.y += cp.vy;
                cp.vy += cp.gravity;
                cp.rotation += cp.spin;
                cp.alpha -= cp.decay;

                if (cp.alpha <= 0) {
                    this.celebrationParticles.splice(i, 1);
                    continue;
                }

                this.ctx.save();
                this.ctx.translate(cp.x, cp.y);
                this.ctx.rotate(cp.rotation);
                this.ctx.globalAlpha = cp.alpha;
                this.ctx.fillStyle = cp.color;
                this.ctx.fillRect(-cp.size / 2, -cp.size / 2, cp.size, cp.size);
                this.ctx.restore();
            }

            if (!this.isReducedMotion) {
                this.animId = requestAnimationFrame(render);
            }
        };

        if (!this.isReducedMotion) {
            this.animId = requestAnimationFrame(render);
        }
    }

    setMode(mode) {
        this.mode = mode || 'dark';
        document.body.setAttribute('data-mode', this.mode);
        document.documentElement.setAttribute('data-mode', this.mode);
        localStorage.setItem('shop_panel_mode', this.mode);
        if (this.canvas) {
            this.canvas.style.opacity = this.mode === 'light' ? '0.35' : '0.85';
        }
        this.createDecorations();
    }

    applyTheme(themeId, overrides = {}) {
        this.theme = themeId || 'royal';
        document.body.setAttribute('data-theme', this.theme);
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('shop_panel_theme', this.theme);
        if (overrides.intensity) {
            document.body.setAttribute('data-intensity', overrides.intensity);
            this.intensity = overrides.intensity;
        } else {
            this.intensity = document.body.getAttribute('data-intensity') || 'balanced';
        }

        if (overrides.primary_color) {
            document.body.style.setProperty('--color-primary', overrides.primary_color);
        }
        if (overrides.secondary_color) {
            document.body.style.setProperty('--color-secondary', overrides.secondary_color);
        }
        if (overrides.accent_color) {
            document.body.style.setProperty('--color-accent', overrides.accent_color);
        }
        if (overrides.background_color) {
            document.body.style.setProperty('--bg-main', overrides.background_color);
        }
        if (overrides.text_color) {
            document.body.style.setProperty('--text-primary', overrides.text_color);
        }
        if (overrides.font_family) {
            document.body.className = document.body.className.replace(/font-\w+/g, '') + ' font-' + overrides.font_family;
        }

        this.createDecorations();
        if (window.activeSpinWheelInstance) {
            window.activeSpinWheelInstance.draw();
        }
    }
}

// Auto-initialize Theme Engine globally on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.ThemeEngineInstance = new ThemeEngine();
});
