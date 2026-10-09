"""
PoshanAI Nutrition & Malnutrition Advisor Engine (पोषण सल्लाहकार)
Evaluates meals against BMR/TDEE targets and provides actionable bilingual guidance.
"""

from __future__ import annotations
import os
from typing import List, Optional
from pydantic import BaseModel, Field

from core.bmr_calculator import UserProfile, NutritionalAssessment, assess_nutrition
from core.nutrition_db import MealSummary, Nutrients


class MalnutritionFlag(BaseModel):
    code: str
    severity: str  # "warning", "critical", "info"
    message_en: str
    message_ne: str


class MealEvaluationVerdict(BaseModel):
    score_out_of_10: float
    verdict_en: str
    verdict_ne: str
    calorie_share_tdee_pct: float
    protein_share_target_pct: float
    carb_energy_pct: float
    malnutrition_flags: List[MalnutritionFlag]
    key_positives_en: List[str]
    key_positives_ne: List[str]
    actionable_advice_en: List[str]
    actionable_advice_ne: List[str]
    suggested_local_additions_en: List[str]
    suggested_local_additions_ne: List[str]


def evaluate_meal_against_bmr(
    meal: MealSummary,
    assessment: NutritionalAssessment,
) -> MealEvaluationVerdict:
    """
    Rigorously assess a meal against the user's daily BMR, TDEE, and malnutrition screening guidelines.
    """
    tdee = assessment.tdee_kcal
    target_pro = assessment.target_daily.protein_g
    meal_cal = meal.totals.calories
    meal_pro = meal.totals.protein_g
    meal_iron = meal.totals.iron_mg
    meal_vita = meal.totals.vitamin_a_mcg

    cal_pct_tdee = round((meal_cal / (tdee or 1.0)) * 100.0, 1)
    pro_pct_target = round((meal_pro / (target_pro or 1.0)) * 100.0, 1)

    flags: List[MalnutritionFlag] = []
    positives_en: List[str] = []
    positives_ne: List[str] = []
    advice_en: List[str] = []
    advice_ne: List[str] = []
    additions_en: List[str] = []
    additions_ne: List[str] = []

    # Scoring baseline
    score = 8.0

    # 1. Carbohydrate Imbalance Check (Classic Nepali "Bhat-heavy" trap)
    # If carbs provide > 70% of energy
    if meal.carb_calorie_pct > 70.0:
        score -= 2.0
        flags.append(
            MalnutritionFlag(
                code="high_carb_ratio",
                severity="warning",
                message_en=f"Carbohydrates account for {meal.carb_calorie_pct}% of meal calories (recommended: 45-60%).",
                message_ne=f"यस खानामा कार्बोहाइड्रेट {meal.carb_calorie_pct}% छ (सिफारिस: ४५-६०%)। भातको मात्रा धेरै भयो।",
            )
        )
        advice_en.append(
            "Reduce white rice (Bhat) by roughly 25-30% and replace the volume with lentils (Dal) or green vegetables."
        )
        advice_ne.append(
            "सेतो भातको भाग २५-३०% घटाउनुहोस् र त्यसको साटो बाक्लो दाल वा हरियो सागसब्जी थप्नुहोस्।"
        )
    else:
        positives_en.append("Carbohydrate to protein balance is within healthy functional limits.")
        positives_ne.append("कार्बोहाइड्रेट र प्रोटिनको सन्तुलन उपयुक्त छ।")

    # 2. Protein Deficiency Check (Critical for stunting / muscle wasting prevention)
    # A single major meal should ideally provide at least 25-35% of daily protein target
    expected_meal_protein = target_pro * 0.30
    if meal_pro < 12.0 or pro_pct_target < 20.0:
        score -= 2.5
        flags.append(
            MalnutritionFlag(
                code="low_protein",
                severity="critical" if assessment.bmi_category.is_malnourished else "warning",
                message_en=f"Low protein content ({meal_pro}g detected; meal target is ~{round(expected_meal_protein, 1)}g). Increases risk of muscle loss and stunting.",
                message_ne=f"प्रोटिनको मात्रा निकै कम छ ({meal_pro} ग्राम मात्र; यो खानामा कम्तीमा {round(expected_meal_protein, 1)} ग्राम हुनुपर्छ)। यसले शारीरिक कमजोरी निम्त्याउँछ।",
            )
        )
        advice_en.append(
            "Prioritize affordable protein sources: add a boiled egg, thick Kwati soup, or roasted soybeans (Bhatmas)."
        )
        advice_ne.append(
            "सस्तो र प्रभावकारी प्रोटिन थप्नुहोस्: १ वटा उसिनेको अण्डा, क्वाँटीको रस वा भुटेको भटमास अनिवार्य खानुहोस्।"
        )
        additions_en.append("1 Boiled Egg (+7.2g protein, ~Rs 15)")
        additions_en.append("Sprouted Kwati Soup (+15.8g protein, rich in zinc)")
        additions_en.append("Roasted Bhatmas / Soybeans (+22.5g protein/100g)")
        additions_ne.append("१ वटा उसिनेको अण्डा (+७.२ ग्राम प्रोटिन, करिब १५ रुपैयाँ)")
        additions_ne.append("उमारेको क्वाँटीको रस (+१५.८ ग्राम प्रोटिन, जिंकसहित)")
        additions_ne.append("भुटेको भटमास खाजा (+२२.५ ग्राम प्रोटिन/१०० ग्राम)")
    else:
        score += 1.0
        positives_en.append(f"Solid protein delivery ({meal_pro}g), achieving {pro_pct_target}% of daily target.")
        positives_ne.append(f"पर्याप्त प्रोटिन ({meal_pro} ग्राम), दैनिक आवश्यकताको {pro_pct_target}% पूरा भयो।")

    # 3. Iron & Anemia Screening (Key public health challenge in Nepal)
    if meal_iron >= 4.0:
        score += 0.5
        positives_en.append(f"Excellent iron supply ({meal_iron}mg) - helps protect against nutritional anemia.")
        positives_ne.append(f"राम्रो आइरन मात्रा ({meal_iron} मि.ग्रा.) - रक्तअल्पता (रगतको कमी) बाट बचाउँछ।")
    else:
        flags.append(
            MalnutritionFlag(
                code="low_iron",
                severity="info",
                message_en="Moderate to low iron level in this meal.",
                message_ne="यस खानामा आइरनको मात्रा केही कम छ।",
            )
        )
        advice_en.append(
            "Add green leafy vegetables (Rayo or Palungo Saag) and fresh tomato achar (Vitamin C increases iron absorption)."
        )
        advice_ne.append(
            "रायो वा पालुङ्गोको हरियो साग र गोलभेँडाको अचार थप्नुहोस् (भिटामिन 'सी' ले आइरन सोस्न मद्दत गर्छ)।"
        )
        additions_en.append("Fresh Mustard/Spinach Greens (Rayo/Palungo Saag)")
        additions_ne.append("ताजा रायो वा पालुङ्गोको साग")

    # 4. Caloric Proportion Check
    if cal_pct_tdee > 60.0:
        score -= 1.0
        flags.append(
            MalnutritionFlag(
                code="heavy_meal",
                severity="warning",
                message_en=f"This single meal provides {cal_pct_tdee}% of your entire daily energy requirement ({tdee} kcal).",
                message_ne=f"यो एकै छाकले तपाईंको दिनभरको क्यालोरीको {cal_pct_tdee}% ओगटेको छ।",
            )
        )
    elif cal_pct_tdee < 15.0:
        flags.append(
            MalnutritionFlag(
                code="insufficient_calories",
                severity="info",
                message_en=f"Very low energy intake ({meal_cal} kcal = {cal_pct_tdee}% of daily TDEE). May leave you fatigued if this is a main meal.",
                message_ne=f"क्यालोरी धेरै कम छ ({meal_cal} क्यालोरी = TDEE को {cal_pct_tdee}%)। मुख्य खाना भए थप ऊर्जा आवश्यक छ।",
            )
        )

    # 5. Traditional Superfood Recognition Bonus
    if any("traditional_superfood" in item.get("notes", "") or "malnutrition_superfood" in item.get("notes", "") for item in meal.items):
        score += 1.0
        positives_en.append("Contains authentic indigenous superfoods (Millet Dhindo / Kwati / Fermented Gundruk).")
        positives_ne.append("नेपाली रैथाने सुपरफुड (कोदोको ढिँडो / क्वाँटी / गुन्द्रुक) समावेश छ।")

    # Final score clamp (1.0 to 10.0)
    final_score = max(min(round(score, 1), 10.0), 1.0)

    # Verdict titles
    if final_score >= 8.0:
        verdict_en = "Nutritious & Well-Balanced Nepali Meal"
        verdict_ne = "पौष्टिक र सन्तुलित नेपाली खाना"
    elif final_score >= 6.0:
        verdict_en = "Moderately Balanced - Needs Minor Tweaks"
        verdict_ne = "मध्यम सन्तुलित - केही सुधार आवश्यक"
    else:
        verdict_en = "Nutritional Imbalance Detected (High Carb / Low Protein)"
        verdict_ne = "असंतुलित खाना (धेरै कार्बोहाइड्रेट / कम प्रोटिन)"

    return MealEvaluationVerdict(
        score_out_of_10=final_score,
        verdict_en=verdict_en,
        verdict_ne=verdict_ne,
        calorie_share_tdee_pct=cal_pct_tdee,
        protein_share_target_pct=pro_pct_target,
        carb_energy_pct=meal.carb_calorie_pct,
        malnutrition_flags=flags,
        key_positives_en=positives_en,
        key_positives_ne=positives_ne,
        actionable_advice_en=advice_en,
        actionable_advice_ne=advice_ne,
        suggested_local_additions_en=additions_en,
        suggested_local_additions_ne=additions_ne,
    )


