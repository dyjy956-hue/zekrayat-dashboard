 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة
st.set_page_config(page_title="لوحة تحكم متجر ذكريات / Zekrayat Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- الدوال المساعدة ---
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
    if 'عنوان' in c or 'مكان' in c or 'address' in c or 'مدينة' in c: return '📍'
    return '📚'

# --- جلب البيانات ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    live_url = f"{base_url}&cache_bust={int(time.time())}"
    df = pd.read_excel(live_url, sheet_name=0)
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    p_col = [c for c in df.columns if "السعر" in c or "الإجمالي" in c or "Price" in c][0]
    city_c = [c for c in df.columns if any(k in str(c) for k in ["مدينة", "عنوان", "City"])][0]
    name_col = [c for c in df.columns if "اسم" in c or "الزبون" in c][0]
    
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد").astype(str).str.strip()
    df[city_c] = df[city_c].fillna("غير محدد").astype(str).str.strip()
    clean_all = df[df[id_c].str.startswith('D-', na=False)].copy()
except:
    clean_all = pd.DataFrame()

# --- التصميم الأساسي ---
st.markdown("<div style='background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white;'><h2>📊 لوحة التحكم التنفيذية - متجر ذكريات الفاخر</h2></div>", unsafe_allow_html=True)
mode = st.sidebar.radio("وضع العرض:", ['🔍 تفاصيل طلبية واحدة', '📊 عرض المجموعات والتقارير'])

if mode == '🔍 تفاصيل طلبية واحدة':
    selected_id = st.sidebar.selectbox("اختر كود الطلب:", sorted(clean_all[id_c].unique()))
    row = clean_all[clean_all[id_c] == selected_id].iloc[0]
    for col in df.columns:
        st.markdown(f"<div style='padding:10px; border-bottom:1px solid #ddd;'><b>{get_icon(col)} {col}:</b> {row[col]}</div>", unsafe_allow_html=True)
else:
    # --- التقارير والأزرار الملونة الطويلة ---
    tbl = clean_all.copy()
    
    # 1. أزرار إحصائية بتنسيق كامل
    col1, col2, col3 = st.columns(3)
    col1.markdown("<div style='background:#27ae60; padding:20px; color:white; border-radius:10px; text-align:center;'><b>📦 الطلبات المستلمة</b><br><h3>" + str(len(tbl[tbl[st_c].str.contains('تسليم', na=False)])) + "</h3></div>", unsafe_allow_html=True)
    col2.markdown("<div style='background:#d35400; padding:20px; color:white; border-radius:10px; text-align:center;'><b>🚚 طلبات الشحن</b><br><h3>" + str(len(tbl[tbl[st_c].str.contains('شحن', na=False)])) + "</h3></div>", unsafe_allow_html=True)
    col3.markdown("<div style='background:#2980b9; padding:20px; color:white; border-radius:10px; text-align:center;'><b>🛠️ قيد التجهيز</b><br><h3>" + str(len(tbl[tbl[st_c].str.contains('تجهيز', na=False)])) + "</h3></div>", unsafe_allow_html=True)

    # 2. إضافة تقرير المدن الطويل
    st.markdown("<br><h3>📍 تحليل المبيعات الجغرافي (المدن)</h3>", unsafe_allow_html=True)
    city_data = tbl.groupby(city_col)[id_c].nunique().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 4))
    city_data.plot(kind='bar', color='#5c2575', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 3. صدارة الكتب (جدول + رسم)
    st.subheader("📈 صدارة المنتجات")
    delivered = tbl[tbl[st_c].str.contains('تسليم|تم', na=False)]
    if not delivered.empty:
        book_cols = [c for c in df.columns if "Book" in c or "كتاب" in c]
        for col in book_cols:
            st.write(f"{col}: {pd.to_numeric(delivered[col], errors='coerce').fillna(0).sum()} قطعة")
    
    # 4. الجدول التفصيلي
    st.subheader("📋 كشف الحساب")
    st.dataframe(tbl, use_container_width=True)
