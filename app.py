 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة الافتراضية لواجهة الويب الفاخرة
st.set_page_config(
    page_title="لوحة تحكم متجر ذكريات / Zekrayat Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دالة تطهير الإيموجي للرسم
def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

# دالة الأيقونات الذكية للبطاقات
def get_icon(col_name):
    c = str(col_name).lower()
    if 'كود' in c or 'code' in c: return '🆔'
    if 'اسم' in c or 'name' in c or 'زبون' in c: return '👤'
    if 'هاتف' in c or 'phone' in c or 'رقم' in c: return '📞'
    if 'سعر' in c or 'إجمالي' in c or 'total' in c or 'price' in c: return '💰'
    if 'حالة' in c or 'status' in c: return '🚦'
    if 'تاريخ' in c or 'date' in c or 'time' in c: return '📅'
    if 'عنوان' in c or 'مكان' in c or 'address' in c: return '📍'
    return '📚'

# --- جلب البيانات السحابية حياً من قوقل شيت ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx&gid=70402037"
try:
    live_url = f"{base_url}&cache_bust={int(time.time())}"
    df = pd.read_excel(live_url)
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    clean_all_temp = df[df[id_c].str.startswith('D-', na=False)]
    clean_ids = sorted([str(x).strip() for x in clean_all_temp[id_c].unique() if str(x).strip() != ''])
    clean_statuses = sorted([str(x).strip() for x in clean_all_temp[st_c].dropna().unique() if str(x).strip() != ''])
except:
    clean_ids = ['D-ORD-1', 'D-ORD-2', 'D-ORD-3', 'D-ORD-4', 'D-ORD-5', 'D-ORD-6']
    clean_statuses = ['تسليم', 'قيد الشحن', 'قيد التجهيز']
    df = pd.DataFrame()

# تصفية وتجهيز الأعمدة
if not df.empty:
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
    df = df.dropna(how='all', axis=1)
    p_cols = [c for c in df.columns if "السعر" in c or "الإجمالي" in c or "Price" in c or "Total" in c]
    p_col = p_cols[0] if p_cols else df.columns[-1]
    name_cols = [c for c in df.columns if "اسم" in c or "الزبون" in c or "العميل" in c or "Name" in c]
    name_col = name_cols[0] if name_cols else df.columns[1]
    clean_all = df[df[id_c].fillna('').astype(str).str.strip().str.startswith('D-')].dropna(subset=[id_c]).copy()
    clean_all[st_c] = clean_all[st_c].fillna('').astype(str).str.strip()
    
    t_cols = [c for c in df.columns if "تاريخ" in c or "Timestamp" in c or "Date" in c]
    date_col = 'parsed_date_only' if t_cols else None
    if t_cols:
        clean_all['parsed_dt'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce')
        clean_all['parsed_date_only'] = clean_all['parsed_dt'].dt.date

# تنسيق الواجهة عبر CSS
st.markdown("""
    <style>
        .stRadio [data-testid="stMarkdownContainer"] p {
            font-size: 16px !important;
            font-weight: 800 !important;
            color: #5c2575 !important;
            font-family: 'Segoe UI', Tahoma, sans-serif !important;
        }
        div[data-testid="stBlock"] { direction: rtl !important; text-align: right !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div style='background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white; font-family:tahoma; margin-bottom:20px;'><h2>📊 لوحة التحكم التنفيذية - متجر ذكريات الفاخر / Zekrayat Store Dashboard</h2></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='background-color:#5c2575; padding:8px; color:white; text-align:center; font-weight:bold; border-radius:4px;'>⚙️ لوحة الفرز والملاحة / Control Panel</div>", unsafe_allow_html=True)

mode = st.sidebar.radio(
    "اختر وضع العرض المطلوب / Select View Mode:",
    ['🔍 تفاصيل طلبية واحدة / Single Order Inquiry', '📊 عرض المجموعات والتقارير / Executive Analytics']
)

# زر التحديث الحي المباشر من السحاب
if st.sidebar.button("🔄 تحديث حياً وجلب البيانات الفورية / Live Fetch Sync", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if 'Single' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب المستهدف / Select Order Code:", clean_ids)
    
    delivered_global_mask = clean_all[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)
    tot_o = len(clean_all.drop_duplicates(subset=[id_c]))
    unique_delivered = clean_all[delivered_global_mask].drop_duplicates(subset=[id_c])
    tot_m = pd.to_numeric(unique_delivered[p_col], errors='coerce').fillna(0).sum()
    
    st.markdown(f"<div style='background:linear-gradient(135deg, #5c2575, #7d3c98); padding:14px; color:white; text-align:right; font-family:tahoma; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><b>📊 إجمالي الطلبات الفريدة بالمنظومة / Total Orders: {tot_o} | 💰 مبيعات الخزينة الكلية المحققة / Total Cash: {tot_m:,} LYD</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#2c3e50; padding:10px; color:white; text-align:right; margin-top:10px; border-radius:6px; font-family:tahoma;'><b>📌 تفاصيل كود الطلب الحالي / Current Order: {selected_id}</b></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    
    matching_rows = df[df[id_c].fillna('').astype(str).str.strip() == str(selected_id).strip()]
    if not matching_rows.empty:
        row = matching_rows.iloc[0]
        for col in df.columns:
            if "رابط" in col or col == 'parsed_date_only' or "parsed_dt" in col or "Unnamed" in str(col) or "Product type" in col: continue
            val = row[col]
            v_str = str(val).strip() if pd.notna(val) else '—'
            
            if "book type" in col.lower() or "نوع الكتاب" in col or "كتاب" in col or "ألبوم" in col:
                try:
                    num_check = float(v_str)
                    if num_check == 0: continue
                    v_str = f"{int(num_check)}"
                except:
                    if v_str in ["0", "0.0", "0.00", "", "—", "nan", "NaN"]: continue
            
            ico = get_icon(col)
            clean_display_header = col.replace('Book type', '').strip()
            if "[" in col and "]" in col:
                match = re.search(r'\[(.*?)\]', col)
                if match: clean_display_header = match.group(1).strip()

            if col == st_c:
                val_element =
