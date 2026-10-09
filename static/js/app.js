/**
 * PoshanAI (पोषण AI) Interactive Single-Page Application Logic
 * Chart.js Visualizations, Hamburger Profile Management, Food Scanner, Chatbot, & Localization
 */

// Application State
const state = {
    user: null,
    lang: 'ne', // 'ne' or 'en'
    currentScannerMode: 'samples',
    selectedSampleFilename: 'dal_bhat_tarkari.jpg',
    currentMealAnalysis: null,
    samplesList: [],
    allFoods: [],
    cameraStream: null,
    charts: {
        macrosPie: null,
        caloriesBar: null,
        micronutrientsBar: null
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
        dashBadge: "✨ व्यक्तिगत पोषण केन्द्र",
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
        dashBadge: "✨ Personal Nutrition Center",
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
    // Check local storage for persistent session
    const savedUser = localStorage.getItem('poshan_user');
    const savedLang = localStorage.getItem('poshan_lang');
    if (savedLang) state.lang = savedLang;

    if (savedUser) {
        try {
            state.user = JSON.parse(savedUser);
            showAppScreen();
        } catch (e) {
            showLoginScreen();
        }
    } else {
        showLoginScreen();
    }

    await loadSamples();
    await loadFoods();
    applyLanguage();
    lucide.createIcons();
});

// =========================================================
// SCREEN ROUTING: LOGIN VS MAIN APP
// =========================================================
function showLoginScreen() {
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('app-screen').classList.add('hidden');
}

function showAppScreen() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('app-screen').classList.remove('hidden');
    updateUserInterface();
    switchNav('dashboard');
    lucide.createIcons();
}

function handleLogout() {
    localStorage.removeItem('poshan_user');
    state.user = null;
    toggleHamburgerDrawer(false);
    showLoginScreen();
}

// =========================================================
// AUTHENTICATION / ONBOARDING
// =========================================================
async function handleLoginSubmit(event) {
    event.preventDefault();
    const name = document.getElementById('login-name').value.trim() || 'प्रयोगकर्ता';
    const age = parseInt(document.getElementById('login-age').value) || 24;
    const sex = document.getElementById('login-sex').value;
    const height = parseFloat(document.getElementById('login-height').value) || 170;
    const weight = parseFloat(document.getElementById('login-weight').value) || 62;
    const activity = document.getElementById('login-activity').value;
    const goal = document.getElementById('login-goal').value;

    const payload = {
        name,
        age_years: age,
        sex,
        height_cm: height,
        weight_kg: weight,
        activity_level: activity,
        goal
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
        alert('त्रुटि: लगइन गर्न सकिएन।');
    }
}

async function handleQuickDemoLogin() {
    const payload = {
        name: state.lang === 'ne' ? 'बैभव (अतिथि)' : 'Baibhav (Guest)',
        age_years: 24,
        sex: 'male',
        height_cm: 170,
        weight_kg: 62,
        activity_level: 'moderate',
        goal: 'maintain'
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
        alert('Could not start guest demo.');
    }
}

// =========================================================
// HAMBURGER MENU & USER METRICS DRAWER
// =========================================================
function toggleHamburgerDrawer(forceState) {
    const backdrop = document.getElementById('drawer-backdrop');
    const panel = document.getElementById('drawer-panel');
    const isOpen = panel.classList.contains('open');
    const shouldOpen = forceState !== undefined ? forceState : !isOpen;

    if (shouldOpen) {
        backdrop.classList.add('open');
        panel.classList.add('open');
    } else {
        backdrop.classList.remove('open');
        panel.classList.remove('open');
    }
}

