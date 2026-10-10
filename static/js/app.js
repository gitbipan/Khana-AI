/**
 * PoshanAI (पोषण AI) Interactive Single-Page Application Logic
 * Organic Green Theme, Weekly Budget Tracker, AI Diet Planner, Checklist Tracking, & 1-Month Doctor PDF Export
 */

// Application State
const state = {
    user: null,
    lang: 'ne', // 'ne' or 'en'
    currentScannerMode: 'samples',
    selectedSampleFilename: 'dal_bhat_tarkari.jpg',
    currentMealAnalysis: null,
    currentDietPlan: null,
    plannerCustomItems: [],
    dietHistory: [],
    historyFilterDays: 30,
    samplesList: [],
    allFoods: [],
    cameraStream: null,
    charts: {
        macrosPie: null,
        caloriesBar: null,
        micronutrientsBar: null,
        weeklyBudget: null
    }
};

// Bilingual Strings Dictionary
const i18n = {
    ne: {
        appTitle: "PoshanAI : पोषण AI",
        loginTitle: "🍲 PoshanAI : पोषण AI",
        loginSubtitle: "नेपाली खानाको तस्विरबाट क्यालोरी पहिचान र BMR अनुसार कुपोषण रोकथाम परामर्श",
        loginLangLabel: "English मा बदल्नुहोस्",
        navLangTag: "English",
        menuProfile: "प्रोफाइल",
        drawerTitle: "स्वास्थ्य प्रोफाइल (Profile)",
        metabolicTitle: "दैनिक ऊर्जा आवश्यकता (Metabolism)",
        navTitle: "द्रुत नेभिगेसन (Quick Links)",
        btnEditProfile: "शारीरिक विवरण सम्पादन गर्नुहोस्",
        btnLogout: "लगआउट (Sign Out)",
        dashGreeting: "नमस्ते, ",
        dashBadge: "🌱 व्यक्तिगत पोषण केन्द्र",
        dashBtnScan: "खाना स्क्यान गर्नुहोस्",
        dashBtnChat: "पोषण साथीसँग सोध्नुहोस्",
        infoPlateTitle: "नेपाली सन्तुलित थाली (The Balanced Nepali Plate)",
        infoPlateSub: "कुपोषण र मधुमेह रोक्न वैज्ञानिक रूपमा सिफारिस गरिएको नेपाली थालीको आदर्श अनुपात:",
        infoMeterTitle: "कुपोषण जोखिम मिटर (WHO South Asian Cutoffs)",
        infoMeterSub: "नेपालमा दक्षिण एसियाली मापदण्ड अनुसार १८.५ भन्दा कमलाई कम तौल र २३.० भन्दा माथिलाई बढी तौल मानिन्छ।",
        scanTitle: "📸 नेपाली खाना स्क्यानर तथा पोषक तत्व विश्लेषण",
        scanSub: "खानाको फोटो खिच्नुहोस्, अपलोड गर्नुहोस् वा तलका नमुना तस्विरबाट तुरुन्तै AI विश्लेषण हेर्नुहोस्।",
        tabSamples: "नमुना परिकारहरू (Quick Samples)",
        tabUpload: "फोटो अपलोड (Upload)",
        tabCamera: "क्यामेरा स्न्याप (Camera)",
        samplePickLbl: "कुनै एक नमुना नेपाली खाना रोज्नुहोस्:",
        uploadPrompt: "खानाको फोटो अपलोड गर्न यहाँ क्लिक गर्नुहोस्",
        btnAnalyze: "🔍 AI द्वारा खाना विश्लेषण गर्नुहोस्",
        analyzingMsg: "AI द्वारा नेपाली परिकार पहिचान गरिँदैछ...",
        detectedTitle: "🥗 पहिचान गरिएका परिकारहरू",
        chartPieTitle: "🥧 म्याक्रो अनुपात (Carbs vs Protein vs Fat)",
        chartBarTitle: "📊 क्यालोरी र BMR तुलना (Energy Comparison)",
        chartMicroTitle: "🥦 सूक्ष्म पोषक तत्व पूर्ति % (Micronutrient RDA Fulfillment)",
        chatTitle: "पोषण साथी (Poshan Saathi AI)",
        chatSub: "नेपाली खाना र कुपोषण रोकथाम परामर्शदाता",
        chatGreeting: "🙏 <strong>नमस्ते! म पोषण साथी हुँ।</strong><br>म नेपाली खानाको क्यालोरी, प्रोटिन, BMR सन्तुलन र कुपोषण हटाउने उपायहरू बताउन तयार छु। तपाईं आफ्नो खाना, BMR वा कुनै पनि स्वास्थ्य प्रश्न सोध्न सक्नुहुन्छ!",
        expTitle: "📖 रैथाने नेपाली खाना पोषण ज्ञानकोष",
        expSub: "नेपालका ४०+ मौलिक परिकारहरूको क्यालोरी, प्रोटिन, भिटामिन तथा कुपोषण निवारण महत्त्व (DFTQC Nepal Reference)."
    },
    en: {
        appTitle: "PoshanAI - Nepali Nutrition AI",
        loginTitle: "🍲 PoshanAI - Nepali Nutrition AI",
        loginSubtitle: "Computer Vision Nepali Food Recognition & Clinical BMR Malnutrition Advisory",
        loginLangLabel: "नेपालीमा बदल्नुहोस्",
        navLangTag: "नेपाली",
        menuProfile: "Profile",
        drawerTitle: "Health Profile & Metrics",
        metabolicTitle: "Daily Metabolic Energy Budget",
        navTitle: "Quick Navigation",
        btnEditProfile: "Edit Health Metrics",
        btnLogout: "Sign Out",
        dashGreeting: "Welcome, ",
        dashBadge: "🌱 Personal Nutrition Center",
        dashBtnScan: "Scan a Meal Photo",
        dashBtnChat: "Ask Poshan Saathi AI",
        infoPlateTitle: "The Balanced Nepali Plate (सन्तुलित थाली)",
        infoPlateSub: "Clinically recommended proportions to prevent stunting, PEM, and diabetes:",
        infoMeterTitle: "Malnutrition Risk Scale (WHO South Asian Cutoffs)",
        infoMeterSub: "South Asian clinical standard: <18.5 indicates underweight/wasting risk; 18.5-22.9 is normal.",
        scanTitle: "📸 Nepali Food Scanner & Nutrient Analysis",
        scanSub: "Take a camera snap, upload a plate image, or select a pre-loaded sample dish for instant AI analysis.",
        tabSamples: "Quick Test Samples",
        tabUpload: "Upload Image",
        tabCamera: "Camera Snapshot",
        samplePickLbl: "Select an authentic Nepali sample dish:",
        uploadPrompt: "Click here to upload a food image",
        btnAnalyze: "🔍 Analyze Meal with PoshanAI",
        analyzingMsg: "Analyzing plate with Gemma multimodal vision...",
        detectedTitle: "🥗 Identified Plate Components",
        chartPieTitle: "🥧 Macronutrient Energy Ratio (Carbs vs Protein vs Fat)",
        chartBarTitle: "📊 Energy Intake vs BMR vs TDEE Comparison",
        chartMicroTitle: "🥦 Micronutrient RDA Fulfillment %",
        chatTitle: "Poshan Saathi (AI Nutritionist)",
        chatSub: "Nepali Diet & Malnutrition Consultant",
        chatGreeting: "🙏 <strong>Namaste! I am Poshan Saathi.</strong><br>I am ready to evaluate your meals, check your BMR/TDEE balance, and recommend affordable, indigenous superfoods. Ask me any nutrition question!",
        expTitle: "📖 Authentic Nepali Foods Encyclopaedia",
        expSub: "Verified nutritional metrics for 40+ traditional dishes based on the Food Composition Table for Nepal."
    }
};

// =========================================================
// INITIALIZATION
// =========================================================
document.addEventListener('DOMContentLoaded', async () => {
    const savedUser = localStorage.getItem('poshan_user');
    const savedLang = localStorage.getItem('poshan_lang');
    if (savedLang) state.lang = savedLang;

    if (savedUser) {
        try {
            state.user = JSON.parse(savedUser);
            if (state.user && state.user.name) {
                fetch(`/api/profile/get?username=${encodeURIComponent(state.user.name)}`)
                    .then(r => r.json())
                    .then(d => {
                        if (d.status === 'success' && d.profile) {
                            state.user.profile = d.profile;
                            state.user.assessment = d.assessment;
                            localStorage.setItem('poshan_user', JSON.stringify(state.user));
                            updateUserInterface();
                        }
                    }).catch(() => {});
            }
            showAppScreen();
        } catch (e) {
            showLoginScreen();
        }
    } else {
        showLoginScreen();
    }

    await loadSamples();
    await loadFoods();
    await loadPlannerCustomItems();
    populateManualFoodPresets();
    applyLanguage();
    lucide.createIcons();
});

// =========================================================
// SCREEN ROUTING & LOGIN
// =========================================================
function showLoginScreen() {
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('app-screen').classList.add('hidden');
}