CHATBOT_SYSTEM_PROMPT = """
You are "Poshan Saathi" (पोषण साथी), an empathetic, culturally knowledgeable AI nutritionist and public health advocate dedicated to fighting malnutrition in Nepal.
You communicate fluently in both Nepali (नेपाली भाषा, देवनागरी) and English depending on the user's language.

Your guiding principles:
1. Ground your nutritional advice in traditional, affordable, locally accessible Nepali foods (Dal, Bhat, Tarkari, Dhindo, Kwati, Gundruk, Bhatmas, Saag, Sattu, Jaulo, Lito, Boiled Eggs, Dahi).
2. Never recommend expensive foreign supplements when affordable indigenous superfoods exist (e.g. recommend roasted Bhatmas / soybeans or Kwati instead of whey protein; recommend Rayo Saag & Achar instead of iron pills unless medically advised).
3. Always factor in the user's specific health metrics (Height, Weight, calculated BMR and TDEE, Malnutrition status).
4. Address the real challenges in Nepal: protein-energy malnutrition (PEM), child stunting, maternal anemia, and excessive white-rice consumption.
5. Tone: Respectful, encouraging, culturally warm ("नमस्ते! तपाईंको स्वास्थ्य नै हाम्रो प्राथमिकता हो").
"""


from core.config import GEMMA_API_KEY, CHAT_MODEL