function updateUserInterface() {
    if (!state.user) return;
    const { name, profile, assessment } = state.user;
    const isNe = state.lang === 'ne';

    // Top greeting & drawer
    document.getElementById('drawer-user-name').textContent = name;
    document.getElementById('drawer-user-initial').textContent = name.charAt(0);
    document.getElementById('drawer-user-specs').textContent = 
        `${profile.age_years} ${isNe ? 'वर्ष' : 'yrs'} • ${profile.sex === 'male' ? (isNe ? 'पुरुष' : 'Male') : (isNe ? 'महिला' : 'Female')} • ${profile.height_cm} cm • ${profile.weight_kg} kg`;

    // BMI Badge in Drawer
    const bmiBadge = document.getElementById('drawer-bmi-badge');
    const bmiCatText = isNe ? assessment.bmi_category.category_ne : assessment.bmi_category.category_en;
    bmiBadge.textContent = `${assessment.bmi} (${bmiCatText})`;
    if (assessment.bmi_category.is_malnourished) {
        bmiBadge.className = 'px-2.5 py-0.5 rounded-full font-bold bg-red-100 text-red-700';
    } else if (assessment.bmi < 23.0) {
        bmiBadge.className = 'px-2.5 py-0.5 rounded-full font-bold bg-green-100 text-green-700';
    } else {
        bmiBadge.className = 'px-2.5 py-0.5 rounded-full font-bold bg-amber-100 text-amber-700';
    }

    // Drawer metabolic stats
    document.getElementById('drawer-bmr-val').textContent = `${assessment.bmr_kcal} kcal`;
    document.getElementById('drawer-tdee-val').textContent = `${assessment.tdee_kcal} kcal`;
    document.getElementById('drawer-target-cal').textContent = `${assessment.target_daily.calories} kcal`;
    document.getElementById('drawer-target-pro').textContent = `${assessment.target_daily.protein_g} g (${assessment.protein_per_kg} g/kg)`;
    document.getElementById('drawer-water-val').textContent = `${assessment.target_daily.water_liters} L`;

    // Dashboard Banner & Stat Cards
    document.getElementById('dash-greeting').textContent = `${isNe ? 'नमस्ते, ' : 'Welcome, '}${name}!`;
    document.getElementById('dash-bmr-text').textContent = `${assessment.bmr_kcal} kcal`;
    document.getElementById('dash-target-text').textContent = `${assessment.target_daily.calories} kcal`;
    document.getElementById('dash-pro-text').textContent = `${assessment.target_daily.protein_g}g ${isNe ? 'प्रोटिन' : 'protein'}`;

    document.getElementById('stat-bmi').textContent = assessment.bmi;
    document.getElementById('stat-bmi-cat').textContent = bmiCatText;
    document.getElementById('stat-bmr').textContent = assessment.bmr_kcal;
    document.getElementById('stat-tdee').textContent = assessment.tdee_kcal;
    document.getElementById('stat-protein').textContent = assessment.target_daily.protein_g;

    // Status quote
    const quoteEl = document.getElementById('info-status-quote');
    const notes = isNe ? assessment.clinical_notes_ne : assessment.clinical_notes_en;
    if (notes && notes.length > 0) {
        quoteEl.textContent = notes[0];
    }
}

// Edit Profile Modal
function openEditProfileModal() {
    if (!state.user) return;
    const { profile } = state.user;
    document.getElementById('edit-height').value = profile.height_cm;
    document.getElementById('edit-weight').value = profile.weight_kg;
    document.getElementById('edit-activity').value = profile.activity_level;
    document.getElementById('edit-goal').value = profile.goal;
    document.getElementById('modal-edit-profile').classList.remove('hidden');
}

function closeEditProfileModal() {
    document.getElementById('modal-edit-profile').classList.add('hidden');
}

async function handleEditProfileSubmit(event) {
    event.preventDefault();
    if (!state.user) return;
    const height = parseFloat(document.getElementById('edit-height').value);
    const weight = parseFloat(document.getElementById('edit-weight').value);
    const activity = document.getElementById('edit-activity').value;
    const goal = document.getElementById('edit-goal').value;

    const updatedProfile = {
        ...state.user.profile,
        height_cm: height,
        weight_kg: weight,
        activity_level: activity,
        goal: goal
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
            // If meal is already displayed, refresh bar charts
            if (state.currentMealAnalysis) {
                renderCaloriesBarChart(state.currentMealAnalysis.meal, state.user.assessment);
            }
        }
    } catch (e) {
        alert('Could not update profile.');
    }
}