function showAppScreen() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('app-screen').classList.remove('hidden');
    updateUserInterface();
    loadPlannerCustomItems();
    switchNav('dashboard');
    lucide.createIcons();
}

function handleLogout() {
    localStorage.removeItem('poshan_user');
    state.user = null;
    toggleHamburgerDrawer(false);
    showLoginScreen();
}

async function handleLoginSubmit(event) {
    event.preventDefault();
    const payload = {
        name: document.getElementById('login-name').value.trim() || 'अतिथि प्रयोगकर्ता',
        age_years: parseInt(document.getElementById('login-age').value) || 24,
        sex: document.getElementById('login-sex').value,
        height_cm: parseFloat(document.getElementById('login-height').value) || 170.0,
        weight_kg: parseFloat(document.getElementById('login-weight').value) || 62.0,
        activity_level: document.getElementById('login-activity').value,
        goal: document.getElementById('login-goal').value
    };

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            state.user = {
                name: data.user_name,
                profile: data.profile,
                assessment: data.assessment
            };
            localStorage.setItem('poshan_user', JSON.stringify(state.user));
            showAppScreen();
        }
    } catch (e) {
        alert('लगइन असफल भयो। कृपया सर्भर सुरु छ कि छैन जाँच्नुहोस्।');
    }
}

async function handleQuickDemoLogin() {
    const payload = {
        name: "बिपान (Bipan)",
        age_years: 23,
        sex: "male",
        height_cm: 172.0,
        weight_kg: 64.0,
        activity_level: "moderate",
        goal: "maintain"
    };

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            state.user = {
                name: data.user_name,
                profile: data.profile,
                assessment: data.assessment
            };
            localStorage.setItem('poshan_user', JSON.stringify(state.user));
            showAppScreen();
        }
    } catch (e) {
        alert('डेमो लगइन असफल भयो।');
    }
}

// =========================================================
// NAVIGATION SWITCHER
// =========================================================
function switchNav(navId) {
    const views = ['dashboard', 'planner', 'history', 'scanner', 'chat', 'explorer'];
    views.forEach(v => {
        const sec = document.getElementById(`view-${v}`);
        if (sec) sec.classList.add('hidden');
        const btn = document.getElementById(`nav-btn-${v}`);
        if (btn) btn.classList.remove('active');
    });

    const activeSec = document.getElementById(`view-${navId}`);
    if (activeSec) activeSec.classList.remove('hidden');

    const activeBtn = document.getElementById(`nav-btn-${navId}`);
    if (activeBtn) activeBtn.classList.add('active');

    // Trigger section-specific loaders
    if (navId === 'dashboard') {
        renderWeeklyBudgetChart();
    } else if (navId === 'planner') {
        loadPlannerCustomItems().then(() => {
            if (!state.currentDietPlan) {
                generateDietPlan();
            } else {
                renderDietPlan(state.currentDietPlan);
            }
        });
    } else if (navId === 'history') {
        loadDietHistory(state.historyFilterDays);
    }

    lucide.createIcons();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =========================================================
// HAMBURGER PROFILE DRAWER & PROFILE UPDATES
// =========================================================
function toggleHamburgerDrawer(forceState) {
    const panel = document.getElementById('drawer-panel');
    const backdrop = document.getElementById('drawer-backdrop');
    const isOpen = panel.classList.contains('open');
    const nextState = forceState !== undefined ? forceState : !isOpen;

    if (nextState) {
        panel.classList.add('open');
        backdrop.classList.add('open');
    } else {
        panel.classList.remove('open');
        backdrop.classList.remove('open');
    }
}

function updateUserInterface() {
    if (!state.user) return;
    const { name, profile, assessment } = state.user;
    const isNe = state.lang === 'ne';

    // Dashboard Greeting & Text
    document.getElementById('dash-greeting').textContent = `${isNe ? 'नमस्ते, ' : 'Welcome, '}${name}!`;
    document.getElementById('dash-bmr-text').textContent = `${assessment.bmr_kcal} kcal`;
    document.getElementById('dash-target-text').textContent = `${assessment.target_daily.calories} kcal`;
    document.getElementById('dash-pro-text').textContent = `${assessment.target_daily.protein_g}g`;

    // 4 Metric cards
    document.getElementById('stat-bmi').textContent = assessment.bmi;
    document.getElementById('stat-bmi-cat').textContent = isNe ? assessment.bmi_category.category_ne : assessment.bmi_category.category_en;
    document.getElementById('stat-bmr').textContent = assessment.bmr_kcal;
    document.getElementById('stat-tdee').textContent = assessment.tdee_kcal;
    document.getElementById('stat-protein').textContent = assessment.target_daily.protein_g;

    // Hamburger drawer items
    document.getElementById('drawer-user-name').textContent = name;
    document.getElementById('drawer-user-initial').textContent = name.charAt(0);
    document.getElementById('drawer-user-specs').textContent = 
        `${profile.age_years} ${isNe ? 'वर्ष' : 'yrs'} • ${profile.sex === 'male' ? (isNe ? 'पुरुष' : 'Male') : (isNe ? 'महिला' : 'Female')} • ${profile.height_cm} cm • ${profile.weight_kg} kg`;
    document.getElementById('drawer-bmi-badge').textContent = `${assessment.bmi} (${isNe ? assessment.bmi_category.category_ne : assessment.bmi_category.category_en})`;
    document.getElementById('drawer-bmr-val').textContent = `${assessment.bmr_kcal} kcal`;
    document.getElementById('drawer-tdee-val').textContent = `${assessment.tdee_kcal} kcal`;
    document.getElementById('drawer-target-cal').textContent = `${assessment.target_daily.calories} kcal`;
    document.getElementById('drawer-target-pro').textContent = `${assessment.target_daily.protein_g} g`;
    const waterEl = document.getElementById('drawer-water-val');
    if (waterEl) waterEl.textContent = `${assessment.water_liters} L`;

    // Render dashboard weekly chart
    renderWeeklyBudgetChart();
}

// Edit Profile Modal
function openEditProfileModal() {
    if (!state.user) return;
    document.getElementById('edit-height').value = state.user.profile.height_cm;
    document.getElementById('edit-weight').value = state.user.profile.weight_kg;
    document.getElementById('edit-activity').value = state.user.profile.activity_level;
    document.getElementById('edit-goal').value = state.user.profile.goal;
    document.getElementById('modal-edit-profile').classList.remove('hidden');
}

function closeEditProfileModal() {
    document.getElementById('modal-edit-profile').classList.add('hidden');
}

async function handleEditProfileSubmit(event) {
    event.preventDefault();
    if (!state.user) return;

    const updatedProfile = {
        age_years: state.user.profile.age_years,
        sex: state.user.profile.sex,
        height_cm: parseFloat(document.getElementById('edit-height').value),
        weight_kg: parseFloat(document.getElementById('edit-weight').value),
        activity_level: document.getElementById('edit-activity').value,
        goal: document.getElementById('edit-goal').value
    };

    try {
        const res = await fetch('/api/profile/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedProfile)
        });
        const data = await res.json();
        if (data.status === 'success') {
            state.user.profile = data.profile;
            state.user.assessment = data.assessment;
            localStorage.setItem('poshan_user', JSON.stringify(state.user));
            closeEditProfileModal();
            updateUserInterface();
            toggleHamburgerDrawer(false);
            // Refresh planner & weekly chart with new metrics
            generateDietPlan();
            renderWeeklyBudgetChart();
        }
    } catch (e) {
        alert('विवरण अद्यावधिक हुन सकेन।');
    }
}

