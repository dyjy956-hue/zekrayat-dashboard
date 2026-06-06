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

# دالة معالجة النصوص العربية للرسوم البيانية
def get_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

# دالة الأيقونات
def get_icon(col_name):
    c = str(col_name).lower()
    if 'كود' in c: return '🆔'
    if 'اسم' in c: return '👤'
    if 'سعر' in c or 'إجمالي' in c: return '💰'
    if 'حالة' in c: return '🚦'
    if 'مدينة' in c or 'عنوان' in c: return '📍'
    return '📚'

# جلب البيانات
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}")
    id_c = [c for c in df.columns if "كود" in c][0]
    st_c = [c for c in df.columns if "حالة" in c][0]
    city_c = [c for c in df.columns if any(k in str(c) for k in ["مدينة", "عنوان"])][0]
    
    df[id_c] = df[id_c].astype(str).str.strip()
    clean_cities = sorted([str(x).strip() for x in df[city_c].unique() if pd.notna(x)])
    clean_statuses = sorted([str(x).strip() for x in df[st_c].unique() if pd.notna(x)])
except:
    st.error("خطأ في جلب البيانات، تأكد من رابط الشيت.")
    st.stop()

# فلترة الواجهة
st.sidebar.header("⚙️ لوحة التحكم")
selected_status = st.sidebar.selectbox("اختر الحالة:", clean_statuses)
selected_city = st.sidebar.selectbox("اختر المدينة:", ['الكل'] + clean_cities)

# معالجة البيانات
tbl = df[df[st_c] == selected_status].copy()
if selected_city != 'الكل':
    tbl = tbl[tbl[city_c] == selected_city]

# عرض الإحصائيات
st.title("📊 لوحة تحكم ذكريات")
col1, col2 = st.columns(2)
with col1:
    st.metric("عدد الطلبات", len(tbl))
with col2:
    p_col = [c for c in df.columns if "سعر" in c or "إجمالي" in c][0]
    st.metric("الإيرادات", f"{tbl[p_col].sum():,.0f} LYD")

# الرسم البياني للمدن (مع دعم العربية)
if city_c:
    city_counts = tbl[city_c].value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    
    labels = [get_arabic_text(x) for x in city_counts.index]
    ax2.pie(city_counts.values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax2.set_title(get_arabic_text("توزيع الطلبات حسب المدينة"), fontsize=12)
    
    st.subheader("📍 التوزيع الجغرافي")
    st.pyplot(fig2)

# جدول الطلبات
st.subheader("📋 تفاصيل الطلبيات")
st.table(tbl)