// =========================================================
// SECTION NAVIGATION
// =========================================================
function switchNav(sectionName) {
    const sections = ['dashboard', 'scanner', 'chat', 'explorer'];
    sections.forEach(sec => {
        const el = document.getElementById(`view-${sec}`);
        const btn = document.getElementById(`nav-btn-${sec}`);
        if (sec === sectionName) {
            el.classList.remove('hidden');
            if (btn) btn.classList.add('active');
        } else {
            el.classList.add('hidden');
            if (btn) btn.classList.remove('active');
        }
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =========================================================
// FOOD SCANNER & SAMPLES
// =========================================================
async function loadSamples() {
    try {
        const res = await fetch('/api/samples');
        const data = await res.json();
        if (data.status === 'success') {
            state.samplesList = data.samples;
            renderSampleCards();
        }
    } catch (e) {
        console.error('Failed to load samples:', e);
    }
}

function renderSampleCards() {
    const container = document.getElementById('sample-cards-container');
    if (!container) return;
    const isNe = state.lang === 'ne';

    container.innerHTML = state.samplesList.map(s => `
        <div onclick="selectSample('${s.filename}')" class="p-2.5 rounded-xl border-2 ${state.selectedSampleFilename === s.filename ? 'border-red-600 bg-red-50/50' : 'border-slate-200 bg-white hover:border-slate-300'} cursor-pointer transition shadow-sm text-center">
            <img src="/static/sample_images/${s.filename}" alt="${s.name_en}" class="w-full h-24 object-cover rounded-lg mb-2">
            <h4 class="font-bold text-xs text-slate-800 line-clamp-1">${isNe ? s.name_ne : s.name_en}</h4>
            <p class="text-[10px] text-slate-500 line-clamp-1 mt-0.5">${isNe ? s.description_ne : s.description_en}</p>
        </div>
    `).join('');
}

function selectSample(filename) {
    state.selectedSampleFilename = filename;
    renderSampleCards();
}

function switchScannerMode(mode) {
    state.currentScannerMode = mode;
    ['samples', 'upload', 'camera'].forEach(m => {
        const el = document.getElementById(`mode-${m}`);
        const tab = document.getElementById(`tab-scan-${m}`);
        if (m === mode) {
            el.classList.remove('hidden');
            tab.className = 'py-2.5 px-4 text-xs font-bold border-b-2 border-red-600 text-red-600 transition flex items-center gap-1.5';
        } else {
            el.classList.add('hidden');
            tab.className = 'py-2.5 px-4 text-xs font-bold border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center gap-1.5';
        }
    });

    if (mode !== 'camera' && state.cameraStream) {
        state.cameraStream.getTracks().forEach(track => track.stop());
        state.cameraStream = null;
    }
}

// Upload Handling
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        executeMealAnalysisWithFile(file);
    }
}

// Camera Handling
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        state.cameraStream = stream;
        const video = document.getElementById('camera-stream');
        video.srcObject = stream;
        video.classList.remove('hidden');
        document.getElementById('camera-placeholder').classList.add('hidden');
    } catch (e) {
        alert('क्यामेरा खोल्न सकिएन। कृपया अनुमति दिनुहोस्।');
    }
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