// =========================================================
// HOMEPAGE FEATURE: PAST WEEK CALORIE BUDGET CHART
// =========================================================
async function renderWeeklyBudgetChart() {
    const canvas = document.getElementById('chart-weekly-budget');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const userName = state.user ? state.user.name : 'default';
    const tdee = state.user ? state.user.assessment.tdee_kcal : 2449;

    try {
        const res = await fetch(`/api/history/weekly-tracker?user_id=${encodeURIComponent(userName)}&target_kcal=${tdee}`);
        const data = await res.json();
        if (data.status !== 'success') return;

        const stats = data.stats;
        const days = stats.days;
        const isNe = state.lang === 'ne';

        // Update stats summary row
        document.getElementById('stat-weekly-target').textContent = `${stats.daily_target_kcal} kcal`;
        document.getElementById('stat-weekly-avg').textContent = `${stats.weekly_avg_daily_kcal} kcal`;
        document.getElementById('stat-weekly-on').textContent = `${stats.on_target_days} ${isNe ? 'दिन' : 'days'}`;
        document.getElementById('stat-weekly-dev').textContent = 
            `${stats.overshot_days} ${isNe ? 'दिन बढी' : 'overshot'} / ${stats.undershot_days} ${isNe ? 'दिन कम' : 'undershot'}`;

        const labels = days.map(d => `${isNe ? d.day_ne : d.day_en} (${d.date.slice(5)})`);
        const consumedValues = days.map(d => d.calories);
        const lowerRangeValues = days.map(d => d.lower_target || Math.round(stats.daily_target_kcal * 0.90));
        const upperRangeValues = days.map(d => d.upper_target || Math.round(stats.daily_target_kcal * 1.10));

        // Bar colors depending on range status:
        // In Range = emerald green, Undershot (< lower range) = sky blue, Overshot (> upper range) = warm orange
        const barColors = days.map(d => {
            if (d.status === 'overshot') return '#ea580c'; // Warm orange
            if (d.status === 'undershot') return '#0284c7'; // Sky blue
            if (d.status === 'no_data') return '#cbd5e1'; // Slate gray
            return '#16a34a'; // Emerald green (In Target Range)
        });

        if (state.charts.weeklyBudget) {
            state.charts.weeklyBudget.destroy();
        }

        state.charts.weeklyBudget = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        type: 'line',
                        label: isNe ? 'तल्लो सीमा (Undershoot Limit)' : 'Lower Limit (Undershoot)',
                        data: lowerRangeValues,
                        borderColor: '#0284c7',
                        borderWidth: 1.5,
                        borderDash: [5, 4],
                        pointRadius: 2,
                        pointBackgroundColor: '#0284c7',
                        fill: false,
                        tension: 0.1,
                        order: 1
                    },
                    {
                        type: 'line',
                        label: isNe ? 'माथिल्लो सीमा (Overshoot Limit)' : 'Upper Limit (Overshoot)',
                        data: upperRangeValues,
                        borderColor: '#ea580c',
                        borderWidth: 1.5,
                        borderDash: [5, 4],
                        pointRadius: 2,
                        pointBackgroundColor: '#ea580c',
                        fill: '-1', // Fills area between Lower and Upper to show the Target Range band!
                        backgroundColor: 'rgba(16, 185, 129, 0.12)',
                        tension: 0.1,
                        order: 2
                    },
                    {
                        type: 'bar',
                        label: isNe ? 'वास्तविक खाएको क्यालोरी' : 'Consumed Calories',
                        data: consumedValues,
                        backgroundColor: barColors,
                        borderRadius: 8,
                        barThickness: 32,
                        order: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        ticks: {
                            callback: v => v + ' kcal',
                            font: { size: 10 }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 11, weight: '600' } }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { boxWidth: 12, font: { size: 11 } }
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: (ctx) => {
                                if (ctx.dataset.type !== 'bar') return '';
                                const day = days[ctx.dataIndex];
                                const cal = day.calories;
                                const upper = day.upper_target || Math.round(stats.daily_target_kcal * 1.10);
                                const lower = day.lower_target || Math.round(stats.daily_target_kcal * 0.90);
                                let statusMsg = isNe ? 'सन्तुलित (In Target Range)' : 'Balanced (In Range)';
                                if (cal > upper) statusMsg = isNe ? `बढी (Overshoot: +${cal - upper} kcal)` : `Overshot (+${cal - upper} kcal)`;
                                else if (cal < lower && cal > 0) statusMsg = isNe ? `कम (Undershoot: -${lower - cal} kcal)` : `Undershot (-${lower - cal} kcal)`;
                                else if (cal === 0) statusMsg = isNe ? 'डाटा छैन (No Data)' : 'No Data';

                                return [
                                    `${isNe ? 'स्थिति' : 'Status'}: ${statusMsg}`,
                                    `${isNe ? 'सन्तुलित दायरा' : 'Target Range'}: ${lower} - ${upper} kcal`,
                                    `${isNe ? 'प्रोटिन' : 'Protein'}: ${day.protein_g}g (${day.meal_count} ${isNe ? 'छाक' : 'meals'})`
                                ];
                            }
                        }
                    }
                }
            }
        });

    } catch (e) {
        console.error('Failed to load weekly tracker:', e);
    }
}

// =========================================================
// FEATURE 1: AUTOMATIC NEPALI DIET PLANNER & INDIVIDUAL FOOD ITEM CHECKLISTS
// =========================================================
async function loadPlannerCustomItems() {
    const userName = state.user ? state.user.name : 'default';
    const today = new Date().toISOString().slice(0, 10);
    try {
        const res = await fetch(`/api/planner/items?user_id=${encodeURIComponent(userName)}&date=${today}`);
        const data = await res.json();
        if (data.status === 'success') {
            state.plannerCustomItems = data.items || [];
        }
    } catch (e) {
        console.warn('Could not load planner custom items:', e);
    }
}

async function generateDietPlan() {
    const preference = document.getElementById('planner-preference-select') ? 
        document.getElementById('planner-preference-select').value : 'all';

    const profile = state.user ? state.user.profile : null;

    try {
        await loadPlannerCustomItems();
        const res = await fetch('/api/planner/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile: profile, preference: preference })
        });
        const data = await res.json();
        if (data.status === 'success') {
            state.currentDietPlan = data.plan;
            renderDietPlan(data.plan);
        }
    } catch (e) {
        console.error('Failed to generate diet plan:', e);
    }
}

function renderDietPlan(plan) {
    if (!plan) return;
    const container = document.getElementById('planner-meals-container');
    if (!container) return;
    const isNe = state.lang === 'ne';

    // Summary banner values
    document.getElementById('plan-stat-target-cal').textContent = `${plan.target_daily_calories} kcal`;
    document.getElementById('plan-stat-plan-cal').textContent = `${plan.total_planned_calories} kcal`;
    document.getElementById('plan-stat-target-pro').textContent = `${plan.target_daily_protein_g} g`;
    document.getElementById('plan-stat-plan-pro').textContent = `${plan.total_planned_protein_g} g`;

    // Tips list
    const tipsContainer = document.getElementById('planner-tips-list');
    if (tipsContainer) {
        const tips = isNe ? plan.tips_ne : plan.tips_en;
        tipsContainer.innerHTML = tips.map(t => `<li>${t}</li>`).join('');
    }

    // Saved checked state for individual items from localStorage for today
    const today = new Date().toISOString().slice(0, 10);
    const checkedKey = `checked_food_items_${today}`;
    const savedChecked = JSON.parse(localStorage.getItem(checkedKey) || '{}');

    // Meal icon mappings
    const icons = {
        breakfast: 'sunrise',
        lunch: 'sun',
        snack: 'coffee',
        dinner: 'moon'
    };

    container.innerHTML = plan.meals.map(meal => {
        // Find custom entries for this meal type
        const customItems = (state.plannerCustomItems || []).filter(c => c.meal_type === meal.meal_type);

        return `
            <div class="glass-card p-5 space-y-4 border border-slate-200">
                <!-- Meal Header -->
                <div class="flex items-start justify-between gap-3 pb-3 border-b border-slate-100">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                            <i data-lucide="${icons[meal.meal_type] || 'utensils'}" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h3 class="font-extrabold text-sm sm:text-base text-slate-900">
                                ${isNe ? meal.title_ne : meal.title_en}
                            </h3>
                            <span class="text-[11px] text-slate-500 font-medium">${meal.time_hint}</span>
                        </div>
                    </div>

                    <span class="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                        ${isNe ? '✓ परिकार चेकलिस्ट' : '✓ Item Checklist'}
                    </span>
                </div>

                <!-- Meal Calories & Macro Badges -->
                <div class="flex items-center justify-between text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
                    <div>
                        <span class="text-slate-400 block text-[10px]">क्यालोरी</span>
                        <strong class="text-emerald-700 font-black">${meal.total_calories} kcal</strong>
                    </div>
                    <div>
                        <span class="text-slate-400 block text-[10px]">प्रोटिन</span>
                        <strong class="text-teal-700 font-bold">${meal.total_protein_g} g</strong>
                    </div>
                    <div>
                        <span class="text-slate-400 block text-[10px]">कार्ब्स</span>
                        <strong class="text-amber-700 font-bold">${meal.total_carbs_g} g</strong>
                    </div>
                    <div>
                        <span class="text-slate-400 block text-[10px]">चिल्लो</span>
                        <strong class="text-slate-700 font-bold">${meal.total_fat_g} g</strong>
                    </div>
                </div>

                <!-- Individual Food Items Checklist (User can check or skip per item) -->
                <div class="space-y-2 text-xs">
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
                        ${isNe ? 'खाएका परिकार छनौट गर्नुहोस् (Check Eaten Items):' : 'Select items you ate:'}
                    </p>
                    ${meal.items.map((it, idx) => {
                        const itemKey = `${meal.meal_type}_it_${idx}_${encodeURIComponent(it.name_ne)}`;
                        const isChecked = !!savedChecked[itemKey];
                        return `
                            <div class="flex items-center justify-between gap-2.5 p-2.5 rounded-xl ${isChecked ? 'bg-emerald-50/70 border-emerald-300' : 'bg-white border-slate-100'} border hover:border-emerald-200 transition">
                                <label class="flex items-center gap-2.5 cursor-pointer flex-1 select-none">
                                    <input type="checkbox" 
                                        id="${itemKey}" 
                                        ${isChecked ? 'checked' : ''} 
                                        onchange="toggleFoodItemCheck('${itemKey}', '${meal.meal_type}', '${it.name_ne.replace(/'/g, "\\'")}', '${it.portion_desc}', ${it.calories}, ${it.protein_g}, ${it.carbs_g}, ${it.fat_g})" 
                                        class="w-4 h-4 accent-emerald-600 rounded cursor-pointer">
                                    <div>
                                        <strong class="text-xs ${isChecked ? 'line-through text-slate-400' : 'text-slate-800'}">
                                            ${isNe ? it.name_ne : it.name_en}
                                        </strong>
                                        <span class="text-[11px] text-slate-500 block">${it.portion_desc} (${it.weight_g}g)</span>
                                        ${it.notes ? `<p class="text-[10px] text-emerald-700 mt-0.5">🌱 ${it.notes}</p>` : ''}
                                    </div>
                                </label>
                                <div class="text-right flex-shrink-0">
                                    <span class="font-bold text-xs ${isChecked ? 'line-through text-slate-400' : 'text-slate-900'}">${it.calories} kcal</span>
                                    <span class="text-[10px] text-slate-400 block">${it.protein_g}g pro</span>
                                </div>
                            </div>
                        `;
                    }).join('')}

                    <!-- Custom Entries in this meal section -->
                    ${customItems.map(c => {
                        const customKey = `custom_${c.id}`;
                        const isCustomChecked = c.is_completed || !!savedChecked[customKey];
                        return `
                            <div class="flex items-center justify-between gap-2.5 p-2.5 rounded-xl ${isCustomChecked ? 'bg-amber-50/70 border-amber-300' : 'bg-amber-50/30 border-amber-200'} border transition">
                                <label class="flex items-center gap-2.5 cursor-pointer flex-1 select-none">
                                    <input type="checkbox" 
                                        id="${customKey}" 
                                        ${isCustomChecked ? 'checked' : ''} 
                                        onchange="toggleFoodItemCheck('${customKey}', '${c.meal_type}', '${c.food_name.replace(/'/g, "\\'")}', '${c.portion_desc}', ${c.calories}, ${c.protein_g}, ${c.carbs_g}, ${c.fat_g}, ${c.id})" 
                                        class="w-4 h-4 accent-amber-600 rounded cursor-pointer">
                                    <div>
                                        <div class="flex items-center gap-1.5">
                                            <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-200 text-amber-900">कस्टम एन्ट्री</span>
                                            <strong class="text-xs ${isCustomChecked ? 'line-through text-slate-400' : 'text-slate-900'}">
                                                ${c.food_name}
                                            </strong>
                                        </div>
                                        <span class="text-[11px] text-slate-500 block">${c.portion_desc}</span>
                                        ${c.notes ? `<p class="text-[10px] text-amber-800 mt-0.5">📝 ${c.notes}</p>` : ''}
                                    </div>
                                </label>
                                <div class="flex items-center gap-2 flex-shrink-0">
                                    <div class="text-right">
                                        <span class="font-bold text-xs ${isCustomChecked ? 'line-through text-slate-400' : 'text-slate-900'}">${c.calories} kcal</span>
                                        <span class="text-[10px] text-slate-400 block">${c.protein_g}g pro</span>
                                    </div>
                                    <button type="button" onclick="deleteCustomPlannerItem(${c.id})" class="p-1 text-slate-400 hover:text-red-600 rounded transition" title="हटाउनुहोस्">
                                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                                    </button>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }).join('');

    lucide.createIcons();
}

