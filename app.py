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
    st_cols = [c for c in df.columns if "حالة" in c or "Status" in c]
    st_c = st_cols[0] if st_cols else "الحالة"
    city_col = [c for c in df.columns if "مدينة" in c or "عنوان" in c or "City" in c][0]
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد").astype(str).str.strip()
    df[city_col] = df[city_col].fillna("غير محدد").astype(str).str.strip()
    clean_all = df[df[id_c].str.startswith('D-', na=False)].copy()
    clean_ids = sorted([str(x).strip() for x in clean_all[id_c].unique()])
    clean_statuses = sorted([str(x).strip() for x in df[st_c].unique()])
except:
    clean_ids, clean_statuses, df, clean_all = ['D-ORD-1'], ['تسليم'], pd.DataFrame(), pd.DataFrame()

# تصفية وتجهيز الأعمدة
if not df.empty:
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
    p_cols = [c for c in df.columns if "السعر" in c or "الإجمالي" in c or "Price" in c or "Total" in c]
    p_col = p_cols[0] if p_cols else "السعر الصافي"
    name_cols = [c for c in df.columns if "اسم" in c or "الزبون" in c or "Name" in c]
    name_col = name_cols[0] if name_cols else df.columns[1]
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
    t_cols = [c for c in df.columns if "تاريخ" in c or "Date" in c]
    date_col = 'parsed_date_only' if t_cols else None
    if t_cols:
        clean_all['parsed_dt'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce')
        clean_all['parsed_date_only'] = clean_all['parsed_dt'].dt.date

# الواجهة و CSS
st.markdown("<style>.stRadio [data-testid='stMarkdownContainer'] p {font-size: 16px !important; font-weight: 800 !important; color: #5c2575 !important;} div[data-testid='stBlock'] { direction: rtl !important; text-align: right !important; }</style>", unsafe_allow_html=True)
st.markdown("<div style='background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white;'><h2>📊 لوحة التحكم التنفيذية - متجر ذكريات</h2></div>", unsafe_allow_html=True)

mode = st.sidebar.radio("وضع العرض:", ['🔍 تفاصيل طلبية واحدة', '📊 عرض التقارير'])

if 'Single' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب:", clean_ids)
    matching_rows = df[df[id_c] == selected_id]
    if not matching_rows.empty:
        row = matching_rows.iloc[0]
        for col in df.columns:
            st.markdown(f"**{get_icon(col)} {col}:** {row[col]}")
else:
    selected_status = st.sidebar.selectbox("فلترة الحالة:", clean_statuses)
    tbl = clean_all[clean_all[st_c] == selected_status].copy()
    
    # الإحصائيات والأزرار الملونة
    unique_all = tbl.drop_duplicates(subset=[id_c])
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 المستلمة", len(unique_all[unique_all[st_c].str.contains('تسليم|تم', na=False)]))
    c2.metric("🚚 الشحن", len(unique_all[unique_all[st_c].str.contains('شحن', na=False)]))
    c3.metric("🛠️ التجهيز", len(unique_all[unique_all[st_c].str.contains('تجهيز', na=False)]))
    
    # --- الإضافة الجديدة: تقرير المدن ---
    st.markdown("<br><h3>📍 توزيع المبيعات حسب المدينة</h3>", unsafe_allow_html=True)
    city_data = tbl.groupby(city_col)[id_c].nunique().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 3))
    city_data.plot(kind='bar', color='#7d3c98', ax=ax)
    st.pyplot(fig)
    
    # صدارة الكتب
    st.subheader("📈 صدارة الكتب")
    delivered = tbl[tbl[st_c].str.contains('تسليم|تم|مستلم', na=False, case=False)]
    book_cols = [c for c in df.columns if "Book type" in c or "كتاب" in c]
    if not delivered.empty and book_cols:
        data = [{"المنتج": c, "الكمية": pd.to_numeric(delivered[c], errors='coerce').fillna(0).sum()} for c in book_cols]
        df_b = pd.DataFrame(data).query("الكمية > 0").sort_values("الكمية", ascending=False)
        st.bar_chart(df_b.set_index("المنتج"))
    
    st.table(tbl)