// =========================================================
// RENDER ANALYSIS RESULTS & CHART.JS
// =========================================================
function renderAnalysisResults(data, imageUrl) {
    state.currentMealAnalysis = data;
    const isNe = state.lang === 'ne';
    const { recognition, meal, evaluation, assessment } = data;

    // Show container
    const container = document.getElementById('analysis-results');
    container.classList.remove('hidden');

    // Photo & titles
    document.getElementById('res-dish-img').src = imageUrl;
    document.getElementById('res-dish-title').textContent = isNe ? recognition.dish_title_ne : recognition.dish_title_en;
    document.getElementById('res-dish-desc').textContent = isNe ? recognition.summary_ne : recognition.summary_en;

    // Totals banner
    document.getElementById('res-tot-cal').textContent = meal.totals.calories;
    document.getElementById('res-tot-pro').textContent = meal.totals.protein_g;
    document.getElementById('res-tot-carb').textContent = meal.totals.carbs_g;
    document.getElementById('res-tot-fat').textContent = meal.totals.fat_g;

    // Detected Items with Range Sliders
    const itemsContainer = document.getElementById('detected-items-container');
    itemsContainer.innerHTML = recognition.items.map((item, idx) => `
        <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
            <div class="flex items-center justify-between text-xs font-bold text-slate-800">
                <span>${isNe ? item.name_ne : item.name_en}</span>
                <span id="item-weight-lbl-${idx}" class="text-red-600">${item.estimated_weight_g} g</span>
            </div>
            <input type="range" min="20" max="500" step="10" value="${item.estimated_weight_g}" 
                data-food-id="${item.food_id_guess}" data-idx="${idx}"
                oninput="document.getElementById('item-weight-lbl-${idx}').textContent = this.value + ' g'"
                class="w-full mt-1.5 accent-red-600 cursor-pointer">
        </div>
    `).join('');

    // Malnutrition Verdict Card
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

    // Flags
    const flagsList = document.getElementById('res-flags-list');
    flagsList.innerHTML = evaluation.malnutrition_flags.map(f => `
        <div class="flex items-start gap-1.5 text-amber-800 font-medium">
            <span>⚠️</span>
            <span>${isNe ? f.message_ne : f.message_en}</span>
        </div>
    `).join('');

    // Local additions
    const additionsList = document.getElementById('res-additions-list');
    const additions = isNe ? evaluation.suggested_local_additions_ne : evaluation.suggested_local_additions_en;
    additionsList.innerHTML = additions.map(add => `<li>${add}</li>`).join('');

    // RENDER INTERACTIVE CHART.JS CHARTS!
    renderMacrosPieChart(meal);
    renderCaloriesBarChart(meal, assessment || (state.user ? state.user.assessment : null));
    renderMicronutrientsBarChart(meal, assessment || (state.user ? state.user.assessment : null));

    container.scrollIntoView({ behavior: 'smooth' });
}

// Recalculate Meal when user adjusts sliders
async function recalculateCurrentMeal() {
    const sliders = document.querySelectorAll('#detected-items-container input[type="range"]');
    const portions = Array.from(sliders).map(slider => ({
        food_id: slider.getAttribute('data-food-id'),
        weight_g: parseFloat(slider.value)
    }));

    try {
        const res = await fetch('/api/meal/recalculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                portions,
                custom_profile: state.user ? state.user.profile : null
            })
        });
        const data = await res.json();
        if (data.status === 'success') {
            state.currentMealAnalysis.meal = data.meal;
            state.currentMealAnalysis.evaluation = data.evaluation;
            renderAnalysisResults(state.currentMealAnalysis, document.getElementById('res-dish-img').src);
        }
    } catch (e) {
        alert('पुनर्गणना असफल भयो।');
    }
}