async function toggleFoodItemCheck(itemKey, mealType, foodName, portionDesc, calories, protein, carbs, fat, customItemId = null) {
    const today = new Date().toISOString().slice(0, 10);
    const checkedKey = `checked_food_items_${today}`;
    const savedChecked = JSON.parse(localStorage.getItem(checkedKey) || '{}');
    const isNowChecked = !savedChecked[itemKey];
    savedChecked[itemKey] = isNowChecked;
    localStorage.setItem(checkedKey, JSON.stringify(savedChecked));

    if (customItemId) {
        // Update custom item in database
        try {
            await fetch('/api/planner/toggle-item', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    item_id: customItemId,
                    is_completed: isNowChecked,
                    user_id: state.user ? state.user.name : 'default',
                    food_name: foodName,
                    meal_type: mealType,
                    portion_desc: portionDesc,
                    calories: calories,
                    protein_g: protein,
                    carbs_g: carbs,
                    fat_g: fat
                })
            });
            await loadPlannerCustomItems();
        } catch (e) {
            console.error('Failed to toggle custom planner item:', e);
        }
    } else {
        // Individual planned food item checked: log to today's consumed total
        if (isNowChecked && calories > 0) {
            const payload = {
                user_id: state.user ? state.user.name : 'default',
                meal_type: mealType,
                food_name: foodName,
                portion_desc: portionDesc || '१ भाग',
                calories: calories,
                protein_g: protein || 0,
                carbs_g: carbs || 0,
                fat_g: fat || 0,
                is_cheat: false,
                notes: 'दैनिक तालिका चेकलिस्टबाट खाएको (Individual Item Checked)'
            };
            try {
                await fetch('/api/history/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } catch (e) {
                console.error('Failed to log individual item:', e);
            }
        }
    }

    // Refresh weekly budget chart on dashboard and update planner list
    renderWeeklyBudgetChart();
    renderDietPlan(state.currentDietPlan);
}

