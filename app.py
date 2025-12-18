import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="MicroNutri AI - Senkronize", page_icon="🍽️", layout="wide")

# --- VERİ YÜKLEME ---
@st.cache_data
def get_data():
    return pd.read_csv("foods.csv")

try:
    df = get_data()
except:
    st.error("foods.csv dosyası bulunamadı! Lütfen dosyanın yüklü olduğundan emin olun.")
    st.stop()

# --- BAŞLIK ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/1046/1046751.png", width=90)
with col2:
    st.title("MicroNutri AI - Akıllı Tabak Dengeleyici")
    st.markdown("**Şu anki öğününü seç, eksiklerini gör, tabağını o öğüne uygun tamamla!**")

st.markdown("---")

# ==========================================
# 1. BÖLÜM: KİŞİSEL VERİLER
# ==========================================
st.sidebar.header("📝 Kişisel Bilgilerin")
gender = st.sidebar.radio("Cinsiyet", ["Erkek", "Kadın"])
age = st.sidebar.number_input("Yaş", 10, 100, 25)
height = st.sidebar.number_input("Boy (cm)", 100, 250, 175)
weight = st.sidebar.number_input("Kilo (kg)", 30, 200, 75)

st.sidebar.markdown("---")
st.sidebar.header("🏃 Hareket Seviyesi")
activity_level = st.sidebar.selectbox("Günlük Aktivite", 
    ["Hareketsiz (Masa başı)", "Az Hareketli (1-3 gün spor)", "Orta Hareketli (3-5 gün spor)", "Çok Hareketli (Her gün spor)"])

activity_multipliers = {
    "Hareketsiz (Masa başı)": 1.2,
    "Az Hareketli (1-3 gün spor)": 1.375,
    "Orta Hareketli (3-5 gün spor)": 1.55,
    "Çok Hareketli (Her gün spor)": 1.725
}

# --- HESAPLAMA MOTORU ---
if gender == "Erkek":
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else:
    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

tdee = bmr * activity_multipliers[activity_level]

st.sidebar.markdown("---")
st.sidebar.header("🎯 Hedefin Ne?")
goal = st.sidebar.radio("Seçimini Yap:", ["Kilo Koru", "Kilo Ver (-500 kcal)", "Kilo Al (+400 kcal)"])

if goal == "Kilo Ver (-500 kcal)":
    daily_cal = tdee - 500
elif goal == "Kilo Al (+400 kcal)":
    daily_cal = tdee + 400
else:
    daily_cal = tdee

# Öğünlük Hedefler (Günlük / 3)
meal_targets = {
    "calories": daily_cal / 3,
    "protein": (daily_cal * 0.20 / 4) / 3,
    "fat": (daily_cal * 0.30 / 9) / 3,
    "carbs": (daily_cal * 0.50 / 4) / 3,
    "vit_a": 900 / 3,
    "vit_b": 2.4 / 3,
    "vit_c": 90 / 3,
    "vit_d": 600 / 3,
    "vit_e": 15 / 3
}

# ==========================================
# 2. BÖLÜM: ZAMAN VE FİLTRELEME
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🕰️ Hangi Öğündesin?")
current_meal_type = st.sidebar.selectbox("Öğün Seçimi:", ["Kahvaltı", "Öğle Yemeği", "Akşam Yemeği"])

# --- AKILLI KATEGORİ FİLTRESİ (Üst ve Alt Yazı Uyuşmazlığını Çözen Kısım) ---
# Eğer Kahvaltı seçtiysen, sana sadece kahvaltılık önerilecek.
allowed_categories = []

if current_meal_type == "Kahvaltı":
    allowed_categories = ["Kahvaltılık", "Süt Ürünü", "Meyve", "Hamur İşi", "Kuruyemiş"]
else: # Öğle ve Akşam
    allowed_categories = ["Çorba", "Et", "Sebze", "Bakliyat", "Tahıl", "Süt Ürünü", "Tatlı", "Meyve"]

# Seçim listesini sadece bu kategorilere göre filtrele (Görsel temizlik için)
# İstersen burayı açabilirsin ama genelde kullanıcı her şeyi seçmek ister, biz öneriyi kısıtlayalım.
# all_foods = df[df['category'].isin(allowed_categories)]['name'].tolist() 
# Şimdilik kullanıcının yediği her şeye izin verelim, ama ÖNERİYİ kısıtlayalım.
all_foods = df['name'].tolist() 

st.sidebar.header("🍽️ Tabağındakiler")
selected_food_names = st.sidebar.multiselect(f"{current_meal_type} için ekle:", all_foods)

user_basket = []

