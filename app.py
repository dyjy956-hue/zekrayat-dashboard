 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة
st.set_page_config(
    page_title="لوحة تحكم متجر ذكريات",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- دوال مساعدة ---
def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

def get_icon(col_name):
    c = str(col_name).lower()
    if 'كود' in c or 'code' in c: return '🆔'
    if 'اسم' in c or 'name' in c or 'زبون' in c: return '👤'
    if 'هاتف' in c or 'phone' in c or 'رقم' in c: return '📞'
    if 'سعر' in c or 'إجمالي' in c or 'total' in c or 'price' in c: return '💰'
    if 'حالة' in c or 'status' in c: return '🚦'
    if 'تاريخ' in c or 'date' in c or 'time' in c: return '📅'
    if 'عنوان' in c or 'مدينة' in c or 'address' in c: return '📍'
    return '📚'

# --- جلب البيانات ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", sheet_name=0)
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    p_col = [c for c in df.columns if "السعر" in c or "الإجمالي" in c or "Price" in c][0]
    name_col = [c for c in df.columns if "اسم" in c or "الزبون" in c][0]
    city_col = [c for c in df.columns if "مدينة" in c or "عنوان" in c or "City" in c][0]
    t_col = [c for c in df.columns if "تاريخ" in c or "Date" in c][0]

    df[id_c] = df[id_c].astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد").astype(str).str.strip()
    df[p_col] = pd.to_numeric(df[p_col], errors='coerce').fillna(0)
    df[t_col] = pd.to_datetime(df[t_col], errors='coerce')
except:
    st.error("خطأ في جلب البيانات من الملف")
    st.stop()

# --- الواجهة ---
st.markdown("<h2 style='text-align: center; color: #5c2575;'>📊 لوحة التحكم التنفيذية - متجر ذكريات</h2>", unsafe_allow_html=True)
mode = st.sidebar.radio("وضع العرض:", ['🔍 تفاصيل طلبية واحدة', '📊 تقارير الأداء الشاملة'])

if mode == '🔍 تفاصيل طلبية واحدة':
    selected_id = st.sidebar.selectbox("اختر كود الطلب:", sorted(df[id_c].unique()))
    row = df[df[id_c] == selected_id].iloc[0]
    for col in df.columns:
        st.markdown(f"**{get_icon(col)} {col}:** {row[col]}")

else:
    # الفلاتر
    selected_status = st.sidebar.selectbox("فلترة الحالة:", ['الكل'] + sorted(df[st_c].unique().tolist()))
    tbl = df.copy()
    if selected_status != 'الكل': tbl = tbl[tbl[st_c] == selected_status]
    
    delivered = tbl[tbl[st_c].str.contains('تسليم|تم|مستلم', na=False, case=False)]

    # 1. إحصائيات سريعة
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الطلبات", len(tbl))
    c2.metric("طلبات مسلّمة", len(delivered))
    c3.metric("الإيرادات (LYD)", f"{delivered[p_col].sum():,.0f}")

    # 2. تحليل المدن (الإضافة الجديدة)
    st.markdown("---")
    st.subheader("📍 التوزيع الجغرافي للمبيعات")
    if not delivered.empty:
        city_data = delivered.groupby(city_col)[id_c].count().sort_values(ascending=False)
        fig_c, ax_c = plt.subplots(figsize=(8, 3))
        city_data.plot(kind='bar', ax=ax_c, color='#7d3c98')
        ax_c.set_title("عدد الطلبيات حسب المدينة")
        st.pyplot(fig_c)
    
    # 3. صدارة الكتب
    st.subheader("📈 صدارة المنتجات")
    book_cols = [c for c in df.columns if "نوع الكتاب" in c or "Book type" in c]
    if book_cols:
        book_sums = delivered[book_cols].sum().sort_values(ascending=False)
        st.bar_chart(book_sums)

    # 4. الجدول
    st.subheader("📋 كشف الطلبات")
    st.dataframe(tbl, use_container_width=True)