// ---------------------------------------------------------
// CHART 1: Macronutrient Doughnut / Pie Chart
// ---------------------------------------------------------
function renderMacrosPieChart(meal) {
    const ctx = document.getElementById('chart-macros-pie').getContext('2d');
    if (state.charts.macrosPie) state.charts.macrosPie.destroy();

    const isNe = state.lang === 'ne';
    const carbsLabel = isNe ? 'कार्बोहाइड्रेट (Carbs)' : 'Carbohydrates';
    const proLabel = isNe ? 'प्रोटिन (Protein)' : 'Protein';
    const fatLabel = isNe ? 'चिल्लो (Fat)' : 'Fats';

    state.charts.macrosPie = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [carbsLabel, proLabel, fatLabel],
            datasets: [{
                data: [meal.carb_calorie_pct, meal.protein_calorie_pct, meal.fat_calorie_pct],
                backgroundColor: ['#f97316', '#dc2626', '#eab308'],
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, font: { size: 11, family: 'Poppins' } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}: ${context.raw}% of energy`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// ---------------------------------------------------------
// CHART 2: Calorie & BMR Comparison Bar Graph
// ---------------------------------------------------------
function renderCaloriesBarChart(meal, assessment) {
    const ctx = document.getElementById('chart-calories-bar').getContext('2d');
    if (state.charts.caloriesBar) state.charts.caloriesBar.destroy();

    const isNe = state.lang === 'ne';
    const mealLabel = isNe ? 'यो खाना (Meal)' : 'Scanned Meal';
    const bmrLabel = isNe ? 'आधारभूत BMR' : 'Resting BMR';
    const tdeeLabel = isNe ? 'कुल दैनिक TDEE' : 'Daily TDEE';

    const bmrVal = assessment ? assessment.bmr_kcal : 1550;
    const tdeeVal = assessment ? assessment.tdee_kcal : 2400;

    state.charts.caloriesBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [mealLabel, bmrLabel, tdeeLabel],
            datasets: [{
                label: isNe ? 'क्यालोरी (kcal)' : 'Calories (kcal)',
                data: [meal.totals.calories, bmrVal, tdeeVal],
                backgroundColor: ['#dc2626', '#f97316', '#16a34a'],
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
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// ---------------------------------------------------------
// CHART 3: Micronutrient RDA Fulfillment Bar Graph
// ---------------------------------------------------------
function renderMicronutrientsBarChart(meal, assessment) {
    const ctx = document.getElementById('chart-micronutrients-bar').getContext('2d');
    if (state.charts.micronutrientsBar) state.charts.micronutrientsBar.destroy();

    const targets = assessment ? assessment.target_daily : {
        protein_g: 70,
        iron_mg: 15,
        calcium_mg: 1000,
        vitamin_a_mcg: 800
    };

    const isNe = state.lang === 'ne';
    const labels = [
        isNe ? 'प्रोटिन (Protein)' : 'Protein',
        isNe ? 'आइरन (Iron)' : 'Iron',
        isNe ? 'क्याल्सियम (Calcium)' : 'Calcium',
        isNe ? 'भिटामिन ए (Vit A)' : 'Vitamin A',
        isNe ? 'फाइबर (Fiber)' : 'Fiber'
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
                backgroundColor: values.map(v => v >= 70 ? '#16a34a' : (v >= 35 ? '#f59e0b' : '#ef4444')),
                borderRadius: 6,
                barThickness: 16
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bars
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    max: 120,
                    ticks: { callback: v => v + '%' },
                    grid: { color: '#f1f5f9' }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.raw}% ${isNe ? 'दैनिक आवश्यकता पूरा' : 'of daily requirement'}`
                    }
                }
            }
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

    // Append User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'flex items-start justify-end gap-3';
    userDiv.innerHTML = `
        <div class="chat-bubble-user p-3.5 text-xs sm:text-sm max-w-[85%] shadow-sm">
            <p>${msg}</p>
        </div>
        <div class="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center flex-shrink-0 font-bold text-xs">
            ${state.user ? state.user.name.charAt(0) : 'म'}
        </div>
    `;
    container.appendChild(userDiv);
    container.scrollTop = container.scrollHeight;

    // Append Typing Animation
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'flex items-start gap-3';
    typingDiv.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0 font-bold text-sm">
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

        // Remove typing
        const t = document.getElementById('typing-indicator');
        if (t) t.remove();

        // Append Bot Reply
        const botDiv = document.createElement('div');
        botDiv.className = 'flex items-start gap-3';
        botDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0 font-bold text-sm">
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
                <span class="text-xs font-black text-red-600 px-2 py-0.5 rounded-md bg-red-50">${food.per_serving.calories} kcal</span>
            </div>
            <p class="text-xs text-slate-600 line-clamp-2">${isNe ? food.malnutrition_benefits_ne : food.malnutrition_benefits}</p>
            
            <div class="grid grid-cols-3 gap-1 text-center bg-slate-50 p-2 rounded-lg text-[11px]">
                <div><span class="text-slate-400 block">प्रोटिन</span><strong class="text-orange-600">${food.per_serving.protein_g}g</strong></div>
                <div><span class="text-slate-400 block">कार्ब्स</span><strong class="text-amber-600">${food.per_serving.carbs_g}g</strong></div>
                <div><span class="text-slate-400 block">आइरन</span><strong class="text-emerald-600">${food.per_serving.iron_mg}mg</strong></div>
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
    pills.forEach(p => p.classList.remove('bg-red-600', 'text-white'));
    event.target.classList.add('bg-red-600', 'text-white');

    if (category === 'all') {
        renderFoodsGrid(state.allFoods);
    } else {
        const filtered = state.allFoods.filter(f => f.tags.includes(category));
        renderFoodsGrid(filtered);
    }
}