class PoshanChatbot:
    """Conversational nutritional advisor with live LLM and comprehensive clinical domain knowledge."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMMA_API_KEY

    def answer_question(
        self,
        user_message: str,
        user_profile: Optional[UserProfile] = None,
        assessment: Optional[NutritionalAssessment] = None,
        meal_context: Optional[MealSummary] = None,
        language: str = "ne",  # "ne" or "en"
    ) -> str:
        """Answer user questions via live Gemini/Gemma API or intelligent clinical fallback."""
        if self.api_key and self.api_key.strip():
            try:
                return self._call_live_llm(user_message, user_profile, assessment, meal_context, language)
            except Exception as e:
                print(f"[PoshanChatbot] Live API call note: {e}. Utilizing comprehensive clinical knowledge engine.")

        return self._clinical_offline_response(user_message, user_profile, assessment, meal_context, language)

    def _call_live_llm(
        self,
        user_message: str,
        profile: Optional[UserProfile],
        assessment: Optional[NutritionalAssessment],
        meal_context: Optional[MealSummary],
        language: str,
    ) -> str:
        from google import genai

        client = genai.Client(api_key=self.api_key.strip())

        context_prompt = CHATBOT_SYSTEM_PROMPT + "\n\n"
        if profile and assessment:
            context_prompt += (
                f"User Profile: Age {profile.age_years}, Sex {profile.sex.value}, "
                f"Weight {profile.weight_kg}kg, Height {profile.height_cm}cm, "
                f"BMI {assessment.bmi} ({assessment.bmi_category.category_en}), "
                f"BMR {assessment.bmr_kcal} kcal, TDEE {assessment.tdee_kcal} kcal, "
                f"Daily Target: {assessment.target_daily.calories} kcal, Protein: {assessment.target_daily.protein_g}g.\n"
            )
        if meal_context:
            context_prompt += (
                f"Latest Meal Scanned: {meal_context.totals.calories} kcal, "
                f"Protein: {meal_context.totals.protein_g}g, Carbs: {meal_context.totals.carbs_g}g, "
                f"Fat: {meal_context.totals.fat_g}g, Iron: {meal_context.totals.iron_mg}mg.\n"
            )
        context_prompt += f"Preferred output language: {'Nepali (नेपाली - देवनागरी)' if language == 'ne' else 'English'}.\n"
        context_prompt += f"User Question: {user_message}\n"

        response = client.models.generate_content(
            model=CHAT_MODEL,
            contents=context_prompt,
        )
        return response.text or ("माफ गर्नुहोस्, जवाफ प्राप्त हुन सकेन।" if language == "ne" else "Apologies, could not generate a response.")

    def _clinical_offline_response(
        self,
        query: str,
        profile: Optional[UserProfile],
        assessment: Optional[NutritionalAssessment],
        meal: Optional[MealSummary],
        language: str,
    ) -> str:
        q = query.lower()

        # Context-aware meal question: "Is my meal good?" / "यो खाना ठीक छ?"
        if any(w in q for w in ["यो खाना", "खाना ठीक", "is this meal", "current meal", "scanned", "my food"]):
            if meal and assessment:
                cal_pct = round((meal.totals.calories / (assessment.tdee_kcal or 1)) * 100, 1)
                pro_pct = round((meal.totals.protein_g / (assessment.target_daily.protein_g or 1)) * 100, 1)
                if language == "ne":
                    status = "धेरै राम्रो र सन्तुलित" if meal.protein_calorie_pct >= 15 else "कार्बोहाइड्रेट बढी र प्रोटिन केही कम"
                    return (
                        f"📊 **तपाईंको पछिल्लो खानाको विश्लेषण:**\n\n"
                        f"• **क्यालोरी:** {meal.totals.calories} kcal (तपाईंको दैनिक TDEE को **{cal_pct}%**)\n"
                        f"• **प्रोटिन:** {meal.totals.protein_g} g (दैनिक लक्ष्यको **{pro_pct}%**)\n"
                        f"• **स्थिति:** तपाईंको खाना **{status}** छ।\n\n"
                        f"💡 **सुझाव:** यदि भात धेरै छ भने १/३ भाग घटाएर १ कचौरा बाक्लो दाल वा १ वटा उसिनेको अण्डा थप्नुहोस्!"
                    )
                else:
                    return (
                        f"📊 **Analysis of Your Scanned Meal:**\n\n"
                        f"• **Calories:** {meal.totals.calories} kcal (**{cal_pct}%** of your daily TDEE)\n"
                        f"• **Protein:** {meal.totals.protein_g} g (**{pro_pct}%** of daily protein goal)\n"
                        f"• **Carb Share:** {meal.carb_calorie_pct}% of total calories.\n\n"
                        f"💡 **Advice:** If carbohydrates exceed 65%, scale down rice by 25% and add a cup of thick lentils, Kwati, or a boiled egg!"
                    )

        # Topic: Momo (म:म:) frequency & health
        if any(w in q for w in ["momo", "म:म:", "मम"]):
            if language == "ne":
                return (
                    "🥟 **म:म: सम्बन्धी पोषण सल्लाह:**\n\n"
                    "१. **उसिनेको म:म: (Steamed Momo)** मा तेल कम हुन्छ, त्यसैले फ्राइ वा सि-म:म: भन्दा धेरै स्वस्थकर हुन्छ।\n"
                    "२. **प्रोटिन:** कुखुरा (Chicken) वा बफ म:म: (Buff Momo) मा १० पिसमा करिब २३-२६ ग्राम राम्रो प्रोटिन पाइन्छ।\n"
                    "३. **ध्यान दिनुपर्ने कुरा:** यसको बाहिरी भाग मैदा (Refined Flour) बाट बन्ने हुनाले दैनिक खानु उपयुक्त हुँदैन। हप्तामा १-२ पटक खाँदा ठीक हुन्छ।\n"
                    "४. **टमाटर-तिलको अचार** सँग खाँदा भिटामिन सी र क्याल्सियम राम्रो प्राप्त हुन्छ।"
                )
            else:
                return (
                    "🥟 **Nutrition Guidance on Momo:**\n\n"
                    "1. **Steamed vs Fried:** Steamed momo is significantly healthier as it avoids deep-frying oils.\n"
                    "2. **Protein Delivery:** 10 pieces of Chicken or Buff momo provide ~23-26g of high-quality protein.\n"
                    "3. **Refined Flour (Maida):** Because the wrappers are refined wheat flour, eating it daily can cause energy spikes. Limit to 1-2 times weekly.\n"
                    "4. **Achar Benefit:** Tomato & sesame dipping achar provides Vitamin C and healthy polyunsaturated fats."
                )

        # Topic: Rice / Bhat portion control (भात कति खाने)
        if any(w in q for w in ["भात", "rice", "bhat", "सेतो भात"]):
            if language == "ne":
                return (
                    "🍚 **नेपाली थालीमा भातको सही मात्रा:**\n\n"
                    "• धेरैजसो नेपाली थालीमा ८०% भाग भात हुन्छ, जसले गर्दा क्यालोरी बढी र प्रोटिन कम हुन्छ (कुपोषणको मुख्य कारण)।\n"
                    "• **आदर्श नियम (१:१ अनुपात):** जति कचौरा भात लिनुहुन्छ, कम्तीमा त्यति नै कचौरा बाक्लो दाल र तरकारी/साग लिनुहोस्।\n"
                    "• सेतो भातको साटो हप्तामा २-३ दिन **कोदो वा फापरको ढिँडो** वा **ताइचिन/रातो भात** खाँदा फाइबर र क्याल्सियम ३ गुणा बढी पाइन्छ।"
                )
            else:
                return (
                    "🍚 **Ideal Rice (Bhat) Portion in Nepali Meals:**\n\n"
                    "• Most traditional Nepali plates are 75-85% white rice, creating a 'Carbohydrate Trap' (high calories, deficient in protein/micronutrients).\n"
                    "• **The 1:1 Rule:** For every bowl of rice, ensure you have an equal volume of dense Dal and green vegetables.\n"
                    "• Swap white rice 2-3 times weekly with **Millet/Buckwheat Dhindo** or unpolished brown/red rice for 3x more calcium and dietary fiber."
                )

        # Topic: BMR, TDEE, Calories
        if any(w in q for w in ["bmr", "tdee", "calorie", "क्यालोरी", "कति खाने"]):
            if assessment:
                if language == "ne":
                    return (
                        f"🔥 **तपाईंको ऊर्जा मापन (BMR र TDEE):**\n\n"
                        f"• **BMR (आधारभूत क्यालोरी):** **{assessment.bmr_kcal} kcal** (शरीरलाई आरामको अवस्थामा बाँच्न चाहिने न्यूनतम ऊर्जा)\n"
                        f"• **TDEE (कुल दैनिक ऊर्जा):** **{assessment.tdee_kcal} kcal** (हिँडडुल र काम गर्दा खर्च हुने ऊर्जा)\n"
                        f"• **दैनिक लक्ष्य:** **{assessment.target_daily.calories} kcal** र **{assessment.target_daily.protein_g} ग्राम प्रोटिन**।\n"
                        f"• दिनमा २ छाक ठूलो खाना (दाल-भात) र २ पटक स्वस्थ खाजा (भटमास, चना, अण्डा, मोही) खानु उत्तम हुन्छ।"
                    )
                else:
                    return (
                        f"🔥 **Your Energy Budget (BMR & TDEE):**\n\n"
                        f"• **BMR:** **{assessment.bmr_kcal} kcal/day** (Resting metabolic energy for organ function)\n"
                        f"• **TDEE:** **{assessment.tdee_kcal} kcal/day** (Total energy expenditure including daily activities)\n"
                        f"• **Target Daily:** **{assessment.target_daily.calories} kcal** with **{assessment.target_daily.protein_g}g protein**.\n"
                        f"• Aim to distribute this across 2 balanced main meals (Dal Bhat) and 2 healthy snacks (Bhatmas, boiled eggs, fruit, Mohi)."
                    )

        # Topic: Cheap Protein (सस्तो प्रोटिन)
        if any(w in q for w in ["protein", "प्रोटिन", "मांसपेसी", "muscle", "मासु"]):
            if language == "ne":
                return (
                    "🥚 **नेपालमा सबैभन्दा सस्तो र गुणस्तरीय प्रोटिन:**\n\n"
                    "१. **भुटेको भटमास (Bhatmas):** १०० ग्राममा **२२.५ ग्राम प्रोटिन** (नेपालको सबैभन्दा सस्तो सुपरफुड)।\n"
                    "२. **उसिनेको अण्डा (Egg):** १ वटामा **७.२ ग्राम पूर्ण प्रोटिन** (करिब १५ रुपैयाँ)।\n"
                    "३. **क्वाँटी (Kwati):** उमारेको ९ थरी गेडागुडीबाट उच्च प्रोटिन, जिंक र आइरन।\n"
                    "४. **मासको दाल र बारा:** कालो दालमा प्रचुर प्रोटिन र पाचन फाइबर।\n"
                    "५. **दही र छुर्पी:** स्थानीय क्याल्सियम र दुग्ध प्रोटिन।"
                )
            else:
                return (
                    "🥚 **Top Cost-Effective Protein Sources in Nepal:**\n\n"
                    "1. **Roasted Soybeans (Bhatmas):** **22.5g protein** per 100g (~Rs 30-40)—cheaper and denser than meat!\n"
                    "2. **Boiled Eggs:** **7.2g complete protein** per egg (~Rs 15) with choline and vitamin A.\n"
                    "3. **Sprouted Kwati Soup:** 9-bean sprouted stew providing ~15.8g bioavailable plant protein.\n"
                    "4. **Black Lentils (Maas ko Dal / Bara):** High protein and soluble fiber.\n"
                    "5. **Curd (Dahi) & Chhurpi:** Indigenous dairy proteins supporting bone density."
                )

        # Topic: Malnutrition, Underweight & Stunting (कुपोषण र दुब्लोपन)
        if any(w in q for w in ["malnutrition", "कुपोषण", "दुब्लो", "weight gain", "तौल बढाउने", "stunting", "पुड्कोपन"]):
            if language == "ne":
                return (
                    "🌱 **कुपोषण र दुब्लोपन हटाउने परम्परागत नेपाली उपाय:**\n\n"
                    "• **पोषण लिटो (Lito):** भुटेको मकै, गहुँ, भटमास र चामलको पिठो मिसाएर दूध वा घिउसँग दिनहुँ खानुहोस्।\n"
                    "• **दैनिक कम्तीमा २ वटा उसिनेको अण्डा** र १ कचौरा बाक्लो गेडागुडी खानुहोस्।\n"
                    "• खानामा **१-२ चम्चा शुद्ध घिउ** मिसाउँदा क्यालोरी घनत्व सुरक्षित रूपमा बढ्छ।\n"
                    "• कमजोर बालबालिकालाई **जाउलो र क्वाँटीको रस** नियमित खुवाउनुहोस्।"
                )
            else:
                return (
                    "🌱 **Combating Underweight & Malnutrition in Nepal:**\n\n"
                    "• **Poshan Lito:** Traditional multi-grain porridge of roasted wheat, corn, rice, and roasted soybeans with milk/ghee.\n"
                    "• **2 Boiled Eggs Daily:** UNICEF and Nepal Poshan protocol for stopping linear stunting.\n"
                    "• Add **1-2 teaspoons of pure Ghee** to meals to increase caloric density safely.\n"
                    "• Offer sprouted Kwati broth and gentle Jaulo for nutrient absorption."
                )

        # Topic: Anemia, Iron deficiency (रक्तअल्पता र आइरन)
        if any(w in q for w in ["anemia", "iron", "आइरन", "रक्तअल्पता", "रगत", "कमजोरी"]):
            if language == "ne":
                return (
                    "🩸 **रगतको कमी (आइरन) हटाउने उपाय:**\n\n"
                    "१. **रायो र पालुङ्गोको हरियो साग** हप्तामा कम्तीमा ३-४ पटक अनिवार्य खानुहोस्।\n"
                    "२. **कागती वा गोलभेँडाको ताजा अचार** सागसँग खानुहोस्—भिटामिन 'सी' ले आइरन सोस्ने क्षमता ३००% बढाउँछ!\n"
                    "३. खाना खाएको १ घण्टासम्म **कालो चिया वा कफी नपिउनुहोस्**, किनकि यसले आइरन शरीरमा सोस्न रोक्छ।\n"
                    "४. खाजामा **चाकु र भुटेको कालो चना** खानुहोस्।"
                )
            else:
                return (
                    "🩸 **Combating Iron Deficiency & Anemia:**\n\n"
                    "1. Eat dark leafy greens (**Rayo / Palungo Saag**) at least 3-4 times a week.\n"
                    "2. Pair greens and lentils with Vitamin C (**Fresh Tomato Achar or Lemon**)—boosts non-heme iron absorption by up to 300%!\n"
                    "3. **Do not drink black tea/coffee** within 1 hour of meals as tannins block iron absorption.\n"
                    "4. Snack on traditional **Chaku (sugarcane molasses)** and roasted black chickpeas."
                )

        # Topic: Diabetes / Blood Sugar (मधुमेह र सुगर)
        if any(w in q for w in ["diabetes", "sugar", "मधुमेह", "सुगर", "चिनी"]):
            if language == "ne":
                return (
                    "🩺 **मधुमेह (सुगर) रोगीका लागि नेपाली खाना:**\n\n"
                    "• सेतो भातको मात्रा आधा घटाउनुहोस्।\n"
                    "• **कोदो वा फापरको ढिँडो** खानुहोस्—यसको Glycemic Index कम हुने हुनाले रगतमा चिनी छिटो बढ्न दिँदैन।\n"
                    "• **क्वाँटी र कालो चनाको तरकारी** प्रशस्त खानुहोस्।\n"
                    "• आलु र सेल रोटी जस्ता गुलियो/तारेको परिकार सीमित गर्नुहोस् र रायोको साग बढाउनुहोस्।"
                )
            else:
                return (
                    "🩺 **Diabetes Nutrition Guidelines for Nepali Diets:**\n\n"
                    "• Cut white rice portions by half to prevent glucose spikes.\n"
                    "• Substitute with **Millet or Buckwheat Dhindo** (low glycemic index and high dietary fiber).\n"
                    "• Prioritize **Kwati and Black Chickpeas (Chana)** for steady blood sugar control.\n"
                    "• Restrict potatoes, white flour, and deep-fried Sel Roti."
                )

        # Topic: Dhindo vs Rice (ढिँडो र भात)
        if any(w in q for w in ["dhindo", "ढिँडो", "फापर", "कोदो"]):
            if language == "ne":
                return (
                    "🌾 **ढिँडो किन सेतो भातभन्दा धेरै गुणा पौष्टिक छ?**\n\n"
                    "• **क्याल्सियम:** कोदोको ढिँडोमा सेतो भातभन्दा **३ गुणा बढी क्याल्सियम** हुन्छ, जसले हड्डी बलियो बनाउँछ।\n"
                    "• **फाइबर:** उच्च फाइबर हुनाले ढिलो पच्छ र दिनभर तागत दिन्छ।\n"
                    "• **मधुमेह नियन्त्रण:** फापर र कोदोले रगतमा ग्लुकोज नियन्त्रण गर्न मद्दत गर्छ।"
                )
            else:
                return (
                    "🌾 **Why Dhindo is Far Superior to White Rice:**\n\n"
                    "• **Calcium Density:** Millet Dhindo packs **3x more calcium** than polished white rice, vital for bone health and stunting prevention.\n"
                    "• **Sustained Energy:** Complex starches and fiber mean slow, steady glucose release without crashes.\n"
                    "• **Cardiometabolic Protection:** Buckwheat contains rutin, which strengthens blood vessels."
                )

        # Greetings & General Politeness
        if any(w in q for w in ["hello", "hi", "namaste", "नमस्ते", "नमस्कार", "कस्तो छ"]):
            if language == "ne":
                return (
                    "🙏 **नमस्ते! म 'पोषण साथी' हुँ।**\n\n"
                    "म तपाईंलाई नेपाली खानाको क्यालोरी, प्रोटिन, BMR सन्तुलन र कुपोषण हटाउने घरेलु उपायहरू बताउन सक्छु। "
                    "तपाईं आफ्नो खानाको बारेमा, BMR बारे वा कुनै पनि स्वास्थ्य प्रश्न सोध्न सक्नुहुन्छ!"
                )
            else:
                return (
                    "🙏 **Namaste! I am Poshan Saathi, your AI Nutritionist.**\n\n"
                    "I am here to guide you on calorie balance, BMR targets, low-cost proteins, and overcoming malnutrition using traditional Nepali foods. "
                    "How can I help your diet today?"
                )

        # Fallback intelligent answer
        if language == "ne":
            return (
                f"💡 **पोषण साथीको सल्लाह:**\n\n"
                f"तपाईंको प्रश्न ('{query}') स्वास्थ्यका लागि महत्त्वपूर्ण छ। नेपाली खानपानमा सबैभन्दा मुख्य कुरा "
                f"**दाल, भात, तरकारी र प्रोटिनको सही अनुपात (सन्तुलित थाली)** हो।\n\n"
                f"• थालीमा कम्तीमा आधा भाग हरियो साग र तरकारी हुनुपर्छ।\n"
                f"• एक चौथाइ भाग बाक्लो दाल, क्वाँटी, अण्डा वा भटमास (प्रोटिन)।\n"
                f"• बाँकी एक चौथाइ भाग मात्र भात वा ढिँडो लिनुहोस्।\n\n"
                f"के तपाईं आफ्नो BMR वा कुनै निश्चित परिकार (जस्तै म:म:, क्वाँटी, ढिँडो) बारे थप जान्न चाहनुहुन्छ?"
            )
        else:
            return (
                f"💡 **Poshan Saathi Nutritional Guidance:**\n\n"
                f"Regarding your inquiry ('{query}'): in the context of Nepali diets, the golden standard is the **Balanced Nepali Plate Rule**:\n\n"
                f"• **1/2 Plate:** Dark leafy greens (Saag) and fresh vegetables.\n"
                f"• **1/4 Plate:** High-density protein (Lentils, Sprouted Kwati, Boiled Eggs, or Soybeans).\n"
                f"• **1/4 Plate:** Whole grains (Rice, Millet Dhindo, or Roti).\n\n"
                f"Would you like advice tailored to your BMR target or a specific food item?"
            )

