"""
KhanaAI (खाना AI) - Open-Source Nepali Nutrition & Malnutrition Advisory Platform
Built for Hacktoberfest | Powered by Gemma & Open AI standards
Team BubbleSort
"""

from __future__ import annotations
import os
from pathlib import Path
from PIL import Image
import streamlit as st

from core.bmr_calculator import (
    UserProfile,
    BiologicalSex,
    ActivityLevel,
    HealthGoal,
    assess_nutrition,
    calculate_bmi,
)
from core.nutrition_db import (
    get_nutrition_db,
    MealItemPortion,
    FoodItem,
)
from core.vision_engine import analyze_food_image
from core.advisor_engine import (
    evaluate_meal_against_bmr,
    PoshanChatbot,
)

# Page configuration
st.set_page_config(
    page_title="KhanaAI - खाना AI",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #b91c1c 0%, #dc2626 50%, #ea580c 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        color: white !important;
    }
    .main-header p {
        margin-top: 8px;
        margin-bottom: 0;
        font-size: 1.05rem;
        opacity: 0.95;
    }
    .badge-bar {
        margin-top: 12px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .badge {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(4px);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #b91c1c;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #4b5563;
        font-weight: 500;
    }
    .verdict-box {
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
    .verdict-good {
        background-color: #ecfdf5;
        border-left: 5px solid #10b981;
    }
    .verdict-warn {
        background-color: #fffbeb;
        border-left: 5px solid #f59e0b;
    }
    .verdict-alert {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load Database
db = get_nutrition_db()
SAMPLES_DIR = Path(__file__).resolve().parent / "static" / "sample_images"

# Session State Initialization
if "lang" not in st.session_state:
    st.session_state.lang = "ne"  # Default to Nepali

if "user_profile" not in st.session_state:
    st.session_state.user_profile = UserProfile(
        age_years=24,
        sex=BiologicalSex.MALE,
        height_cm=170.0,
        weight_kg=62.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )

if "assessment" not in st.session_state:
    st.session_state.assessment = assess_nutrition(st.session_state.user_profile)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "analyzed_meal" not in st.session_state:
    st.session_state.analyzed_meal = None

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None

# Sidebar Controls
with st.sidebar:
    st.image("https://raw.githubusercontent.com/google/gemma_pytorch/main/docs/gemma_logo.png", width=120) if False else None
    st.markdown("### 🌐 भाषा छनौट / Language")
    lang_choice = st.radio(
        "UI Language",
        options=["🇳🇵 नेपाली (Nepali)", "🇬🇧 English"],
        index=0 if st.session_state.lang == "ne" else 1,
        label_visibility="collapsed",
    )
    st.session_state.lang = "ne" if "नेपाली" in lang_choice else "en"
    lang = st.session_state.lang

    st.markdown("---")
    st.markdown("### ⚙️ AI सेटिङ / Model Settings")
    api_key_input = st.text_input(
        "Google AI Studio / Gemma Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Optional: KhanaAI works 100% offline with its built-in Nepali Food Knowledge Base if no key is entered!",
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    if api_key_input:
        st.success("🟢 Live Gemma / Gemini AI Mode Active" if lang == "en" else "🟢 प्रत्यक्ष Gemma AI मोड सक्रिय")
    else:
        st.info(
            "🔵 Zero-Cost Offline Fallback Mode Active (Ideal for hackathons without paid credits!)"
            if lang == "en"
            else "🔵 निःशुल्क अफलाइन ज्ञानकोष मोड सक्रिय (कुनै शुल्क लाग्दैन!)"
        )

    st.markdown("---")
    st.markdown(
        "**Hacktoberfest 2026**\n\n"
        "🇳🇵 Dedicated to tackling malnutrition & promoting traditional indigenous superfoods in Nepal."
    )

# Header Banner
header_title = (
    "KhanaAI: खाना AI" if lang == "ne" else "KhanaAI - Nepali Nutrition & Malnutrition Prevention"
)
header_sub = (
    "नेपाली खानाको फोटोबाट क्यालोरी र पोषक तत्व पहिचान | BMR अनुसार व्यक्तिगत पोषण सल्लाह"
    if lang == "ne"
    else "Computer Vision Food Recognition & Clinical BMR/TDEE Malnutrition Advisory for Nepali Diets"
)

st.markdown(
    f"""
    <div class="main-header">
        <h1>🍲 {header_title}</h1>
        <p>{header_sub}</p>
        <div class="badge-bar">
            <span class="badge">🎃 Hacktoberfest 2026</span>
            <span class="badge">🤖 Open-Source AI</span>
            <span class="badge">🧠 Gemma Multimodal</span>
            <span class="badge">🩺 WHO South Asian Standard</span>
            <span class="badge">🇳🇵 100% Indigenous Knowledge</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tabs
tab_profile, tab_scanner, tab_chatbot, tab_explorer = st.tabs(
    [
        "👤 १. स्वास्थ्य प्रोफाइल र BMR मापक" if lang == "ne" else "👤 1. Health Profile & BMR",
        "📸 २. खाना स्क्यानर र विश्लेषण" if lang == "ne" else "📸 2. Food Scanner & Nutrition",
        "💬 ३. पोषण साथी (AI सल्लाहकार)" if lang == "ne" else "💬 3. Poshan Saathi (AI Chat)",
        "📖 ४. रैथाने खाना ज्ञानकोष" if lang == "ne" else "📖 4. Nepali Foods Explorer",
    ]
)

# ==========================================================
# TAB 1: USER PROFILE & BMR/TDEE CALCULATOR
# ==========================================================
with tab_profile:
    st.subheader("व्यक्तिगत शारीरिक विवरण र दैनिक आवश्यकता" if lang == "ne" else "Personal Metrics & Daily Energy Targets")
    st.caption(
        "तपाईंको उमेर, उचाइ, तौल र दैनिक परिश्रम अनुसार शरीरलाई चाहिने आधारभूत क्यालोरी (BMR) र कुल ऊर्जा (TDEE) गणना गरिन्छ।"
        if lang == "ne"
        else "Clinical Mifflin-St Jeor formula calculating your Basal Metabolic Rate and energy expenditure."
    )

    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        age = st.number_input(
            "उमेर (वर्ष) / Age" if lang == "ne" else "Age (Years)",
            min_value=5,
            max_value=110,
            value=st.session_state.user_profile.age_years,
        )
        sex_opts = (
            ["पुरुष (Male)", "महिला (Female)"]
            if lang == "ne"
            else ["Male", "Female"]
        )
        sex_sel = st.selectbox(
            "लिङ्ग / Biological Sex",
            options=sex_opts,
            index=0 if st.session_state.user_profile.sex == BiologicalSex.MALE else 1,
        )
        sex_val = BiologicalSex.MALE if "Male" in sex_sel or "पुरुष" in sex_sel else BiologicalSex.FEMALE

    with col_in2:
        height = st.number_input(
            "उचाइ (से.मी.) / Height (cm)",
            min_value=60.0,
            max_value=230.0,
            value=st.session_state.user_profile.height_cm,
            step=1.0,
        )
        weight = st.number_input(
            "तौल (के.जी.) / Weight (kg)",
            min_value=15.0,
            max_value=200.0,
            value=st.session_state.user_profile.weight_kg,
            step=0.5,
        )

    with col_in3:
        act_mapping = {
            "न्यून शारीरिक परिश्रम (Sedentary / Desk)": ActivityLevel.SEDENTARY,
            "हल्का हिँडडुल (Light 1-3 days/wk)": ActivityLevel.LIGHT,
            "मध्यम सक्रिय / सामान्य काम (Moderate)": ActivityLevel.MODERATE,
            "धेरै परिश्रम / भारी काम वा खेल (Very Active)": ActivityLevel.VERY_ACTIVE,
            "अत्यधिक शारीरिक श्रम / भरिया वा किसान (Extra Active)": ActivityLevel.EXTRA_ACTIVE,
        }
        act_sel = st.selectbox(
            "दैनिक सक्रियता / Activity Level",
            options=list(act_mapping.keys()),
            index=2,
        )
        act_val = act_mapping[act_sel]

        goal_mapping = {
            "तौल र ऊर्जा स्थिर राख्ने (Maintain)": HealthGoal.MAINTAIN,
            "कुपोषण / दुब्लोपन हटाउने (Malnutrition Recovery)": HealthGoal.MALNUTRITION_RECOVERY,
            "तौल / बोसो घटाउने (Fat Loss)": HealthGoal.WEIGHT_LOSS,
            "मांसपेशी बढाउने (Muscle Gain)": HealthGoal.MUSCLE_GAIN,
        }
        goal_sel = st.selectbox(
            "स्वास्थ्य लक्ष्य / Goal",
            options=list(goal_mapping.keys()),
            index=0,
        )
        goal_val = goal_mapping[goal_sel]

    # Recalculate button
    if st.button("📊 गणना अपडेट गर्नुहोस् / Update Assessment", type="primary"):
        new_prof = UserProfile(
            age_years=age,
            sex=sex_val,
            height_cm=height,
            weight_kg=weight,
            activity_level=act_val,
            goal=goal_val,
        )
        st.session_state.user_profile = new_prof
        st.session_state.assessment = assess_nutrition(new_prof)
        st.success("✅ प्रोफाइल सफलतापूर्वक अपडेट भयो!" if lang == "ne" else "✅ Profile successfully updated!")

    # Display Assessment Cards
    ass = st.session_state.assessment
    st.markdown("---")

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{ass.bmi}</div>
                <div class="metric-lbl">BMI ({ass.bmi_category.category_ne if lang == 'ne' else ass.bmi_category.category_en})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{ass.bmr_kcal}</div>
                <div class="metric-lbl">BMR (आधारभूत क्यालोरी / दिन)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{ass.tdee_kcal}</div>
                <div class="metric-lbl">TDEE (कुल दैनिक खपत / दिन)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{ass.target_daily.calories}</div>
                <div class="metric-lbl">दैनिक लक्ष्य क्यालोरी / Target kcal</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Macro targets bar
    st.markdown("#### 🎯 सिफारिस गरिएको दैनिक पोषक तत्व विभाजन" if lang == "ne" else "#### 🎯 Target Daily Nutrient Allocation")
    d_col1, d_col2, d_col3, d_col4, d_col5 = st.columns(5)
    with d_col1:
        st.metric(
            label="प्रोटिन / Protein" if lang == "ne" else "Protein",
            value=f"{ass.target_daily.protein_g} g",
            delta=f"{ass.protein_per_kg} g/kg",
        )
    with d_col2:
        st.metric(
            label="कार्बोहाइड्रेट / Carbs" if lang == "ne" else "Carbohydrates",
            value=f"{ass.target_daily.carbs_g} g",
        )
    with d_col3:
        st.metric(
            label="चिल्लो / Healthy Fats" if lang == "ne" else "Fats",
            value=f"{ass.target_daily.fat_g} g",
        )
    with d_col4:
        st.metric(
            label="आइरन / Iron (RDA)" if lang == "ne" else "Iron",
            value=f"{ass.target_daily.iron_mg} mg",
        )
    with d_col5:
        st.metric(
            label="पानी / Water Minimum" if lang == "ne" else "Water Target",
            value=f"{ass.target_daily.water_liters} L",
        )

    # Clinical Notes Box
    notes = ass.clinical_notes_ne if lang == "ne" else ass.clinical_notes_en
    if notes:
        st.info("💡 **स्वास्थ्य सल्लाह (Clinical Guidance):**\n\n" + "\n".join(f"• {n}" for n in notes))


# ==========================================================
# TAB 2: FOOD SCANNER & NUTRITION ANALYZER
# ==========================================================
with tab_scanner:
    st.subheader("नेपाली खानाको तस्विर स्क्यान र विश्लेषण" if lang == "ne" else "Nepali Food Scanner & Meal Nutrition Analysis")
    st.caption(
        "खानाको फोटो अपलोड गर्नुहोस् वा तुरुन्तै परीक्षणका लागि तलका नमुना तस्विर छान्नुहोस्।"
        if lang == "ne"
        else "Upload a food image, take a camera snap, or choose a pre-loaded authentic Nepali dish sample."
    )

    # Input method selection
    input_method = st.radio(
        "छनौट गर्नुहोस् / Source",
        [
            "🖼️ नमुना तस्विरबाट परीक्षण (Quick Samples)" if lang == "ne" else "🖼️ Quick Test Samples",
            "📤 आफ्नै फोटो अपलोड (Upload Image)" if lang == "ne" else "📤 Upload My Photo",
            "📷 क्यामेराबाट खिच्ने (Take Camera Snapshot)" if lang == "ne" else "📷 Camera Snapshot",
        ],
        horizontal=True,
    )

    loaded_image = None
    image_hint = None

    if "Quick Samples" in input_method or "नमुना" in input_method:
        sample_options = {
            "दाल भात तरकारी थाली (Dal Bhat Tarkari)": "dal_bhat_tarkari.jpg",
            "कुखुराको म:म: (Chicken Momo)": "momo_plate.jpg",
            "कोदोको ढिँडो र गुन्द्रुक (Millet Dhindo & Gundruk)": "dhindo_gundruk.jpg",
            "क्वाँटी सुप (Sprouted Kwati Soup)": "kwati_soup.jpg",
            "सेल रोटी र अचार (Sel Roti Platter)": "sel_roti.jpg",
        }
        selected_sample_label = st.selectbox(
            "नमुना परिकार रोज्नुहोस् / Select Dish",
            options=list(sample_options.keys()),
        )
        sample_filename = sample_options[selected_sample_label]
        sample_path = SAMPLES_DIR / sample_filename
        if sample_path.exists():
            loaded_image = Image.open(sample_path)
            image_hint = sample_filename
    elif "Upload" in input_method or "अपलोड" in input_method:
        uploaded_file = st.file_uploader(
            "खानाको फोटो छान्नुहोस् (JPG, PNG)",
            type=["jpg", "jpeg", "png", "webp"],
        )
        if uploaded_file is not None:
            loaded_image = Image.open(uploaded_file)
            image_hint = uploaded_file.name
    else:
        camera_snap = st.camera_input("खानाको फोटो खिच्नुहोस् / Take Photo")
        if camera_snap is not None:
            loaded_image = Image.open(camera_snap)
            image_hint = "camera_snapshot.jpg"

    if loaded_image is not None:
        scan_col1, scan_col2 = st.columns([1, 1.2])

        with scan_col1:
            st.image(loaded_image, caption="स्क्यान गरिएको परिकार / Scanned Plate", use_container_width=True)

            if st.button("🔍 खाना पहिचान र पोषण विश्लेषण गर्नुहोस् / Analyze Meal", type="primary", use_container_width=True):
                with st.spinner("AI द्वारा नेपाली परिकार पहिचान गरिँदैछ..." if lang == "ne" else "Analyzing meal with PoshanAI vision engine..."):
                    recognition_res = analyze_food_image(
                        loaded_image,
                        api_key=os.getenv("GEMINI_API_KEY"),
                        image_name_hint=image_hint,
                    )
                    st.session_state["recognition_res"] = recognition_res

                    # Convert detected items into meal portions
                    portions = [
                        MealItemPortion(
                            food_id=item.food_id_guess,
                            weight_g=item.estimated_weight_g,
                            notes=item.notes,
                        )
                        for item in recognition_res.items
                    ]
                    meal_sum = db.calculate_meal(portions)
                    st.session_state.analyzed_meal = meal_sum
                    st.session_state.evaluation = evaluate_meal_against_bmr(
                        meal_sum, st.session_state.assessment
                    )

        with scan_col2:
            if "recognition_res" in st.session_state and st.session_state.analyzed_meal is not None:
                rec = st.session_state["recognition_res"]
                meal = st.session_state.analyzed_meal
                eval_res = st.session_state.evaluation

                st.markdown(f"### {rec.dish_title_ne if lang == 'ne' else rec.dish_title_en}")
                st.caption(rec.summary_ne if lang == 'ne' else rec.summary_en)

                st.markdown("##### 🥗 पहिचान गरिएका परिकारहरू / Detected Components:")
                for it in rec.items:
                    st.markdown(
                        f"• **{it.name_ne if lang == 'ne' else it.name_en}** — `{it.estimated_weight_g} ग्राम` "
                        f"<small style='color:gray;'>({it.notes or ''})</small>",
                        unsafe_allow_html=True,
                    )

                st.markdown("---")
                # Nutritional metrics display
                st.markdown("##### 📊 पोषक तत्व विवरण / Nutrition Totals:")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("क्यालोरी / Energy", f"{meal.totals.calories} kcal")
                c2.metric("प्रोटिन / Protein", f"{meal.totals.protein_g} g")
                c3.metric("कार्ब्स / Carbs", f"{meal.totals.carbs_g} g")
                c4.metric("चिल्लो / Fat", f"{meal.totals.fat_g} g")

                c5, c6, c7, c8 = st.columns(4)
                c5.metric("फाइबर / Fiber", f"{meal.totals.fiber_g} g")
                c6.metric("आइरन / Iron", f"{meal.totals.iron_mg} mg")
                c7.metric("क्याल्सियम / Calcium", f"{meal.totals.calcium_mg} mg")
                c8.metric("भिटामिन ए / Vit A", f"{meal.totals.vitamin_a_mcg} µg")

                # Progress bars for macro balance
                st.markdown("##### ⚖️ म्याक्रो सन्तुलन (क्यालोरी अनुपात):")
                st.write(f"🍞 कार्बोहाइड्रेट: **{meal.carb_calorie_pct}%** (सिफारिस: ४५-६०%)")
                st.progress(min(int(meal.carb_calorie_pct), 100))
                st.write(f"🥩 प्रोटिन: **{meal.protein_calorie_pct}%** (सिफारिस: १५-२५%)")
                st.progress(min(int(meal.protein_calorie_pct), 100))
                st.write(f"🥑 चिल्लो पदार्थ: **{meal.fat_calorie_pct}%** (सिफारिस: २०-३०%)")
                st.progress(min(int(meal.fat_calorie_pct), 100))

                # Clinical Verdict Box
                v_class = "verdict-good" if eval_res.score_out_of_10 >= 8.0 else ("verdict-warn" if eval_res.score_out_of_10 >= 6.0 else "verdict-alert")
                st.markdown(
                    f"""
                    <div class="verdict-box {v_class}">
                        <h4 style="margin:0 0 8px 0;">🏆 {eval_res.verdict_ne if lang == 'ne' else eval_res.verdict_en} (अङ्क: {eval_res.score_out_of_10}/१०)</h4>
                        <p style="margin:0;">यो खानाले तपाईंको दैनिक कुल ऊर्जाको <strong>{eval_res.calorie_share_tdee_pct}%</strong> र प्रोटिन लक्ष्यको <strong>{eval_res.protein_share_target_pct}%</strong> पूरा गर्छ।</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Malnutrition Flags
                if eval_res.malnutrition_flags:
                    st.markdown("⚠️ **ध्यान दिनुपर्ने कुराहरू (Nutrition Alerts):**")
                    for flg in eval_res.malnutrition_flags:
                        st.warning(flg.message_ne if lang == "ne" else flg.message_en)

                # Actionable Nepali additions
                if eval_res.suggested_local_additions_ne:
                    st.markdown("💡 **सस्तो र स्थानीय सुधारका उपायहरू (Affordable Local Additions):**")
                    additions = eval_res.suggested_local_additions_ne if lang == "ne" else eval_res.suggested_local_additions_en
                    for add in additions:
                        st.success(f"➕ {add}")


# ==========================================================
# TAB 3: POSHAN SAATHI CHATBOT (पोषण साथी)
# ==========================================================
with tab_chatbot:
    st.subheader("पोषण साथी (Poshan Saathi) - AI आहार परामर्शदाता" if lang == "ne" else "Poshan Saathi - AI Nutrition Consultant")
    st.caption(
        "तपाईंको BMR, तौल र खाना अनुसार व्यक्तिगत पोषण परामर्श लिनुहोस्। नेपाली वा अंग्रेजी दुवैमा सोध्न सक्नुहुन्छ।"
        if lang == "ne"
        else "Ask personalized questions regarding your BMR, dietary balance, low-cost proteins, and malnutrition solutions."
    )

    chatbot = PoshanChatbot(api_key=os.getenv("GEMINI_API_KEY"))

    # Quick Suggestion Buttons
    st.markdown("**छिटो सोध्नुहोस् / Quick Prompts:**")
    qp_col1, qp_col2, qp_col3, qp_col4 = st.columns(4)

    prompt_to_send = None
    if qp_col1.button("🔥 BMR अनुसार खाना ठीक छ?" if lang == "ne" else "🔥 Is this meal fit for my BMR?"):
        prompt_to_send = "मेरो BMR अनुसार यो खाना सन्तुलित छ कि छैन?" if lang == "ne" else "Is my current meal intake balanced for my BMR?"
    if qp_col2.button("🥚 सस्तो प्रोटिन कसरी बढाउने?" if lang == "ne" else "🥚 Cheap protein sources?"):
        prompt_to_send = "नेपालमा सस्तो र सुलभ रूपमा प्रोटिन कसरी बढाउने?" if lang == "ne" else "What are the cheapest high-protein foods in Nepal?"
    if qp_col3.button("🌱 कुपोषण र दुब्लोपन हटाउने" if lang == "ne" else "🌱 Overcome underweight?"):
        prompt_to_send = "कुपोषण र दुब्लोपन हटाउन परम्परागत नेपाली खाना के के हुन्?" if lang == "ne" else "How to overcome malnutrition with traditional Nepali foods?"
    if qp_col4.button("🩸 रगतको कमी (आइरन) बढाउन" if lang == "ne" else "🩸 Anemia & Iron foods?"):
        prompt_to_send = "रक्तअल्पता वा रगतको कमी हुन नदिन के खाने?" if lang == "ne" else "What foods prevent anemia and boost iron?"

    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # Chat input box
    chat_input = st.chat_input("पोषण सम्बन्धी कुनै पनि प्रश्न सोध्नुहोस्..." if lang == "ne" else "Ask any nutrition or diet question...")
    user_query = prompt_to_send or chat_input

    if user_query:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("पोषण साथी सोचिरहेको छ..." if lang == "ne" else "Poshan Saathi is typing..."):
                resp = chatbot.answer_question(
                    user_message=user_query,
                    user_profile=st.session_state.user_profile,
                    assessment=st.session_state.assessment,
                    language=st.session_state.lang,
                )
                st.markdown(resp)
                st.session_state.chat_history.append({"role": "assistant", "content": resp})


# ==========================================================
# TAB 4: NEPALI FOODS NUTRITION EXPLORER
# ==========================================================
with tab_explorer:
    st.subheader("रैथाने नेपाली खाना पोषण ज्ञानकोष" if lang == "ne" else "Authentic Nepali Foods Nutritional Encyclopaedia")
    st.caption(
        "नेपालका ४०+ मौलिक तथा रैथाने परिकारहरूको क्यालोरी, प्रोटिन, भिटामिन तथा कुपोषण निवारण महत्त्व हेर्नुहोस्।"
        if lang == "ne"
        else "Curated database of traditional dishes based on the Food Composition Table for Nepal."
    )

    ex_col1, ex_col2 = st.columns([2, 1])
    with ex_col1:
        search_query = st.text_input(
            "खाना खोज्नुहोस् / Search food",
            placeholder="उदा: ढिँडो, म:म:, Kwati, Bhatmas, Saag...",
        )
    with ex_col2:
        tag_filter = st.selectbox(
            "विशेष वर्ग / Filter by Category",
            options=[
                "सबै (All)",
                "उच्च प्रोटिन (High Protein)",
                "रैथाने सुपरफुड (Indigenous Superfoods)",
                "आइरनयुक्त (Iron Rich)",
                "क्याल्सियमयुक्त (Calcium Rich)",
            ],
        )

    # Filter foods
    filtered_foods = db.search(search_query) if search_query else db.all_foods()
    if "उच्च प्रोटिन" in tag_filter or "High Protein" in tag_filter:
        filtered_foods = [f for f in filtered_foods if "high_protein" in f.tags or "plant_protein" in f.tags or "meat_protein" in f.tags]
    elif "रैथाने" in tag_filter or "Indigenous" in tag_filter:
        filtered_foods = [f for f in filtered_foods if "traditional_superfood" in f.tags or "malnutrition_superfood" in f.tags]
    elif "आइरनयुक्त" in tag_filter or "Iron Rich" in tag_filter:
        filtered_foods = [f for f in filtered_foods if "iron_rich" in f.tags]
    elif "क्याल्सियम" in tag_filter or "Calcium Rich" in tag_filter:
        filtered_foods = [f for f in filtered_foods if "calcium_rich" in f.tags]

    st.write(f"कुल भेटिएका परिकार: **{len(filtered_foods)}**" if lang == "ne" else f"Showing **{len(filtered_foods)}** foods")

    # Render food cards in 2 columns
    f_cols = st.columns(2)
    for idx, food in enumerate(filtered_foods):
        with f_cols[idx % 2]:
            with st.expander(f"🍲 {food.name_ne if lang == 'ne' else food.name_en} ({food.name_en})", expanded=False):
                st.write(f"**मात्रा (Serving):** {food.serving_unit}")
                st.write(f"**स्वास्थ्य महत्त्व:** {food.malnutrition_benefits_ne if lang == 'ne' else food.malnutrition_benefits}")

                # Nutritional table per 100g and per serving
                st.markdown(
                    f"""
                    | पोषक तत्व | प्रति १०० ग्राम | प्रति सर्भिंग |
                    | :--- | :---: | :---: |
                    | **क्यालोरी (Energy)** | {food.per_100g.calories} kcal | {food.per_serving.calories} kcal |
                    | **प्रोटिन (Protein)** | {food.per_100g.protein_g} g | {food.per_serving.protein_g} g |
                    | **कार्बोहाइड्रेट (Carbs)** | {food.per_100g.carbs_g} g | {food.per_serving.carbs_g} g |
                    | **चिल्लो (Fat)** | {food.per_100g.fat_g} g | {food.per_serving.fat_g} g |
                    | **फाइबर (Fiber)** | {food.per_100g.fiber_g} g | {food.per_serving.fiber_g} g |
                    | **आइरन (Iron)** | {food.per_100g.iron_mg} mg | {food.per_serving.iron_mg} mg |
                    | **क्याल्सियम (Calcium)** | {food.per_100g.calcium_mg} mg | {food.per_serving.calcium_mg} mg |
                    """
                )
                tags_str = " ".join([f"`#{t}`" for t in food.tags])
                st.markdown(f"**ट्यागहरू:** {tags_str}")