async function deleteCustomPlannerItem(itemId) {
    if (!confirm('के तपाईं यो कस्टम परिकार दैनिक तालिकाबाट हटाउन चाहनुहुन्छ?')) return;
    try {
        const res = await fetch(`/api/planner/items/${itemId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.status === 'success') {
            await loadPlannerCustomItems();
            renderDietPlan(state.currentDietPlan);
        }
    } catch (e) {
        console.error('Failed to delete custom planner item:', e);
    }
}

// =========================================================
// FEATURE 2: CUSTOM PLANNER ENTRY & NUTRITION ESTIMATION
// =========================================================
function populateManualFoodPresets() {
    const select = document.getElementById('manual-food-preset');
    if (!select || !state.allFoods || state.allFoods.length === 0) return;

    select.innerHTML = '<option value="">-- रोज्नुहोस् वा आफ्नै लेख्नुहोस् --</option>' + 
        state.allFoods.map(f => `
            <option value="${f.id}" data-name="${f.name_ne}" data-cal="${f.per_serving.calories}" data-pro="${f.per_serving.protein_g}" data-carb="${f.per_serving.carbs_g}" data-fat="${f.per_serving.fat_g}">
                ${f.name_ne} (${f.name_en}) - ${f.per_serving.calories} kcal
            </option>
        `).join('');
}

function handleManualFoodPresetSelect(event) {
    const opt = event.target.selectedOptions[0];
    if (!opt || !opt.dataset.name) return;

    document.getElementById('manual-food-name').value = opt.dataset.name;
    document.getElementById('manual-calories').value = opt.dataset.cal;
    document.getElementById('manual-protein').value = opt.dataset.pro;
    document.getElementById('manual-carbs').value = opt.dataset.carb;
    document.getElementById('manual-fat').value = opt.dataset.fat;
}

async function autoEstimateNutritionFromInput() {
    const foodName = document.getElementById('manual-food-name').value.trim();
    if (!foodName) return;
    const portionDesc = document.getElementById('manual-portion-desc').value.trim();
    const curCal = document.getElementById('manual-calories').value.trim();

    try {
        const res = await fetch('/api/foods/estimate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ food_name: foodName, portion_desc: portionDesc })
        });
        const data = await res.json();
        if (data.status === 'success' && data.estimate) {
            const est = data.estimate;
            if (!curCal || parseFloat(curCal) === 0) {
                document.getElementById('manual-calories').value = est.calories;
                document.getElementById('manual-protein').value = est.protein_g;
                document.getElementById('manual-carbs').value = est.carbs_g;
                document.getElementById('manual-fat').value = est.fat_g;
            }
            const badge = document.getElementById('manual-estimate-badge');
            const txt = document.getElementById('manual-estimate-text');
            if (badge && txt) {
                badge.classList.remove('hidden');
                txt.textContent = `${est.source}: ~${est.calories} kcal, ${est.protein_g}g प्रोटिन`;
            }
        }
    } catch (e) {
        console.warn('Auto estimation note:', e);
    }
}

function openManualMealModal() {
    document.getElementById('modal-manual-meal').classList.remove('hidden');
    populateManualFoodPresets();
}

function closeManualMealModal() {
    document.getElementById('modal-manual-meal').classList.add('hidden');
}

async function handleManualMealSubmit(event) {
    event.preventDefault();
    const foodName = document.getElementById('manual-food-name').value.trim();
    if (!foodName) return;

    const payload = {
        user_id: state.user ? state.user.name : 'default',
        meal_type: document.getElementById('manual-meal-type').value,
        food_name: foodName,
        portion_desc: document.getElementById('manual-portion-desc').value.trim() || '१ भाग',
        calories: parseFloat(document.getElementById('manual-calories').value) || 0,
        protein_g: parseFloat(document.getElementById('manual-protein').value) || 0,
        carbs_g: parseFloat(document.getElementById('manual-carbs').value) || 0,
        fat_g: parseFloat(document.getElementById('manual-fat').value) || 0,
        notes: document.getElementById('manual-notes').value.trim() || '',
        date: new Date().toISOString().slice(0, 10)
    };

    try {
        // Directly adds to Daily Planner (not history tab!)
        const res = await fetch('/api/planner/custom-entry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            closeManualMealModal();
            // Reset form
            document.getElementById('manual-food-name').value = '';
            document.getElementById('manual-portion-desc').value = '';
            document.getElementById('manual-calories').value = '';
            document.getElementById('manual-protein').value = '';
            document.getElementById('manual-carbs').value = '';
            document.getElementById('manual-fat').value = '';
            document.getElementById('manual-notes').value = '';
            const b = document.getElementById('manual-estimate-badge');
            if (b) b.classList.add('hidden');

            // Refresh planner items and re-render
            await loadPlannerCustomItems();
            renderDietPlan(state.currentDietPlan);
            alert('कस्टम परिकार दैनिक तालिकामा थपियो! (Added to Daily Planner)');
        }
    } catch (e) {
        alert('कस्टम परिकार थप्न असफल भयो।');
    }
}

// =========================================================
// FEATURE 3: DIET HISTORY TAB & LOG FEED
// =========================================================
async function loadDietHistory(days = 30) {
    state.historyFilterDays = days;
    const userName = state.user ? state.user.name : 'default';

    try {
        const res = await fetch(`/api/history/list?user_id=${encodeURIComponent(userName)}&days=${days}`);
        const data = await res.json();
        if (data.status === 'success') {
            state.dietHistory = data.logs;
            renderDietHistory(data.logs);
        }
    } catch (e) {
        console.error('Failed to load diet history:', e);
    }
}

function filterHistoryDays(days) {
    const btns = [1, 7, 30];
    btns.forEach(d => {
        const b = document.getElementById(`hist-btn-${d}`);
        if (b) {
            b.classList.remove('bg-emerald-600', 'text-white');
            b.classList.add('bg-white', 'text-slate-700');
        }
    });

    const activeBtn = document.getElementById(`hist-btn-${days}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-white', 'text-slate-700');
        activeBtn.classList.add('bg-emerald-600', 'text-white');
    }

    loadDietHistory(days);
}

function renderDietHistory(logs) {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;
    const isNe = state.lang === 'ne';

    // Calculate today's adherence stats
    const todayStr = new Date().toISOString().slice(0, 10);
    const todayLogs = logs.filter(l => l.date === todayStr);
    const todayCal = Math.round(todayLogs.reduce((acc, l) => acc + (l.calories || 0), 0));
    const todayPro = Math.round(todayLogs.reduce((acc, l) => acc + (l.protein_g || 0), 0) * 10) / 10;
    const targetCal = state.user ? state.user.assessment.target_daily.calories : 2449;

    document.getElementById('hist-stat-today-cal').textContent = `${todayCal} kcal`;
    document.getElementById('hist-stat-today-target').textContent = `${targetCal} kcal`;
    document.getElementById('hist-stat-today-pro').textContent = `${todayPro} g`;
    document.getElementById('hist-stat-total-count').textContent = `${logs.length} ${isNe ? 'छाक' : 'meals'}`;
    document.getElementById('history-count-badge').textContent = `${logs.length} ${isNe ? 'रेकर्ड भेटियो' : 'records'}`;

    if (logs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="py-8 text-center text-slate-400">
                    कुनै खाना रेकर्ड गरिएको छैन। माथिको 'म्यानुअल थप्नुहोस्' वा खाना तालिकाबाट चेक गर्नुहोस्।
                </td>
            </tr>
        `;
        return;
    }

    const mealLabels = {
        breakfast: isNe ? 'बिहानी खाजा' : 'Breakfast',
        lunch: isNe ? 'मुख्य खाना' : 'Lunch',
        snack: isNe ? 'दिउँसो खाजा' : 'Snack',
        dinner: isNe ? 'साँझ खाना' : 'Dinner',
        cheat: isNe ? 'कस्टम परिकार ✨' : 'Custom Entry'
    };

    tbody.innerHTML = logs.map(log => `
        <tr class="hover:bg-slate-50/80 transition">
            <td class="py-3 px-4 text-slate-600">
                <span class="font-bold text-slate-900 block">${log.date}</span>
                <span class="text-[10px] text-slate-400">${(log.timestamp || '').slice(11, 16)}</span>
            </td>
            <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${log.is_cheat ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">
                    ${mealLabels[log.meal_type] || log.meal_type}
                </span>
            </td>
            <td class="py-3 px-4 font-semibold text-slate-800">
                <span>${log.food_name}</span>
                ${log.portion_desc ? `<span class="text-[11px] text-slate-400 block">${log.portion_desc}</span>` : ''}
                ${log.notes ? `<span class="text-[10px] text-slate-500 italic block">"${log.notes}"</span>` : ''}
            </td>
            <td class="py-3 px-4 font-extrabold text-emerald-700">${log.calories}</td>
            <td class="py-3 px-4 font-bold text-teal-700">${log.protein_g}g</td>
            <td class="py-3 px-4">
                ${log.is_cheat ? 
                    '<span class="text-[11px] font-bold text-amber-700">✨ कस्टम परिकार</span>' : 
                    '<span class="text-[11px] font-medium text-emerald-700">✓ नियमित</span>'}
            </td>
            <td class="py-3 px-4 text-right">
                <button onclick="deleteHistoryLog(${log.id})" class="p-1 text-slate-400 hover:text-red-600 rounded transition" title="Delete">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </td>
        </tr>
    `).join('');

    lucide.createIcons();
}

async function deleteHistoryLog(id) {
    if (!confirm('के तपाईं यो रेकर्ड मेटाउन चाहनुहुन्छ?')) return;
    try {
        const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.status === 'success') {
            loadDietHistory(state.historyFilterDays);
            renderWeeklyBudgetChart();
        }
    } catch (e) {
        alert('मेटाउन असफल भयो।');
    }
}

// Log directly from Scanner Results
async function logScannedMealToHistory() {
    if (!state.currentMealAnalysis) return;
    const { recognition, meal } = state.currentMealAnalysis;

    const payload = {
        user_id: state.user ? state.user.name : 'default',
        meal_type: 'lunch',
        food_name: recognition.dish_title_ne || recognition.dish_title_en,
        portion_desc: 'AI क्यामेरा स्क्यान गरिएको थाली',
        calories: meal.totals.calories,
        protein_g: meal.totals.protein_g,
        carbs_g: meal.totals.carbs_g,
        fat_g: meal.totals.fat_g,
        is_cheat: false,
        notes: 'Gemma Multimodal AI Vision द्वारा स्क्यान'
    };

    try {
        await fetch('/api/history/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert('खाना इतिहासमा थपियो! तपाईं इतिहास ट्याबमा हेर्न सक्नुहुन्छ।');
        renderWeeklyBudgetChart();
    } catch (e) {
        alert('इतिहासमा थप्न असफल भयो।');
    }
}

// =========================================================
// FEATURE 4: 1-MONTH DOCTOR PDF REPORT EXPORT
// =========================================================
async function downloadDoctorReportPDF() {
    const userName = state.user ? state.user.name : 'Patient';
    const profile = state.user ? state.user.profile : { age_years: 23, sex: 'male', height_cm: 172, weight_kg: 64 };
    const assessment = state.user ? state.user.assessment : { bmi: 21.6, bmr_kcal: 1580, tdee_kcal: 2449, bmi_category: { category_en: 'Normal' } };

    try {
        const res = await fetch(`/api/history/doctor-report-data?user_id=${encodeURIComponent(userName)}&target_kcal=${assessment.tdee_kcal}`);
        const data = await res.json();
        const logs = data.logs_30_days || [];
        const stats = data.weekly_stats || {};

        if (!window.jspdf || !window.jspdf.jsPDF) {
            alert('PDF लाइब्रेरी लोड हुन सकेन। कृपया इन्टरनेट जाँच गर्नुहोस्।');
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

        // 1. Header Banner
        doc.setFillColor(22, 101, 52); // Forest Green
        doc.rect(0, 0, 210, 28, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text('POSHAN-AI : CLINICAL NUTRITION & DIETETICS REPORT', 14, 12);
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        doc.text('Comprehensive 30-Day Dietary Adherence, BMR & Malnutrition Assessment', 14, 19);
        doc.text(`Generated: ${new Date().toLocaleDateString()} | For Physician & Dietitian Review`, 14, 24);

        // 2. Patient Demographics & Clinical Profile
        doc.setTextColor(30, 41, 59);
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('1. PATIENT DEMOGRAPHICS & CLINICAL METRICS', 14, 37);

        const patientTableData = [
            [
                `Patient Name: ${userName}`,
                `Age / Sex: ${profile.age_years} yrs / ${profile.sex.toUpperCase()}`,
                `Height / Weight: ${profile.height_cm} cm / ${profile.weight_kg} kg`
            ],
            [
                `WHO BMI: ${assessment.bmi} (${assessment.bmi_category ? assessment.bmi_category.category_en : 'Healthy'})`,
                `Resting BMR: ${assessment.bmr_kcal} kcal/day`,
                `Daily TDEE Target: ${assessment.tdee_kcal} kcal/day`
            ],
            [
                `Protein Target: ${assessment.target_daily ? assessment.target_daily.protein_g : 75} g/day`,
                `Malnutrition Risk: Low / Stable`,
                `Reporting Window: Past 30 Days`
            ]
        ];

        doc.autoTable({
            startY: 40,
            head: [],
            body: patientTableData,
            theme: 'plain',
            styles: { fontSize: 8.5, cellPadding: 2, textColor: [51, 65, 85] },
            columnStyles: { 0: { cellWidth: 65 }, 1: { cellWidth: 65 }, 2: { cellWidth: 60 } }
        });

        // 3. 30-Day Dietary Adherence Summary
        const summaryY = doc.lastAutoTable.finalY + 6;
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('2. 30-DAY METABOLIC COMPLIANCE SUMMARY', 14, summaryY);

        const totalCal = logs.reduce((acc, l) => acc + (l.calories || 0), 0);
        const totalPro = logs.reduce((acc, l) => acc + (l.protein_g || 0), 0);
        const cheatCount = logs.filter(l => l.is_cheat).length;
        const avgDailyCal = logs.length > 0 ? Math.round(totalCal / Math.min(30, logs.length)) : assessment.tdee_kcal;

        const complianceData = [
            [
                `Average Daily Calorie Intake: ${avgDailyCal} kcal`,
                `Daily Budget Variance: ${avgDailyCal - assessment.tdee_kcal > 0 ? '+' : ''}${avgDailyCal - assessment.tdee_kcal} kcal`,
                `Total Meals Logged: ${logs.length} entries`
            ],
            [
                `Average Protein Delivery: ${Math.round(totalPro / Math.max(1, logs.length / 3))} g/day`,
                `Custom Entries Logged: ${cheatCount} meals`,
                `Budget Adherence Rate: ${stats.adherence_rate_pct || 85}%`
            ]
        ];

        doc.autoTable({
            startY: summaryY + 3,
            head: [],
            body: complianceData,
            theme: 'grid',
            styles: { fontSize: 8, cellPadding: 2.5, fillColor: [240, 253, 244] },
        });

        // 4. Detailed 30-Day Log Table
        const logTableY = doc.lastAutoTable.finalY + 6;
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('3. DETAILED DIETARY INTAKE LOG (PAST 30 DAYS)', 14, logTableY);

        const tableRows = logs.map(l => [
            l.date,
            l.meal_type.toUpperCase(),
            l.food_name + (l.portion_desc ? ` (${l.portion_desc})` : ''),
            `${l.calories} kcal`,
            `${l.protein_g} g`,
            l.is_cheat ? 'CUSTOM' : 'NORMAL'
        ]);

        doc.autoTable({
            startY: logTableY + 3,
            head: [['Date', 'Meal', 'Food Description & Portion', 'Calories', 'Protein', 'Status']],
            body: tableRows.length > 0 ? tableRows : [['-', '-', 'No meal logs recorded in this period', '-', '-', '-']],
            theme: 'striped',
            styles: { fontSize: 7.5, cellPadding: 2 },
            headStyles: { fillColor: [22, 101, 52], textColor: 255, fontStyle: 'bold' },
            alternateRowStyles: { fillColor: [250, 250, 250] },
            columnStyles: {
                0: { cellWidth: 22 },
                1: { cellWidth: 22 },
                2: { cellWidth: 85 },
                3: { cellWidth: 25 },
                4: { cellWidth: 20 },
                5: { cellWidth: 16 }
            }
        });

        // 5. Physician Clinical Notes Box
        const notesY = Math.min(doc.lastAutoTable.finalY + 6, 260);
        if (notesY < 250) {
            doc.setFontSize(10);
            doc.setFont('helvetica', 'bold');
            doc.text('4. CLINICAL IMPRESSION & DIETITIAN SIGN-OFF', 14, notesY);
            doc.setFontSize(8);
            doc.setFont('helvetica', 'normal');
            doc.text('Remarks: Patient dietary adherence screened via PoshanAI. Recommendations: maintain dense legume & greens intake.', 14, notesY + 5);
            doc.line(14, notesY + 18, 90, notesY + 18);
            doc.text('Physician / Clinical Nutritionist Signature', 14, notesY + 22);
            doc.line(120, notesY + 18, 190, notesY + 18);
            doc.text('Date & Hospital / Clinic Stamp', 120, notesY + 22);
        }

        // Save PDF
        const safeName = userName.replace(/[^a-zA-Z0-9]/g, '_');
        doc.save(`PoshanAI_Medical_Nutrition_Report_${safeName}.pdf`);

    } catch (e) {
        console.error('Failed to generate doctor PDF:', e);
        alert('PDF निर्माण गर्न असफल भयो।');
    }
}

// =========================================================
// FOOD SCANNER & MULTIMODAL VISION ENGINE
// =========================================================
async function loadSamples() {
    try {
        const res = await fetch('/api/samples');
        const data = await res.json();
        if (data.status === 'success') {
            state.samplesList = data.samples;
            renderSamplesGrid(data.samples);
        }
    } catch (e) {
        console.error('Failed to load sample dishes:', e);
    }
}

function renderSamplesGrid(samples) {
    const container = document.getElementById('sample-cards-container');
    if (!container) return;
    const isNe = state.lang === 'ne';

    container.innerHTML = samples.map(s => `
        <div onclick="selectSampleDish('${s.filename}', this)" 
            class="sample-card cursor-pointer p-2.5 rounded-xl border ${s.filename === state.selectedSampleFilename ? 'border-emerald-600 bg-emerald-50/50 ring-2 ring-emerald-500/30' : 'border-slate-200 bg-white'} hover:shadow-md transition text-center space-y-2">
            <img src="/static/sample_images/${s.filename}" alt="${s.name_en}" class="w-full h-24 object-cover rounded-lg shadow-sm">
            <h4 class="font-extrabold text-xs text-slate-800 truncate">${isNe ? s.name_ne : s.name_en}</h4>
            <p class="text-[10px] text-slate-500 line-clamp-2 leading-tight">${isNe ? s.description_ne : s.description_en}</p>
        </div>
    `).join('');
}

function selectSampleDish(filename, cardEl) {
    state.selectedSampleFilename = filename;
    document.querySelectorAll('.sample-card').forEach(c => {
        c.classList.remove('border-emerald-600', 'bg-emerald-50/50', 'ring-2', 'ring-emerald-500/30');
        c.classList.add('border-slate-200', 'bg-white');
    });
    if (cardEl) {
        cardEl.classList.remove('border-slate-200', 'bg-white');
        cardEl.classList.add('border-emerald-600', 'bg-emerald-50/50', 'ring-2', 'ring-emerald-500/30');
    }
}

function switchScannerMode(mode) {
    state.currentScannerMode = mode;
    ['samples', 'upload', 'camera'].forEach(m => {
        const tab = document.getElementById(`tab-scan-${m}`);
        const view = document.getElementById(`mode-${m}`);
        if (tab) {
            tab.classList.remove('border-emerald-600', 'text-emerald-700');
            tab.classList.add('border-transparent', 'text-slate-500');
        }
        if (view) view.classList.add('hidden');
    });

    const activeTab = document.getElementById(`tab-scan-${mode}`);
    const activeView = document.getElementById(`mode-${mode}`);
    if (activeTab) {
        activeTab.classList.remove('border-transparent', 'text-slate-500');
        activeTab.classList.add('border-emerald-600', 'text-emerald-700');
    }
    if (activeView) activeView.classList.remove('hidden');

    if (mode === 'camera') {
        startCamera();
    } else {
        stopCamera();
    }
}

// Camera Controls
async function startCamera() {
    const video = document.getElementById('camera-stream');
    const placeholder = document.getElementById('camera-placeholder');
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        state.cameraStream = stream;
        video.srcObject = stream;
        video.classList.remove('hidden');
        if (placeholder) placeholder.classList.add('hidden');
    } catch (e) {
        alert('क्यामेरा सुरु गर्न सकिएन। कृपया अनुमति दिनुहोस् वा फोटो अपलोड गर्नुहोस्।');
    }
}

function stopCamera() {
    if (state.cameraStream) {
        state.cameraStream.getTracks().forEach(t => t.stop());
        state.cameraStream = null;
    }
    const video = document.getElementById('camera-stream');
    if (video) video.classList.add('hidden');
    const placeholder = document.getElementById('camera-placeholder');
    if (placeholder) placeholder.classList.remove('hidden');
}

function captureCameraSnapshot() {
    const video = document.getElementById('camera-stream');
    const canvas = document.getElementById('camera-canvas');
    if (!state.cameraStream) {
        alert('पहिले क्यामेरा खोल्नुहोस्।');
        return;
    }
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
        const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
        executeMealAnalysisWithFile(file);
    }, 'image/jpeg');
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        executeMealAnalysisWithFile(file);
    }
}

// Execute Analysis
async function executeMealAnalysis() {
    if (state.currentScannerMode === 'samples') {
        const btn = document.getElementById('btn-trigger-analysis');
        btn.innerHTML = `<span class="inline-block animate-spin mr-2">⏳</span> ${state.lang === 'ne' ? i18n.ne.analyzingMsg : i18n.en.analyzingMsg}`;
        btn.disabled = true;

        try {
            const res = await fetch('/api/analyze/sample', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sample_filename: state.selectedSampleFilename,
                    custom_profile: state.user ? state.user.profile : null
                })
            });
            const data = await res.json();
            if (data.status === 'success') {
                renderAnalysisResults(data, `/static/sample_images/${state.selectedSampleFilename}`);
            }
        } catch (e) {
            alert('विश्लेषण असफल भयो।');
        } finally {
            btn.innerHTML = `<i data-lucide="sparkles" class="w-5 h-5"></i><span>${state.lang === 'ne' ? i18n.ne.btnAnalyze : i18n.en.btnAnalyze}</span>`;
            btn.disabled = false;
            lucide.createIcons();
        }
    }
}

async function executeMealAnalysisWithFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    if (state.user) {
        formData.append('age', state.user.profile.age_years);
        formData.append('sex', state.user.profile.sex);
        formData.append('height_cm', state.user.profile.height_cm);
        formData.append('weight_kg', state.user.profile.weight_kg);
        formData.append('activity', state.user.profile.activity_level);
        formData.append('goal', state.user.profile.goal);
    }

    const btn = document.getElementById('btn-trigger-analysis');
    btn.innerHTML = `<span class="inline-block animate-spin mr-2">⏳</span> ${state.lang === 'ne' ? i18n.ne.analyzingMsg : i18n.en.analyzingMsg}`;
    btn.disabled = true;

    try {
        const res = await fetch('/api/analyze/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.status === 'success') {
            const previewUrl = URL.createObjectURL(file);
            renderAnalysisResults(data, previewUrl);
        }
    } catch (e) {
        alert('फोटो विश्लेषण असफल भयो।');
    } finally {
        btn.innerHTML = `<i data-lucide="sparkles" class="w-5 h-5"></i><span>${state.lang === 'ne' ? i18n.ne.btnAnalyze : i18n.en.btnAnalyze}</span>`;
        btn.disabled = false;
        lucide.createIcons();
    }
}

// Render Scanner Results & Chart.js Charts
function renderAnalysisResults(data, imageUrl) {
    state.currentMealAnalysis = data;
    const isNe = state.lang === 'ne';
    const { recognition, meal, evaluation, assessment } = data;

    const container = document.getElementById('analysis-results');
    container.classList.remove('hidden');

    document.getElementById('res-dish-img').src = imageUrl;
    document.getElementById('res-dish-title').textContent = isNe ? recognition.dish_title_ne : recognition.dish_title_en;
    document.getElementById('res-dish-desc').textContent = isNe ? recognition.summary_ne : recognition.summary_en;

    document.getElementById('res-tot-cal').textContent = meal.totals.calories;
    document.getElementById('res-tot-pro').textContent = meal.totals.protein_g;
    document.getElementById('res-tot-carb').textContent = meal.totals.carbs_g;
    document.getElementById('res-tot-fat').textContent = meal.totals.fat_g;

    const itemsContainer = document.getElementById('detected-items-container');
    itemsContainer.innerHTML = recognition.items.map((item, idx) => `
        <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <div class="flex items-center justify-between text-xs font-bold text-slate-800">
                <span>${isNe ? item.name_ne : item.name_en}</span>
                <span id="item-weight-lbl-${idx}" class="text-emerald-700">${item.estimated_weight_g} g</span>
            </div>
            <input type="range" min="20" max="500" step="10" value="${item.estimated_weight_g}" 
                data-food-id="${item.food_id_guess}" data-idx="${idx}"
                oninput="document.getElementById('item-weight-lbl-${idx}').textContent = this.value + ' g'"
                class="w-full mt-1.5 accent-emerald-600 cursor-pointer">
        </div>
    `).join('');

    const verdictBox = document.getElementById('res-verdict-box');
    document.getElementById('res-verdict-title').textContent = isNe ? evaluation.verdict_ne : evaluation.verdict_en;
    document.getElementById('res-verdict-summary').textContent = 
        `${isNe ? 'यो खानाले दैनिक कुल ऊर्जाको' : 'Meal fulfills'} ${evaluation.calorie_share_tdee_pct}% ${isNe ? 'र प्रोटिनको' : 'of daily TDEE and'} ${evaluation.protein_share_target_pct}% ${isNe ? 'पूरा गर्छ।' : 'of protein goal.'}`;
    document.getElementById('res-verdict-score').textContent = `${evaluation.score_out_of_10}/१०`;

    if (evaluation.score_out_of_10 >= 8.0) {
        verdictBox.className = 'p-4 rounded-xl border-l-4 shadow-sm bg-emerald-50 border-emerald-500';
    } else if (evaluation.score_out_of_10 >= 6.0) {
        verdictBox.className = 'p-4 rounded-xl border-l-4 shadow-sm bg-amber-50 border-amber-500';
    } else {
        verdictBox.className = 'p-4 rounded-xl border-l-4 shadow-sm bg-red-50 border-red-500';
    }

    const flagsList = document.getElementById('res-flags-list');
    flagsList.innerHTML = evaluation.malnutrition_flags.map(f => `
        <div class="flex items-start gap-1.5 text-amber-800 font-medium">
            <span>⚠️</span>
            <span>${isNe ? f.message_ne : f.message_en}</span>
        </div>
    `).join('');

    const additionsList = document.getElementById('res-additions-list');
    const additions = isNe ? evaluation.suggested_local_additions_ne : evaluation.suggested_local_additions_en;
    additionsList.innerHTML = additions.map(add => `<li>${add}</li>`).join('');

    // Charts
    renderMacrosPieChart(meal);
    renderCaloriesBarChart(meal, assessment || (state.user ? state.user.assessment : null));
    renderMicronutrientsBarChart(meal, assessment || (state.user ? state.user.assessment : null));

    lucide.createIcons();
    container.scrollIntoView({ behavior: 'smooth' });
}

async function recalculateCurrentMeal() {
    const sliders = document.querySelectorAll('#detected-items-container input[type="range"]');
    const portions = Array.from(sliders).map(s => ({
        food_id: s.dataset.foodId,
        weight_g: parseFloat(s.value),
        notes: null
    }));

    try {
        const res = await fetch('/api/meal/recalculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                portions: portions,
                custom_profile: state.user ? state.user.profile : null
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            const { meal, evaluation } = data;
            document.getElementById('res-tot-cal').textContent = meal.totals.calories;
            document.getElementById('res-tot-pro').textContent = meal.totals.protein_g;
            document.getElementById('res-tot-carb').textContent = meal.totals.carbs_g;
            document.getElementById('res-tot-fat').textContent = meal.totals.fat_g;

            document.getElementById('res-verdict-score').textContent = `${evaluation.score_out_of_10}/१०`;

            renderMacrosPieChart(meal);
            renderCaloriesBarChart(meal, state.user ? state.user.assessment : null);
            renderMicronutrientsBarChart(meal, state.user ? state.user.assessment : null);
        }
    } catch (e) {
        alert('पुनर्गणना असफल भयो।');
    }
}

// Chart 1: Macronutrient Pie
function renderMacrosPieChart(meal) {
    const ctx = document.getElementById('chart-macros-pie').getContext('2d');
    if (state.charts.macrosPie) state.charts.macrosPie.destroy();

    const isNe = state.lang === 'ne';
    state.charts.macrosPie = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                isNe ? 'कार्बोहाइड्रेट' : 'Carbs',
                isNe ? 'प्रोटिन' : 'Protein',
                isNe ? 'चिल्लो (Fat)' : 'Fat'
            ],
            datasets: [{
                data: [meal.totals.carbs_g, meal.totals.protein_g, meal.totals.fat_g],
                backgroundColor: ['#d97706', '#16a34a', '#84cc16'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } }
            },
            cutout: '65%'
        }
    });
}

// Chart 2: Energy Comparison Bar
function renderCaloriesBarChart(meal, assessment) {
    const ctx = document.getElementById('chart-calories-bar').getContext('2d');
    if (state.charts.caloriesBar) state.charts.caloriesBar.destroy();

    const bmr = assessment ? assessment.bmr_kcal : 1580;
    const tdee = assessment ? assessment.tdee_kcal : 2449;
    const isNe = state.lang === 'ne';

    state.charts.caloriesBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [
                isNe ? 'यो खाना' : 'This Meal',
                isNe ? 'BMR (आधारभूत)' : 'BMR Target',
                isNe ? 'TDEE (दिनभर)' : 'TDEE Budget'
            ],
            datasets: [{
                label: 'Calories (kcal)',
                data: [meal.totals.calories, bmr, tdee],
                backgroundColor: ['#16a34a', '#0d9488', '#0284c7'],
                borderRadius: 8,
                barThickness: 28
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: { font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// Chart 3: Micronutrients Bar
function renderMicronutrientsBarChart(meal, assessment) {
    const ctx = document.getElementById('chart-micronutrients-bar').getContext('2d');
    if (state.charts.micronutrientsBar) state.charts.micronutrientsBar.destroy();

    const targets = assessment ? assessment.target_daily : {
        protein_g: 75,
        iron_mg: 15,
        calcium_mg: 1000,
        vitamin_a_mcg: 800
    };

    const isNe = state.lang === 'ne';
    const labels = [
        isNe ? 'प्रोटिन' : 'Protein',
        isNe ? 'आइरन' : 'Iron',
        isNe ? 'क्याल्सियम' : 'Calcium',
        isNe ? 'भिटामिन ए' : 'Vit A',
        isNe ? 'फाइबर' : 'Fiber'
    ];

    const proPct = Math.min(Math.round((meal.totals.protein_g / (targets.protein_g || 1)) * 100), 150);
    const ironPct = Math.min(Math.round((meal.totals.iron_mg / (targets.iron_mg || 1)) * 100), 150);
    const calcPct = Math.min(Math.round((meal.totals.calcium_mg / (targets.calcium_mg || 1)) * 100), 150);
    const vitaPct = Math.min(Math.round((meal.totals.vitamin_a_mcg / (targets.vitamin_a_mcg || 1)) * 100), 150);
    const fiberPct = Math.min(Math.round((meal.totals.fiber_g / 30.0) * 100), 150);

    const values = [proPct, ironPct, calcPct, vitaPct, fiberPct];

    state.charts.micronutrientsBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '% of Daily Target',
                data: values,
                backgroundColor: values.map(v => v >= 70 ? '#16a34a' : (v >= 35 ? '#d97706' : '#ea580c')),
                borderRadius: 6,
                barThickness: 16
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    max: 120,
                    ticks: { callback: v => v + '%' },
                    grid: { color: '#f1f5f9' }
                },
                y: { grid: { display: false }, ticks: { font: { size: 10 } } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// =========================================================
// CHATBOT ENGINE
// =========================================================
async function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('chat-input-text');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    await sendChatMessage(msg);
}

async function sendQuickChatMessage(text) {
    switchNav('chat');
    await sendChatMessage(text);
}

async function sendChatMessage(msg) {
    const container = document.getElementById('chat-messages-container');

    const userDiv = document.createElement('div');
    userDiv.className = 'flex items-start justify-end gap-3';
    userDiv.innerHTML = `
        <div class="chat-bubble-user p-3.5 text-xs sm:text-sm max-w-[85%] shadow-sm">
            <p>${msg}</p>
        </div>
        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center flex-shrink-0 font-bold text-xs">
            ${state.user ? state.user.name.charAt(0) : 'म'}
        </div>
    `;
    container.appendChild(userDiv);
    container.scrollTop = container.scrollHeight;

    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'flex items-start gap-3';
    typingDiv.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0 font-bold text-sm">
            <i data-lucide="bot" class="w-4 h-4"></i>
        </div>
        <div class="chat-bubble-bot p-3 text-xs flex items-center gap-1.5">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    container.appendChild(typingDiv);
    lucide.createIcons();
    container.scrollTop = container.scrollHeight;

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg,
                language: state.lang,
                profile: state.user ? state.user.profile : null,
                meal_context: state.currentMealAnalysis ? state.currentMealAnalysis.meal : null
            })
        });
        const data = await res.json();
        const reply = data.status === 'success' ? data.reply : 'माफ गर्नुहोस्, जवाफ पाउन सकिएन।';

        const t = document.getElementById('typing-indicator');
        if (t) t.remove();

        const botDiv = document.createElement('div');
        botDiv.className = 'flex items-start gap-3';
        botDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0 font-bold text-sm">
                <i data-lucide="bot" class="w-4 h-4"></i>
            </div>
            <div class="chat-bubble-bot p-4 text-xs sm:text-sm max-w-[85%] space-y-1.5 leading-relaxed">
                ${reply.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
            </div>
        `;
        container.appendChild(botDiv);
        lucide.createIcons();
        container.scrollTop = container.scrollHeight;
    } catch (e) {
        const t = document.getElementById('typing-indicator');
        if (t) t.remove();
        alert('च्याट सर्भरसँग सम्पर्क हुन सकेन।');
    }
}

// =========================================================
// NEPALI FOODS ENCYCLOPAEDIA
// =========================================================
async function loadFoods() {
    try {
        const res = await fetch('/api/foods');
        const data = await res.json();
        if (data.status === 'success') {
            state.allFoods = data.foods;
            renderFoodsGrid(state.allFoods);
        }
    } catch (e) {
        console.error('Failed to load foods:', e);
    }
}

function renderFoodsGrid(foods) {
    const grid = document.getElementById('foods-grid');
    if (!grid) return;
    const isNe = state.lang === 'ne';

    grid.innerHTML = foods.map(food => `
        <div class="glass-card p-4 space-y-3 hover:shadow-md transition">
            <div class="flex items-start justify-between">
                <div>
                    <h4 class="font-extrabold text-sm text-slate-900">${isNe ? food.name_ne : food.name_en}</h4>
                    <span class="text-[11px] text-slate-500">${food.name_en}</span>
                </div>
                <span class="text-xs font-black text-emerald-700 px-2 py-0.5 rounded-md bg-emerald-50">${food.per_serving.calories} kcal</span>
            </div>
            <p class="text-xs text-slate-600 line-clamp-2">${isNe ? food.malnutrition_benefits_ne : food.malnutrition_benefits}</p>
            
            <div class="grid grid-cols-3 gap-1 text-center bg-slate-50 p-2 rounded-lg text-[11px]">
                <div><span class="text-slate-400 block">प्रोटिन</span><strong class="text-teal-700">${food.per_serving.protein_g}g</strong></div>
                <div><span class="text-slate-400 block">कार्ब्स</span><strong class="text-amber-700">${food.per_serving.carbs_g}g</strong></div>
                <div><span class="text-slate-400 block">आइरन</span><strong class="text-emerald-700">${food.per_serving.iron_mg}mg</strong></div>
            </div>

            <div class="flex flex-wrap gap-1">
                ${food.tags.map(t => `<span class="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold">#${t}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

function handleFoodSearch(event) {
    const q = event.target.value.toLowerCase().trim();
    if (!q) {
        renderFoodsGrid(state.allFoods);
        return;
    }
    const filtered = state.allFoods.filter(f => 
        f.name_en.toLowerCase().includes(q) ||
        f.name_ne.toLowerCase().includes(q) ||
        f.tags.some(t => t.toLowerCase().includes(q))
    );
    renderFoodsGrid(filtered);
}

function filterFoodsCategory(category) {
    const pills = document.querySelectorAll('.cat-pill');
    pills.forEach(p => p.classList.remove('bg-emerald-600', 'text-white'));
    event.target.classList.add('bg-emerald-600', 'text-white');

    if (category === 'all') {
        renderFoodsGrid(state.allFoods);
    } else {
        const filtered = state.allFoods.filter(f => f.tags.includes(category));
        renderFoodsGrid(filtered);
    }
}

// =========================================================
// LOCALIZATION (NEPALI / ENGLISH)
// =========================================================
function toggleLanguage() {
    state.lang = state.lang === 'ne' ? 'en' : 'ne';
    localStorage.setItem('poshan_lang', state.lang);
    applyLanguage();
    updateUserInterface();
    if (state.currentMealAnalysis) {
        renderAnalysisResults(state.currentMealAnalysis, document.getElementById('res-dish-img').src);
    }
    if (state.currentDietPlan) {
        renderDietPlan(state.currentDietPlan);
    }
    renderFoodsGrid(state.allFoods);
    renderSamplesGrid(state.samplesList);
}

function applyLanguage() {
    const isNe = state.lang === 'ne';
    const dict = isNe ? i18n.ne : i18n.en;

    document.title = dict.appTitle;
    const loginLangLabel = document.getElementById('login-lang-label');
    if (loginLangLabel) loginLangLabel.textContent = dict.loginLangLabel;

    const navLangTag = document.getElementById('nav-lang-tag');
    if (navLangTag) navLangTag.textContent = dict.navLangTag;

    const navMenuBtnText = document.getElementById('nav-menu-btn-text');
    if (navMenuBtnText) navMenuBtnText.textContent = dict.menuProfile;
}