if selected_food_names:
    # Bilgi Çubuğu
    st.info(f"📅 **{current_meal_type}** Analizi | Hedef Kalori: **{int(meal_targets['calories'])} kcal**")

    st.subheader(f"⚖️ Porsiyonlar")
    cols = st.columns(3)
    
    for i, food_name in enumerate(selected_food_names):
        row = df[df['name'] == food_name].iloc[0]
        with cols[i % 3]:
            grams = st.number_input(f"{food_name} (gr)", 10, 1000, 100, 10, key=food_name)
            ratio = grams / 100
            
            cal_val = row['calories'] * ratio
            pro_val = row['protein'] * ratio
            st.caption(f"🔥 {int(cal_val)} kcal | 💪 {pro_val:.1f}g Protein")
            
            item_data = row.to_dict()
            for key in ["calories", "protein", "fat", "carbs", "vit_a_iu", "vit_b_mg", "vit_c_mg", "vit_d_iu", "vit_e_mg"]:
                 item_data[key] = row[key] * ratio
            
            # Standartlaştırma
            formatted_item = {
                "name": food_name,
                "category": row['category'],
                "calories": item_data['calories'],
                "protein": item_data['protein'],
                "fat": item_data['fat'],
                "carbs": item_data['carbs'],
                "vit_a": item_data['vit_a_iu'],
                "vit_b": item_data['vit_b_mg'],
                "vit_c": item_data['vit_c_mg'],
                "vit_d": item_data['vit_d_iu'],
                "vit_e": item_data['vit_e_mg']
            }
            user_basket.append(formatted_item)

    # Toplamları Al
    current_totals = {k: sum(item[k] for item in user_basket) for k in meal_targets.keys()}

    st.markdown("---")

    # --- GÖRSEL ANALİZ ---
    c1, c2, c3 = st.columns(3)
    remaining_cal = meal_targets['calories'] - current_totals['calories']
    
    with c1: st.metric("Öğün Hedefi", f"{int(meal_targets['calories'])} kcal")
    with c2: st.metric("Şu Anki Tabak", f"{int(current_totals['calories'])} kcal")
    with c3: 
        if remaining_cal > 0: st.metric("Kalan Yer", f"{int(remaining_cal)} kcal", "Yemeye devam", delta_color="normal")
        else: st.metric("Aşılan", f"{int(abs(remaining_cal))} kcal", "Limit aşıldı", delta_color="inverse")

    st.markdown("---")
    
    # Barlar
    cm, cv = st.columns(2)
    with cm:
        st.subheader("💪 Makrolar")
        for m in ["protein", "carbs", "fat"]:
            curr, tgt = current_totals[m], meal_targets[m]
            st.progress(min(curr/tgt, 1.0), text=f"{m.capitalize()}: {curr:.1f}/{tgt:.1f}g")
            
    with cv:
        st.subheader("💊 Vitaminler")
        for v in ["vit_a", "vit_b", "vit_c", "vit_d", "vit_e"]:
            curr, tgt = current_totals[v], meal_targets[v]
            st.progress(min(curr/tgt, 1.0), text=f"{v.upper()}: {curr:.1f}/{tgt:.1f}")

    # ==========================================
    # 3. BÖLÜM: EŞLEŞTİRİLMİŞ ÖNERİ SİSTEMİ
    # ==========================================
    st.markdown("---")
    st.subheader(f"👨‍🍳 {current_meal_type} Tavsiyesi") # <-- BURASI ARTIK TUTUYOR!

    # 1. EKSİKLERİ BUL
    deficiencies = {}
    for nutrient, target in meal_targets.items():
        if nutrient == 'calories': continue
        if current_totals[nutrient] < (target * 0.5): # %50 kuralı
            gap = target - current_totals[nutrient]
            deficiencies[nutrient] = gap / target 

    if deficiencies:
        most_needed = max(deficiencies, key=deficiencies.get)
        
        csv_map = {
            "protein": "protein", "fat": "fat", "carbs": "carbs",
            "vit_a": "vit_a_iu", "vit_b": "vit_b_mg", "vit_c": "vit_c_mg", 
            "vit_d": "vit_d_iu", "vit_e": "vit_e_mg"
        }
        target_col = csv_map[most_needed]

        # 2. FİLTRELEME: Sadece SEÇİLEN ÖĞÜNE UYGUN olanları öner
        # Kahvaltıysa -> Kahvaltılık öner. Akşamsa -> Yemek öner.
        suitable_foods = df[df['category'].isin(allowed_categories)]
        
        # 3. SIRALAMA
        sorted_df = suitable_foods.sort_values(by=target_col, ascending=False)
        
        menu_suggestion = []
        seen_categories = set()
        
        # Tabağında zaten olan kategoriden bir daha önerme (Çeşitlilik)
        current_categories = {item['category'] for item in user_basket}

        for _, row in sorted_df.iterrows():
             if row['name'] not in [x['name'] for x in user_basket]: # Zaten tabağında yoksa
                 if row['category'] not in current_categories: # Zaten tabağında bu kategori yoksa
                    if row['category'] not in seen_categories:
                        menu_suggestion.append(row)
                        seen_categories.add(row['category'])
             if len(menu_suggestion) >= 3: break
        
        # Eğer liste boşsa (çok filtrelediysek), en zengin kaynağı koy
        if not menu_suggestion:
             menu_suggestion.append(sorted_df.iloc[0])

        st.warning(f"⚠️ **{current_meal_type}** tabağında **{most_needed.upper()}** çok eksik kaldı.")
        st.success(f"💡 Tabağının yanına şunları ekleyerek dengeyi kurabilirsin:")
        
        cols = st.columns(len(menu_suggestion))
        for idx, item in enumerate(menu_suggestion):
            with cols[idx]:
                st.image("https://cdn-icons-png.flaticon.com/512/706/706164.png", width=50)
                st.markdown(f"**{item['category']}**")
                st.markdown(f"### {item['name']}")
                st.caption(f"Bu ekleme sana **{item[target_col]}** birim {most_needed} kazandıracak.")

    else:
        st.balloons()
        st.success(f"Harika! **{current_meal_type}** tabağın tam dengede. Afiyet olsun! 🌟")

else:
    st.info("👈 Önce sol taraftan hangi öğünde olduğunu ve ne yediğini seç.")