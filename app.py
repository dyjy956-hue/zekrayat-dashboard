 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة
st.set_page_config(page_title="لوحة تحكم متجر ذكريات / Zekrayat Dashboard", layout="wide", initial_sidebar_state="expanded")

# دوال مساعدة
def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

def get_icon(col_name):
    c = str(col_name).lower()
    if 'كود' in c or 'code' in c: return '🆔'
    if 'اسم' in c or 'name' in c or 'زبون' in c: return '👤'
    if 'سعر' in c or 'إجمالي' in c or 'total' in c or 'price' in c: return '💰'
    if 'حالة' in c or 'status' in c: return '🚦'
    if 'عنوان' in c or 'مكان' in c or 'مدينة' in c: return '📍'
    return '📚'

# --- جلب البيانات ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", sheet_name=0)
    
    # تحديد الأعمدة بمرونة
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    p_col = [c for c in df.columns if "سعر" in c or "إجمالي" in c or "Price" in c][0]
    name_col = [c for c in df.columns if "اسم" in c or "الزبون" in c][0]
    # محاولة كشف عمود المدينة
    city_cols = [c for c in df.columns if "مدينة" in c or "عنوان" in c or "City" in c]
    city_c = city_cols[0] if city_cols else None
    
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد").astype(str).str.strip()
    if city_c: df[city_c] = df[city_c].fillna("غير محدد").astype(str).str.strip()
    df[p_col] = pd.to_numeric(df[p_col], errors='coerce').fillna(0)
    
    clean_all = df[df[id_c].str.startswith('D-', na=False)].copy()
except Exception as e:
    st.error(f"خطأ في جلب البيانات: {e}")
    clean_all = pd.DataFrame()

# --- CSS وتصميم الواجهة ---
st.markdown("<style>.stRadio p {font-size: 16px !important; font-weight: 800 !important; color: #5c2575 !important;} div[data-testid='stBlock'] { direction: rtl !important; text-align: right !important; }</style>", unsafe_allow_html=True)
st.markdown("<div style='background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white;'><h2>📊 لوحة التحكم التنفيذية - متجر ذكريات</h2></div>", unsafe_allow_html=True)

mode = st.sidebar.radio("وضع العرض:", ['🔍 تفاصيل طلبية', '📊 تقارير الأداء'])

if mode == '🔍 تفاصيل طلبية':
    selected_id = st.sidebar.selectbox("اختر كود الطلب:", sorted(clean_all[id_c].unique()))
    row = clean_all[clean_all[id_c] == selected_id].iloc[0]
    for col in df.columns:
        st.markdown(f"**{get_icon(col)} {col}:** {row[col]}")
else:
    # التقارير
    selected_status = st.sidebar.selectbox("فلترة الحالة:", ['الكل'] + sorted(clean_all[st_c].unique().tolist()))
    tbl = clean_all.copy()
    if selected_status != 'الكل': tbl = tbl[tbl[st_c] == selected_status]

    # أزرار الإحصائيات (KPIs)
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 الطلبات المستلمة", len(tbl[tbl[st_c].str.contains('تسليم|تم', na=False)]))
    c2.metric("🚚 في الشحن", len(tbl[tbl[st_c].str.contains('شحن', na=False)]))
    c3.metric("🛠️ قيد التجهيز", len(tbl[tbl[st_c].str.contains('تجهيز', na=False)]))

    # تحليل المدن (بشكل آمن)
    if city_c and city_c in tbl.columns:
        st.markdown("<br><h3>📍 التوزيع الجغرافي للمبيعات</h3>", unsafe_allow_html=True)
        city_counts = tbl.groupby(city_c)[id_c].nunique().sort_values(ascending=False)
        fig_c, ax_c = plt.subplots(figsize=(8, 3))
        city_counts.plot(kind='bar', color='#7d3c98', ax=ax_c)
        st.pyplot(fig_c)
    else:
        st.warning("عمود المدينة غير موجود في ملف البيانات.")

    # صدارة الكتب
    st.subheader("📈 صدارة المنتجات")
    delivered = tbl[tbl[st_c].str.contains('تسليم|تم', na=False)]
    book_cols = [c for c in df.columns if "Book type" in c or "كتاب" in c]
    if not delivered.empty and book_cols:
        data = [{"المنتج": c, "الكمية": pd.to_numeric(delivered[c], errors='coerce').fillna(0).sum()} for c in book_cols]
        df_b = pd.DataFrame(data).query("الكمية > 0").sort_values("الكمية", ascending=False)
        st.bar_chart(df_b.set_index("المنتج"))
    
    # الجدول
    st.table(tbl)