// =========================================================
// BILINGUAL LOCALIZATION TOGGLE
// =========================================================
function toggleLanguage() {
    state.lang = state.lang === 'ne' ? 'en' : 'ne';
    localStorage.setItem('poshan_lang', state.lang);
    applyLanguage();
}

function applyLanguage() {
    const isNe = state.lang === 'ne';
    const dict = isNe ? i18n.ne : i18n.en;

    // Login screen
    document.getElementById('login-title').textContent = dict.loginTitle;
    document.getElementById('login-subtitle').textContent = dict.loginSubtitle;
    document.getElementById('login-lang-label').textContent = dict.loginLangLabel;

    // Navbar & Drawer
    document.getElementById('nav-lang-tag').textContent = dict.navLangTag;
    document.getElementById('nav-menu-btn-text').textContent = dict.menuProfile;
    document.getElementById('drawer-title').textContent = dict.drawerTitle;
    document.getElementById('drawer-metabolic-title').textContent = dict.metabolicTitle;
    document.getElementById('drawer-nav-title').textContent = dict.navTitle;
    document.getElementById('btn-edit-profile-text').textContent = dict.btnEditProfile;
    document.getElementById('btn-logout-text').textContent = dict.btnLogout;

    // Navigation pills
    document.querySelectorAll('.nav-text-dashboard').forEach(el => el.textContent = isNe ? 'डैशबोर्ड' : 'Dashboard');
    document.querySelectorAll('.nav-text-scanner').forEach(el => el.textContent = isNe ? 'खाना स्क्यानर' : 'Food Scanner');
    document.querySelectorAll('.nav-text-chat').forEach(el => el.textContent = isNe ? 'पोषण साथी (AI)' : 'Poshan Saathi AI');
    document.querySelectorAll('.nav-text-explorer').forEach(el => el.textContent = isNe ? 'रैथाने ज्ञानकोष' : 'Encyclopaedia');

    // Dashboard
    document.getElementById('dash-badge').textContent = dict.dashBadge;
    document.getElementById('dash-btn-scan').textContent = dict.dashBtnScan;
    document.getElementById('dash-btn-chat').textContent = dict.dashBtnChat;
    document.getElementById('info-plate-title').textContent = dict.infoPlateTitle;
    document.getElementById('info-plate-sub').textContent = dict.infoPlateSub;
    document.getElementById('info-meter-title').textContent = dict.infoMeterTitle;
    document.getElementById('info-meter-sub').textContent = dict.infoMeterSub;

    // Scanner
    document.getElementById('scan-head-title').textContent = dict.scanTitle;
    document.getElementById('scan-head-sub').textContent = dict.scanSub;
    document.getElementById('tab-samples-text').textContent = dict.tabSamples;
    document.getElementById('tab-upload-text').textContent = dict.tabUpload;
    document.getElementById('tab-camera-text').textContent = dict.tabCamera;
    document.getElementById('sample-pick-lbl').textContent = dict.samplePickLbl;
    document.getElementById('upload-prompt-text').textContent = dict.uploadPrompt;
    document.getElementById('btn-analyze-text').textContent = dict.btnAnalyze;
    document.getElementById('chart-pie-title').textContent = dict.chartPieTitle;
    document.getElementById('chart-bar-title').textContent = dict.chartBarTitle;
    document.getElementById('chart-micro-title').textContent = dict.chartMicroTitle;

    // Chat
    document.getElementById('chat-title').textContent = dict.chatTitle;
    document.getElementById('chat-sub').textContent = dict.chatSub;
    document.getElementById('chat-initial-greeting').innerHTML = dict.chatGreeting;

    // Explorer
    document.getElementById('exp-title').textContent = dict.expTitle;
    document.getElementById('exp-sub').textContent = dict.expSub;

    // Re-render components with localized strings
    renderSampleCards();
    if (state.allFoods.length > 0) renderFoodsGrid(state.allFoods);
    if (state.user) updateUserInterface();
    if (state.currentMealAnalysis) {
        renderAnalysisResults(state.currentMealAnalysis, document.getElementById('res-dish-img').src);
    }
}
