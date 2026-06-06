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

# --- دوال مساعدة ---
def get_arabic(text):
    return get_display(arabic_reshaper.reshape(str(text)))

def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

def get_icon(col_name):
    c = str(col_name).lower()
    if 'كود' in c: return '🆔'
    if 'اسم' in c: return '👤'
    if 'سعر' in c: return '💰'
    if 'حالة' in c: return '🚦'
    if 'مدينة' in c: return '📍'
    return '📚'

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
    df[p_col] = pd.to_numeric(df[p_col], errors='coerce').fillna(0)
except:
    st.error("خطأ في جلب البيانات")
    st.stop()

# --- التصفية ---
selected_status = st.sidebar.selectbox("فلترة الحالة:", ['الكل'] + sorted(df[st_c].unique().tolist()))
selected_city = st.sidebar.selectbox("فلترة المدينة:", ['الكل'] + sorted(df[city_c].unique().tolist()))

tbl = df.copy()
if selected_status != 'الكل': tbl = tbl[tbl[st_c] == selected_status]
if selected_city != 'الكل': tbl = tbl[tbl[city_c] == selected_city]

# --- الواجهة ---
st.markdown("<h1 style='text-align: center;'>📊 لوحة تحكم متجر ذكريات</h1>", unsafe_allow_html=True)

# 1. إحصائيات المدن (Donut Chart)
st.subheader("📍 التوزيع الجغرافي للطلبات")
city_counts = tbl[city_c].value_counts()
fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
ax_pie.pie(city_counts.values, labels=[get_arabic(x) for x in city_counts.index], 
           autopct='%1.1f%%', startangle=140, wedgeprops={'width': 0.4})
ax_pie.set_title(get_arabic("توزيع الطلبات حسب المدينة"), fontsize=14)
st.pyplot(fig_pie)
plt.close(fig_pie)

# 2. الإحصائيات المالية
st.subheader("💰 ملخص المبيعات")
c1, c2 = st.columns(2)
c1.metric("عدد الطلبات", len(tbl))
c2.metric("الإيرادات (LYD)", f"{tbl[p_col].sum():,.0f}")

# 3. صدارة الكتب
st.subheader("📈 صدارة الكتب الأكثر طلباً")
delivered = tbl[tbl[st_c].str.contains('تسليم|تم|مستلم', na=False, case=False)]
if not delivered.empty:
    book_cols = [c for c in df.columns if "Book type" in c or "كتاب" in c]
    data = [{"Book": get_arabic(c), "Qty": pd.to_numeric(delivered[c], errors='coerce').fillna(0).sum()} for c in book_cols]
    df_b = pd.DataFrame(data).query("Qty > 0").sort_values("Qty", ascending=False)
    st.bar_chart(df_b.set_index("Book"))
else:
    st.info("لا توجد مبيعات كتب في طلبات التسليم.")

# 4. الجدول
st.subheader("📋 التفاصيل")
st.table(tbl)
