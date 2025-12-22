import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="MicroNutri AI Pro", page_icon="🧬", layout="wide")

# --- CSS TASARIM ---
st.markdown("""
<style>
    .stButton button { width: 100%; background-color: #FF4B4B; color: white; border-radius: 10px; padding: 15px; border: none; font-weight: bold; }
    .stButton button:hover { background-color: #D93F3F; color: white; }
    .metric-container { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #FF4B4B; margin-bottom: 10px; }
    .nutrient-row { padding: 10px; margin: 5px 0; border-radius: 8px; border: 1px solid #eee; }
    .nutrient-perfect { background-color: #e6fffa; border-left: 5px solid #00b894; }
    .nutrient-low { background-color: #fff5f5; border-left: 5px solid #ff7675; }
    .nutrient-high { background-color: #fff0db; border-left: 5px solid #fdcb6e; }
    .step-indicator { font-size: 1.2rem; font-weight: bold; color: #555; text-align: center; padding: 10px; background-color: #eef; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def get_data():
    return pd.read_csv("foods.csv")

try:
    df = get_data()
except:
    st.error("❌ 'foods.csv' dosyası bulunamadı.")
    st.stop()

# --- KALICI HAFIZA ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "gender": "Erkek", "age": 25, "height": 175, 
        "weight": 75, "activity": "Hareketsiz", "goal": "Kilo Koru"
    }
if 'meal_state' not in st.session_state:
    st.session_state.meal_state = {
        "current_meal": "Kahvaltı", 
        "next_meal_name": "Öğle Yemeği", 
        "next_cats": [],
        "basket": []
    }

# --- GEÇİŞ FONKSİYONLARI ---
def save_profile_and_next():
    st.session_state.user_profile["gender"] = st.session_state.w_gender
    st.session_state.user_profile["age"] = st.session_state.w_age
    st.session_state.user_profile["height"] = st.session_state.w_height
    st.session_state.user_profile["weight"] = st.session_state.w_weight
    st.session_state.user_profile["activity"] = st.session_state.w_activity
    st.session_state.user_profile["goal"] = st.session_state.w_goal
    st.session_state.step += 1

def save_meal_and_next():
    current = st.session_state.w_meal_type
    st.session_state.meal_state["current_meal"] = current
    if current == "Kahvaltı":
        nxt, cats = "Öğle Yemeği", ["Çorba", "Et", "Sebze", "Bakliyat", "Tahıl"]
    elif current == "Öğle Yemeği":
        nxt, cats = "Akşam Yemeği", ["Çorba", "Sebze", "Et", "Salata", "Süt Ürünü"]
    else:
        nxt, cats = "Yarınki Kahvaltı", ["Kahvaltılık", "Süt Ürünü", "Meyve", "Kuruyemiş"]
    st.session_state.meal_state["next_meal_name"] = nxt
    st.session_state.meal_state["next_cats"] = cats
    st.session_state.step += 1

def go_back(): st.session_state.step -= 1
def restart(): 
    st.session_state.step = 1
    st.session_state.meal_state["basket"] = []

# --- SAĞLIK SÖZLÜĞÜ (YORUMLAR İÇİN) ---
nutrient_info = {
    "protein": "Kas onarımı ve bağışıklık için temeldir.",
    "fat": "Hücre zarı ve hormon üretimi için gereklidir.",
    "carbs": "Vücudun temel enerji kaynağıdır.",
    "vit_a_iu": "Göz sağlığı ve bağışıklık sistemi için kritiktir.",
    "vit_c_mg": "Antioksidandır, bağışıklığı güçlendirir, demir emilimini artırır.",
    "vit_d_iu": "Kemik sağlığı ve ruh hali için güneş vitaminidir.",
    "vit_e_mg": "Cilt sağlığı ve hücre yenilenmesi için önemlidir.",
    "calcium_mg": "Kemik ve diş yapısını korur, kas kasılmasını sağlar.",
    "iron_mg": "Kan yapımı ve oksijen taşıma için hayati önemdedir.",
    "magnesium_mg": "Kas gevşemesi ve sinir sistemi dengesi için şarttır.",
    "zinc_mg": "Bağışıklık, yara iyileşmesi ve hormon dengesi için gereklidir."
}

# --- YARDIMCI ANALİZ FONKSİYONU ---
def analyze_nutrient(label, value, target, unit, key_name):
    ratio = value / target if target > 0 else 0
    
    if ratio < 0.5:
        status_class = "nutrient-low"
        status_text = "⚠️ KRİTİK AZ"
        advice = "Çok yetersiz kaldı. Takviye edici gıdalar seçmelisin."
    elif ratio < 0.85:
        status_class = "nutrient-low"
        status_text = "📉 AZ"
        advice = "Hedefin altında, biraz daha artırabilirsin."
    elif ratio <= 1.15:
        status_class = "nutrient-perfect"
        status_text = "✅ İDEAL"
        advice = "Harika! Tam olması gereken seviyede."
    else:
        status_class = "nutrient-high"
        status_text = "📈 FAZLA"
        advice = "Hedefi aştın, diğer öğünlerde dikkat et."
        
    desc = nutrient_info.get(key_name, "")
    
    st.markdown(f"""
    <div class="nutrient-row {status_class}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h4 style="margin:0;">{label}</h4>
                <small style="color:#555;">{desc}</small>
            </div>
            <div style="text-align:right;">
                <h3 style="margin:0;">{value:.1f} / {int(target)} {unit}</h3>
                <strong>{status_text}</strong>
            </div>
        </div>
        <p style="margin-top:5px; font-style:italic;">💡 {advice}</p>
    </div>
    """, unsafe_allow_html=True)

# --- BAŞLIK ---
c1, c2 = st.columns([1, 8])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=80)
with c2: 
    st.title("MicroNutri AI Pro 🧬")
    st.caption("Detaylı Besin Analiz Raporu")

# ==========================================
# 🏁 SAYFA 1: PROFİL
# ==========================================
if st.session_state.step == 1:
    st.markdown('<div class="step-indicator">Adım 1/3: Profilini Oluştur</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Kişisel Bilgiler")
        st.radio("Cinsiyet", ["Erkek", "Kadın"], horizontal=True, key="w_gender", 
                 index=0 if st.session_state.user_profile["gender"]=="Erkek" else 1)
        st.number_input("Yaş", 10, 100, st.session_state.user_profile["age"], key="w_age")
        st.number_input("Boy (cm)", 100, 250, st.session_state.user_profile["height"], key="w_height")
        st.number_input("Kilo (kg)", 30, 200, st.session_state.user_profile["weight"], key="w_weight")
    with col2:
        st.subheader("🎯 Hedefler")
        act_opts = ["Hareketsiz (Masa başı)", "Az Hareketli (1-3 spor)", "Orta Hareketli (3-5 spor)", "Çok Hareketli"]
        try: act_idx = act_opts.index(st.session_state.user_profile.get("activity", act_opts[0]))
        except: act_idx = 0
        st.selectbox("Hareket Seviyesi", act_opts, index=act_idx, key="w_activity")
        
        goal_opts = ["Kilo Koru", "Kilo Ver (-500 kcal)", "Kilo Al (+400 kcal)"]
        try: goal_idx = goal_opts.index(st.session_state.user_profile.get("goal", goal_opts[0]))
        except: goal_idx = 0
        st.radio("Hedef", goal_opts, index=goal_idx, key="w_goal")

    st.markdown("---")
    st.button("Kaydet ve İlerle 👉", on_click=save_profile_and_next)

# ==========================================
# 🥗 SAYFA 2: YEMEK SEÇİMİ
# ==========================================
elif st.session_state.step == 2:
    st.markdown('<div class="step-indicator">Adım 2/3: Ne Yiyorsun?</div>', unsafe_allow_html=True)
    
    col_meal, col_select = st.columns([1, 2])
    with col_meal:
        meal_opts = ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği"]
        try: meal_idx = meal_opts.index(st.session_state.meal_state.get("current_meal", meal_opts[0]))
        except: meal_idx = 0
        st.radio("Zaman Dilimi", meal_opts, index=meal_idx, key="w_meal_type")
        
    with col_select:
        st.multiselect("🍽️ Menüden Seç:", df['name'].tolist(), key="w_selected_foods")

    temp_basket = []
    selected = st.session_state.w_selected_foods
    
    if selected:
        st.markdown("---")
        st.info("👇 Gramajları ayarlamayı unutma!")
        cols = st.columns(3)
        for i, food_name in enumerate(selected):
            row = df[df['name'] == food_name].iloc[0]
            with cols[i % 3]:
                grams = st.number_input(f"{food_name} (gr)", 10, 1000, 100, 10, key=f"gram_{food_name}")
                ratio = grams / 100
                item_full = row.to_dict()
                for k in item_full.keys():
                    if k not in ["name", "category"]: item_full[k] = item_full[k] * ratio
                temp_basket.append(item_full)
    
    st.session_state.meal_state["basket"] = temp_basket
    
    st.markdown("---")
    b1, b2 = st.columns([1, 4])
    with b1: st.button("👈 Geri", on_click=go_back)
    with b2: 
        if selected: st.button("Analizi Başlat 🚀", on_click=save_meal_and_next)
        else: st.warning("Devam etmek için en az bir yemek seçmelisin.")

# ==========================================
# 📊 SAYFA 3: DETAYLI RAPOR
# ==========================================
elif st.session_state.step == 3:
    st.markdown('<div class="step-indicator">Sonuç: Detaylı Beslenme Karnesi</div>', unsafe_allow_html=True)
    
    # --- 1. HESAPLAMALAR ---
    profile = st.session_state.user_profile
    meal_data = st.session_state.meal_state
    gender, weight, height, age = profile["gender"], profile["weight"], profile["height"], profile["age"]
    
    mults = {"Hareketsiz": 1.2, "Az Hareketli": 1.375, "Orta Hareketli": 1.55, "Çok Hareketli": 1.725}
    act_key = profile["activity"].split(" (")[0]
    act_mult = mults.get(act_key, 1.2)
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "Erkek" else -161)
    tdee = bmr * act_mult
    goal_cal = tdee - 500 if "Ver" in profile["goal"] else tdee + 400 if "Al" in profile["goal"] else tdee
    
    # HEDEFLER
    targets = {
        "calories": goal_cal / 3,
        "protein": (goal_cal * 0.20 / 4) / 3,
        "fat": (goal_cal * 0.30 / 9) / 3,
        "carbs": (goal_cal * 0.50 / 4) / 3,
        "vit_a_iu": 900 / 3, "vit_b_mg": 2.4 / 3, "vit_c_mg": 90 / 3, "vit_d_iu": 600 / 3, "vit_e_mg": 15 / 3,
        "calcium_mg": 1000 / 3,
        "iron_mg": (8 if gender == "Erkek" else 18) / 3,
        "magnesium_mg": (400 if gender == "Erkek" else 310) / 3,
        "zinc_mg": (11 if gender == "Erkek" else 8) / 3
    }
    
    basket = meal_data["basket"]
    totals = {k: sum(x.get(k, 0) for x in basket) for k in targets.keys()}

    # --- SEKMELİ RAPORLAMA ---
    tab1, tab2, tab3 = st.tabs(["📊 Özet Durum", "📋 Detaylı Karne", "💡 Akıllı Öneri"])

    # --- TAB 1: ÖZET ---
    with tab1:
        st.subheader("🔥 Kalori ve Enerji Dengesi")
        rem_cal = targets['calories'] - totals['calories']
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-container'><h3>Hedef</h3><h2>{int(targets['calories'])}</h2></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-container'><h3>Alınan</h3><h2>{int(totals['calories'])}</h2></div>", unsafe_allow_html=True)
        with c3: 
            lbl = "Açık (Kalan)" if rem_cal > 0 else "Fazlalık"
            color = "#4CAF50" if rem_cal > 0 else "#FF4B4B"
            st.markdown(f"<div class='metric-container' style='border-left: 5px solid {color}'><h3>{lbl}</h3><h2>{abs(int(rem_cal))}</h2></div>", unsafe_allow_html=True)
        
        st.progress(min(totals['calories'] / targets['calories'], 1.0))
        st.info("Detaylı besin analizi için yukarıdaki **'Detaylı Karne'** sekmesine tıklayın 👆")

    # --- TAB 2: DETAYLI KARNE ---
    with tab2:
        st.subheader("💪 Makro Besinler")
        analyze_nutrient("Protein", totals["protein"], targets["protein"], "g", "protein")
        analyze_nutrient("Karbonhidrat", totals["carbs"], targets["carbs"], "g", "carbs")
        analyze_nutrient("Yağ", totals["fat"], targets["fat"], "g", "fat")
        
        st.markdown("---")
        st.subheader("💊 Vitaminler")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            analyze_nutrient("A Vitamini", totals["vit_a_iu"], targets["vit_a_iu"], "IU", "vit_a_iu")
            analyze_nutrient("C Vitamini", totals["vit_c_mg"], targets["vit_c_mg"], "mg", "vit_c_mg")
        with col_v2:
            analyze_nutrient("D Vitamini", totals["vit_d_iu"], targets["vit_d_iu"], "IU", "vit_d_iu")
            analyze_nutrient("E Vitamini", totals["vit_e_mg"], targets["vit_e_mg"], "mg", "vit_e_mg")
            
        st.markdown("---")
        st.subheader("🪨 Mineraller")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            analyze_nutrient("Demir", totals["iron_mg"], targets["iron_mg"], "mg", "iron_mg")
            analyze_nutrient("Kalsiyum", totals["calcium_mg"], targets["calcium_mg"], "mg", "calcium_mg")
        with col_m2:
            analyze_nutrient("Magnezyum", totals["magnesium_mg"], targets["magnesium_mg"], "mg", "magnesium_mg")
            analyze_nutrient("Çinko", totals["zinc_mg"], targets["zinc_mg"], "mg", "zinc_mg")

    # --- TAB 3: AKILLI ÖNERİ ---
    with tab3:
        st.subheader(f"🔮 Gelecek Öğün Planı: {meal_data['next_meal_name']}")
        
        # En büyük eksiği bul
        deficiencies = {}
        for k, v in targets.items():
            if k == "calories": continue
            if totals[k] < (v * 0.6):
                deficiencies[k] = (v - totals[k]) / v
        
        if deficiencies:
            worst = max(deficiencies, key=deficiencies.get)
            clean_name = worst.replace("_mg", "").replace("_iu", "").upper()
            
            # Filtrele
            next_foods = df[df['category'].isin(meal_data['next_cats'])]
            suggestions = next_foods.sort_values(by=worst, ascending=False).head(3)
            
            st.error(f"Bu öğünde **{clean_name}** alımın çok yetersiz kaldı.")
            st.info(f"💡 {meal_data['next_meal_name']} öğününde bu açığı kapatmak için öneriler:")
            
            sc1, sc2, sc3 = st.columns(3)
            for idx, (_, row) in enumerate(suggestions.iterrows()):
                with [sc1, sc2, sc3][idx]:
                    st.markdown(f"""
                    <div class="nutrient-card">
                        <h3>{row['name']}</h3>
                        <p>{row['category']}</p>
                        <h2 style="color:#FF4B4B">{row[worst]:.1f}</h2>
                        <p>{clean_name}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.balloons()
            st.success("Tebrikler! Besin değerlerin harika. Gelecek öğünde serbestsin!")

    st.markdown("---")
    c_b1, c_b2 = st.columns(2)
    with c_b1: st.button("🔄 Düzenle", on_click=go_back)
    with c_b2: st.button("🏠 Başa Dön", on_click=restart)