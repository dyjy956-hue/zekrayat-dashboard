 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات الواجهة
st.set_page_config(page_title="Zekrayat Dashboard", layout="wide", initial_sidebar_state="expanded")

# دالة معالجة النصوص العربية للرسوم البيانية
def get_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def clean_emojis(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

# جلب البيانات من قوقل شيت
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", engine='openpyxl')
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    p_col = [c for c in df.columns if "سعر" in c or "إجمالي" in c or "Price" in c][0]
    city_c = [c for c in df.columns if any(k in str(c) for k in ["مدينة", "عنوان", "City"])][0]
    
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    clean_all = df[df[id_c].str.startswith('D-', na=False)].copy()
    clean_all[st_c] = clean_all[st_c].fillna("Unspecified").astype(str)
    clean_all[city_c] = clean_all[city_c].fillna("Unspecified").astype(str)
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
except:
    st.error("خطأ في الاتصال بالشيت. تأكد من الرابط والأعمدة.")
    st.stop()

# الفرز في القائمة الجانبية
st.sidebar.markdown("### ⚙️ لوحة الفرز")
selected_status = st.sidebar.selectbox("اختر الحالة:", sorted(clean_all[st_c].unique()))
selected_city = st.sidebar.selectbox("اختر المدينة:", ['الكل'] + sorted(clean_all[city_c].unique()))

# تصفية البيانات
tbl = clean_all[clean_all[st_c] == selected_status].copy()
if selected_city != 'الكل':
    tbl = tbl[tbl[city_c] == selected_city]

# اللوحة الرئيسية
st.markdown("## 📊 لوحة تحكم متجر ذكريات")

col1, col2, col3 = st.columns(3)
col1.metric("إجمالي الطلبات", len(tbl))
col2.metric("إجمالي الإيرادات", f"{tbl[p_col].sum():,.0f} LYD")
col3.metric("عدد المدن المغطاة", len(tbl[city_c].unique()))

# الرسم البياني للمدن (مع دعم العربية)
city_counts = tbl[city_c].value_counts()
fig_city, ax_city = plt.subplots(figsize=(6, 4))
labels = [get_arabic_text(x) for x in city_counts.index]
ax_city.pie(city_counts.values, labels=labels, autopct='%1.1f%%', startangle=90)
ax_city.set_title(get_arabic_text("توزيع الطلبات حسب المدينة"), fontsize=12)

st.subheader("📍 التوزيع الجغرافي")
st.pyplot(fig_city)

# لوحة صدارة الكتب (للمستلمين فقط)
st.markdown("---")
st.subheader("📈 صدارة الكتب الأكثر طلباً (طلبات التسليم)")
book_cols = [c for c in clean_all.columns if "book type" in c.lower() or "كتاب" in c]
strict_delivered = tbl[tbl[st_c].str.contains('تسليم|تم|مستلم', na=False, case=False)]

if not strict_delivered.empty:
    data = []
    for col in book_cols:
        qty = pd.to_numeric(strict_delivered[col], errors='coerce').fillna(0).sum()
        if qty > 0:
            name = re.search(r'\[(.*?)\]', col).group(1) if "[" in col else col
            data.append({"Book": name, "Qty": int(qty)})
    
    if data:
        df_b = pd.DataFrame(data).sort_values("Qty", ascending=False)
        fig_b, ax_b = plt.subplots(figsize=(8, 4))
        ax_b.bar(df_b["Book"], df_b["Qty"], color='#117a65')
        ax_b.set_title(get_arabic_text("الكتب الأكثر طلباً"), fontsize=12)
        plt.xticks(rotation=15)
        st.pyplot(fig_b)
    else:
        st.info("لا توجد مبيعات كتب في هذه الحزمة.")
else:
    st.warning("لا توجد طلبيات تسليم لعرض صدارة الكتب.")
