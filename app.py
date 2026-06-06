 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات الصفحة
st.set_page_config(page_title="Zekrayat Dashboard", layout="wide")

# دوال التعريب للرسوم البيانية
def get_arabic(text):
    return get_display(arabic_reshaper.reshape(str(text)))

def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

# --- جلب البيانات ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", sheet_name=0)
    id_c = [c for c in df.columns if "كود" in c][0]
    st_c = [c for c in df.columns if "حالة" in c][0]
    city_c = [c for c in df.columns if any(k in str(c) for k in ["مدينة", "عنوان"])][0]
    p_col = [c for c in df.columns if "سعر" in c or "إجمالي" in c][0]
    
    df[id_c] = df[id_c].astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد").astype(str)
    df[city_c] = df[city_c].fillna("غير محدد").astype(str)
except:
    st.error("خطأ في قراءة البيانات")
    st.stop()

# --- واجهة الفلترة ---
selected_status = st.sidebar.selectbox("فلترة الحالة:", ['الكل'] + sorted(df[st_c].unique().tolist()))
selected_city = st.sidebar.selectbox("فلترة المدينة:", ['الكل'] + sorted(df[city_c].unique().tolist()))

tbl = df.copy()
if selected_status != 'الكل': tbl = tbl[tbl[st_c] == selected_status]
if selected_city != 'الكل': tbl = tbl[tbl[city_c] == selected_city]

st.title("📊 لوحة تحكم متجر ذكريات")

# --- لوحة المدن (Donut Chart) المضافة ---
st.subheader("📍 التوزيع الجغرافي للطلبات")
city_counts = tbl[city_c].value_counts()

fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
ax_pie.pie(city_counts.values, 
           labels=[get_arabic(x) for x in city_counts.index], 
           autopct='%1.1f%%', 
           startangle=140,
           wedgeprops={'width': 0.4}) # Donut Style
ax_pie.set_title(get_arabic("توزيع الطلبات حسب المدينة"), fontsize=14)
st.pyplot(fig_pie)
plt.close(fig_pie)

# (باقي الكود الخاص بك يوضع هنا...)
st.table(tbl)
