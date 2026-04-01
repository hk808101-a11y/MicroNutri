import streamlit as st
import pandas as pd
import random

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
    .nutrient-card { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.05); text-align: center; height: 100%; border-top: 5px solid #FF4B4B;}
    .gram-badge { background-color: #007BFF; color: white; padding: 5px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; display: inline-block; margin: 10px 0; box-shadow: 0 4px 6px rgba(0,123,255,0.2);}
</style>
""", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def get_data():
    return pd.read_csv("foods.csv")

try:
    df = get_data()
except Exception as e:
    st.error("❌ 'foods.csv' dosyası bulunamadı veya okunamadı. Lütfen dosyanın aynı klasörde olduğundan emin ol.")
    st.stop()

# --- KALICI HAFIZA (SESSION STATE) ---
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
        nxt, cats = "Öğle Yemeği", ["Çorba", "Et", "Sebze", "Bakliyat", "Tahıl", "Ana Yemek", "Ara Yemek"]
    elif current == "Öğle Yemeği":
        nxt, cats = "Akşam Yemeği", ["Çorba", "Sebze", "Et", "Salata", "Süt Ürünü", "Ana Yemek"]
    else:
        nxt, cats = "Yarınki Kahvaltı", ["Kahvaltılık", "Süt Ürünü", "Meyve", "Kuruyemiş", "İçecek"]
        
    st.session_state.meal_state["next_meal_name"] = nxt
    st.session_state.meal_state["next_cats"] = cats
    st.session_state.step += 1

def go_back(): st.session_state.step -= 1
def restart(): 
    st.session_state.step = 1
    st.session_state.meal_state["basket"] = []

# --- SAĞLIK SÖZLÜĞÜ ---
nutrient_info = {
    "protein": "Kas onarımı ve bağışıklık için temeldir.",
    "fat": "Hücre zarı ve hormon üretimi için gereklidir.",
    "carbs": "Vücudun temel enerji kaynağıdır.",
    "vit_a_iu": "Göz sağlığı ve bağışıklık sistemi için kritiktir.",
    "vit_c_mg": "Antioksidandır, bağışıklığı güçlendirir.",
    "vit_d_iu": "Kemik sağlığı ve ruh hali için güneş vitaminidir.",
    "vit_e_mg": "Cilt sağlığı ve hücre yenilenmesi için önemlidir.",
    "calcium_mg": "Kemik ve diş yapısını korur, kas kasılmasını sağlar.",
    "iron_mg": "Kan yapımı ve oksijen taşıma için hayati önemdedir.",
    "magnesium_mg": "Kas gevşemesi ve sinir sistemi dengesi için şarttır.",
    "zinc_mg": "Bağışıklık, yara iyileşmesi ve hormon dengesi için gereklidir."
}

def analyze_nutrient(label, value, target, unit, key_name):
    ratio = value / target if target > 0 else 0
    if ratio < 0.5:
        status_class, status_text, advice = "nutrient-low", "⚠️ KRİTİK AZ", "Çok yetersiz kaldı. Takviye edici gıdalar seçmelisin."
    elif ratio < 0.85:
        status_class, status_text, advice = "nutrient-low", "📉 AZ", "Hedefin altında, biraz daha artırabilirsin."
    elif ratio <= 1.15:
        status_class, status_text, advice = "nutrient-perfect", "✅ İDEAL", "Harika! Tam olması gereken seviyede."
    else:
        status_class, status_text, advice = "nutrient-high", "📈 FAZLA", "Hedefi aştın, diğer öğünlerde dikkat et."
        
    desc = nutrient_info.get(key_name, "")
    st.markdown(f"""
    <div class="nutrient-row {status_class}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div><h4 style="margin:0;">{label}</h4><small style="color:#555;">{desc}</small></div>
            <div style="text-align:right;"><h3 style="margin:0;">{value:.1f} / {int(target)} {unit}</h3><strong>{status_text}</strong></div>
        </div>
        <p style="margin-top:5px; font-style:italic;">💡 {advice}</p>
    </div>
    """, unsafe_allow_html=True)

# --- BAŞLIK ---
c1, c2 = st.columns([1, 8])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=80)
with c2: 
    st.title("MicroNutri AI Pro 🧬")
    st.caption("Detaylı Besin Analiz Raporu ve Akıllı Karar Destek Sistemi")

# ==========================================
# 🏁 SAYFA 1: PROFİL
# ==========================================
if st.session_state.step == 1:
    st.markdown('<div class="step-indicator">Adım 1/3: Profilini Oluştur</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Kişisel Bilgiler")
        st.radio("Cinsiyet", ["Erkek", "Kadın"], horizontal=True, key="w_gender", index=0 if st.session_state.user_profile["gender"]=="Erkek" else 1)
        st.number_input("Yaş", 10, 100, st.session_state.user_profile["age"], key="w_age")
        st.number_input("Boy (cm)", 100, 250, st.session_state.user_profile["height"], key="w_height")
        st.number_input("Kilo (kg)", 30, 200, st.session_state.user_profile["weight"], key="w_weight")
    with col2:
        st.subheader("🎯 Hedefler")
        act_opts = ["Hareketsiz (Masa başı)", "Az Hareketli (1-3 spor)", "Orta Hareketli (3-5 spor)", "Çok Hareketli"]
        act_idx = act_opts.index(st.session_state.user_profile.get("activity", act_opts[0])) if st.session_state.user_profile.get("activity") in act_opts else 0
        st.selectbox("Hareket Seviyesi", act_opts, index=act_idx, key="w_activity")
        
        goal_opts = ["Kilo Koru", "Kilo Ver (-500 kcal)", "Kilo Al (+400 kcal)"]
        goal_idx = goal_opts.index(st.session_state.user_profile.get("goal", goal_opts[0])) if st.session_state.user_profile.get("goal") in goal_opts else 0
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
        meal_idx = meal_opts.index(st.session_state.meal_state.get("current_meal", meal_opts[0])) if st.session_state.meal_state.get("current_meal") in meal_opts else 0
        st.radio("Zaman Dilimi", meal_opts, index=meal_idx, key="w_meal_type")
        
    with col_select:
        st.markdown("### 🍽️ Menüden Seç")
        st.caption("Aradığın yemeği bulmak için ilgili kategoriye tıkla:")
        
        all_selected = []
        groups = {
            "🍳 Kahvaltı & Süt": ["Kahvaltılık", "Süt Ürünü"],
            "🍲 Yemekler": ["Çorba", "Et", "Sebze", "Bakliyat"],
            "🥗 Salata & Yancı": ["Salata", "Tahıl", "Hamur İşi"],
            "🍎 Tatlı & Atıştırmalık": ["Meyve", "Kuruyemiş", "Tatlı", "İçecek", "FastFood"]
        }
        
        category_tabs = st.tabs(list(groups.keys()))
        
        for i, (grp_name, cats) in enumerate(groups.items()):
            with category_tabs[i]:
                for cat in cats:
                    cat_foods = df[df['category'] == cat]['name'].tolist()
                    if cat_foods:
                        sel = st.multiselect(f"👉 {cat} Ekle:", cat_foods, key=f"sel_{cat}")
                        all_selected.extend(sel)
                        
        st.session_state.w_selected_foods = all_selected

    temp_basket = []
    selected = st.session_state.w_selected_foods
    
    if selected:
        st.markdown("---")
        st.info("👇 Seçtiğin yemeklerin gramajlarını ayarlamayı unutma!")
        cols = st.columns(3)
        for i, food_name in enumerate(selected):
            row = df[df['name'] == food_name].iloc[0]
            with cols[i % 3]:
                grams = st.number_input(f"{food_name} (gr)", 10, 1000, 100, 10, key=f"gram_{food_name}")
                ratio = grams / 100
                item_full = row.to_dict()
                for k in item_full.keys():
                    if pd.api.types.is_numeric_dtype(type(item_full[k])):
                        item_full[k] = item_full[k] * ratio
                temp_basket.append(item_full)
                
    st.session_state.meal_state["basket"] = temp_basket
    
    st.markdown("---")
    b1, b2 = st.columns([1, 4])
    with b1: st.button("👈 Geri", on_click=go_back)
    with b2: 
        if selected: st.button("Analizi Başlat 🚀", on_click=save_meal_and_next)
        else: st.warning("Devam etmek için en az bir yemek seçmelisin.")

# ==========================================
# 📊 SAYFA 3: DETAYLI RAPOR VE ÖNERİ
# ==========================================
elif st.session_state.step == 3:
    st.markdown('<div class="step-indicator">Sonuç: Detaylı Beslenme Karnesi</div>', unsafe_allow_html=True)
    
    profile = st.session_state.user_profile
    meal_data = st.session_state.meal_state
    gender, weight, height, age = profile["gender"], profile["weight"], profile["height"], profile["age"]
    
    mults = {"Hareketsiz": 1.2, "Az Hareketli": 1.375, "Orta Hareketli": 1.55, "Çok Hareketli": 1.725}
    act_mult = mults.get(profile["activity"].split(" (")[0], 1.2)
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "Erkek" else -161)
    tdee = bmr * act_mult
    goal_cal = tdee - 500 if "Ver" in profile["goal"] else tdee + 400 if "Al" in profile["goal"] else tdee
    
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

    # --- OYUNLAŞTIRMA ---
    score_sum = 0
    num_metrics = len(targets)
    for k, v in targets.items():
        if v > 0:
            ratio = totals[k] / v
            if k in ['calories', 'fat', 'carbs']:
                if ratio <= 1.15: score_sum += min(ratio, 1.0)
                else: score_sum += max(1.0 - (ratio - 1.15), 0)
            else:
                score_sum += min(ratio, 1.0)
                
    final_score = int((score_sum / num_metrics) * 100)
    
    if final_score >= 80: s_color, s_msg, s_icon = "#00b894", "Harika gidiyorsun! Hedeflerine çok yakınsın.", "🌟"
    elif final_score >= 50: s_color, s_msg, s_icon = "#fdcb6e", "İdare eder. Eksiklerini sonraki öğünde kapatmalısın.", "⚖️"
    else: s_color, s_msg, s_icon = "#ff7675", "Kritik seviye! Seçtiğin menü hedeflerinin uzağında kaldı.", "⚠️"

    st.markdown(f"""
    <div style="background-color: {s_color}15; border: 3px solid {s_color}; border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 30px;">
        <h3 style="margin:0; color: #555; text-transform: uppercase; font-size:16px;">{s_icon} Bu Öğün İçin Sağlık Skorun {s_icon}</h3>
        <h1 style="margin:10px 0; font-size: 60px; color: {s_color};">{final_score} <span style="font-size:30px; color:#aaa;">/ 100</span></h1>
        <p style="margin:0; color: #333; font-weight: bold; font-size:16px;">{s_msg}</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Özet Durum", "📋 Detaylı Karne", "💡 Akıllı Alternatifli Fiks Menü"])

    with tab1:
        st.subheader("🔥 Kalori ve Enerji Dengesi")
        rem_cal = targets['calories'] - totals['calories']
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-container'><h3>Hedef</h3><h2>{int(targets['calories'])} kcal</h2></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-container'><h3>Alınan</h3><h2>{int(totals['calories'])} kcal</h2></div>", unsafe_allow_html=True)
        with c3: 
            lbl, color = ("Açık (Kalan)", "#4CAF50") if rem_cal > 0 else ("Fazlalık", "#FF4B4B")
            st.markdown(f"<div class='metric-container' style='border-left: 5px solid {color}'><h3>{lbl}</h3><h2>{abs(int(rem_cal))} kcal</h2></div>", unsafe_allow_html=True)
        st.progress(min(totals['calories'] / (targets['calories'] if targets['calories']>0 else 1), 1.0))

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

    with tab3:
        st.subheader(f"🔮 Gelecek Öğün Planı: {meal_data['next_meal_name']}")
        
        deficiencies = {}
        for k, v in targets.items():
            if k in ["calories", "protein", "carbs", "fat"]: continue 
            if totals[k] < (v * 0.6): 
                deficiencies[k] = (v - totals[k]) / v
        
        if deficiencies:
            sorted_deficiencies = sorted(deficiencies.items(), key=lambda x: x[1], reverse=True)
            
            st.error("Bu süreçte bazı mineral ve vitamin alımların yetersiz kaldı.")
            st.info("💡 Hedeflerine tam ulaşabilmen için sana 2 farklı Tam Menü (3 Yiyecek + 1 İçecek) alternatifi hazırladım. Dilediğini seç!")
            
            used_foods = [] 
            search_meal = "Kahvaltı" if meal_data['next_meal_name'] == "Yarınki Kahvaltı" else meal_data['next_meal_name']
            
            target_cal_per_item = targets['calories'] / 4
            all_micros = ["vit_a_iu", "vit_b_mg", "vit_c_mg", "vit_d_iu", "vit_e_mg", "calcium_mg", "iron_mg", "magnesium_mg", "zinc_mg"]
            
            if 'Ogun' in df.columns:
                next_foods = df[df['Ogun'].str.contains(search_meal, na=False, case=False)]
            else:
                next_foods = df[df['category'].isin(meal_data['next_cats'])]
                
            solids_df = next_foods[next_foods['category'] != 'İçecek']
            drinks_df = next_foods[next_foods['category'] == 'İçecek']

            # HTML Kart Oluşturucu Fonksiyon
            def create_card_html(best_food, nutrient_key, clean_name):
                food_cal_100g = best_food['calories']
                if food_cal_100g > 0: rec_grams = (target_cal_per_item / food_cal_100g) * 100
                else: rec_grams = 200 
                    
                rec_grams = round(rec_grams / 10) * 10
                if rec_grams > 350: rec_grams = 350
                if rec_grams < 20: rec_grams = 20
                
                final_cal = (food_cal_100g / 100) * rec_grams
                
                if nutrient_key in best_food and best_food[nutrient_key] > 0:
                    final_nut = (best_food[nutrient_key] / 100) * rec_grams
                    nut_text = f"+{final_nut:.1f} eklenecek"
                else:
                    nut_text = "Su dengesi sağlanacak"
                    
                tur_baslik = best_food['Tur'] if 'Tur' in best_food.index and pd.notna(best_food['Tur']) else best_food['category']
                
                bonus_list = []
                for m in all_micros:
                    if m != nutrient_key and m in best_food and best_food[m] > 0:
                        m_val = (best_food[m] / 100) * rec_grams
                        if m_val >= 0.5: 
                            bonus_list.append(f"{m.replace('_mg', '').replace('_iu', '').upper()} (+{m_val:.1f})")
                
                bonus_html = ""
                if bonus_list:
                    bonus_html = f"<div style='margin-top:10px; font-size:10px; color:#666; border-top:1px dashed #ccc; padding-top:8px;'><b>🎁 Ekstra:</b> {', '.join(bonus_list[:3])}</div>"
                
                html_code = f'''<div class="nutrient-card"><p style="color:#888; font-size:11px; margin-bottom:0; text-transform:uppercase;">{tur_baslik}</p><h3 style="margin-top:5px; margin-bottom:5px; font-size:16px;">{best_food["name"]}</h3><div class="gram-badge">⚖️ Porsiyon: {int(rec_grams)} gr/ml</div><br><span style="background-color:#ffebeb; color:#FF4B4B; padding:4px 8px; border-radius:10px; font-size:12px; font-weight:bold;">🔥 {int(final_cal)} kcal</span><div style="background-color:#f8f9fa; padding:10px; border-radius:8px; margin-top:15px; border: 1px solid #eee;"><p style="font-size:11px; color:#555; margin-bottom:0;">Kazanılan:</p><h2 style="color:#00b894; margin:5px 0; font-size:18px;">{clean_name}</h2><p style="font-size:13px; color:#333; margin-top:5px;"><b>{nut_text}</b></p>{bonus_html}</div></div>'''
                return html_code

            # İKİ FARKLI SEÇENEK (DÖNGÜSÜ)
            for option in [1, 2]:
                st.markdown(f"<h3 style='color:#FF4B4B; margin-top:20px; text-align:center;'>🍱 Menü Seçeneği {option}</h3>", unsafe_allow_html=True)
                cols = st.columns(4)
                
                # İlk 3 Kolon: Yiyecekler
                solid_idx = 0
                for nutrient_key, def_ratio in sorted_deficiencies:
                    if solid_idx >= 3: break
                    clean_name = nutrient_key.replace("_mg", "").replace("_iu", "").upper()
                    
                    avail_solids = solids_df[~solids_df['name'].isin(used_foods)].copy()
                    if not avail_solids.empty:
                        avail_solids['fp'] = avail_solids[nutrient_key] / avail_solids['calories'].replace(0, 1)
                        best_solid = avail_solids.sort_values(by='fp', ascending=False).head(4).sample(n=1).iloc[0]
                        used_foods.append(best_solid['name']) # İkinci menüde bir daha çıkmaması için listeye ekle
                        
                        with cols[solid_idx]:
                            st.markdown(create_card_html(best_solid, nutrient_key, clean_name), unsafe_allow_html=True)
                    solid_idx += 1

                # Son Kolon: İçecek
                with cols[3]:
                    best_drink = None
                    drink_nut_name = "FERAHLIK"
                    drink_nut_key = "calories"
                    
                    for nutrient_key, def_ratio in sorted_deficiencies:
                        avail_drinks = drinks_df[~drinks_df['name'].isin(used_foods)].copy()
                        if not avail_drinks.empty:
                            avail_drinks['fp'] = avail_drinks[nutrient_key] / avail_drinks['calories'].replace(0, 1)
                            helpful_drinks = avail_drinks[avail_drinks[nutrient_key] > 0]
                            if not helpful_drinks.empty:
                                best_drink = helpful_drinks.sort_values(by='fp', ascending=False).head(3).sample(n=1).iloc[0]
                                drink_nut_name = nutrient_key.replace("_mg", "").replace("_iu", "").upper()
                                drink_nut_key = nutrient_key
                                break
                    
                    if best_drink is None and not drinks_df.empty:
                        avail_drinks_fallback = drinks_df[~drinks_df['name'].isin(used_foods)]
                        if not avail_drinks_fallback.empty:
                            best_drink = avail_drinks_fallback.sample(n=1).iloc[0]
                        drink_nut_name = "HİDRASYON"
                        
                    if best_drink is not None:
                        used_foods.append(best_drink['name'])
                        st.markdown(create_card_html(best_drink, drink_nut_key, drink_nut_name), unsafe_allow_html=True)
                
                # Araya ayırıcı çizgi at (Eğer 1. seçenekteysek)
                if option == 1:
                    st.markdown("<br><hr style='border: 2px dashed #ddd; margin: 30px 0;'><br>", unsafe_allow_html=True)
                    
        else:
            st.balloons()
            st.success("Tebrikler! Besin değerlerin harika. Gelecek öğünde serbestsin!")

    st.markdown("---")
    c_b1, c_b2 = st.columns(2)
    with c_b1: st.button("🔄 Düzenle", on_click=go_back)
    with c_b2: st.button("🏠 Başa Dön", on_click=restart)