 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

st.set_page_config(
    page_title="Zekrayat Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- محرك دمج الخط العربي للرسومات ---
def fix_arabic_text_for_charts(text):
    text = str(text).strip()
    if not text: return ""
    replacements = {
        "تسليم": "مـسـتـلـم",
        "تم": "تـم",
        "قيد الشحن": "فـي الـشـحـن",
        "قيد التجهيز": "قـيـد الـتـجـهـيـز",
        "كبير": "كـبـيـر",
        "وسط": "وسـط",
        "صغير": "صـغـيـر",
        "مخمل": "مـخـمـل",
        "جلد": "جـلـد",
        "ألبوم": "ألـبـوم",
        "كتاب": "كـتـاب",
        "Received Revenue": "Received Cash",
        "Pending Revenue": "Pending Cash"
    }
    for key, value in replacements.items():
        if key in text: text = text.replace(key, value)
    return text

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
    if 'عنوان' in c or 'مكان' in c or 'address' in c: return '📍'
    return '📚'

# --- جلب البيانات السحابية حياً من قوقل شيت ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    live_url = f"{base_url}&cache_bust={int(time.time())}"
    df = pd.read_excel(live_url, sheet_name=0)
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_cols = [c for c in df.columns if "حالة" in c or "Status" in c]
    st_c = st_cols[0] if st_cols else "الحالة"
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد / Unspecified").astype(str).str.strip()
    clean_all_temp = df[df[id_c].str.startswith('D-', na=False)]
    clean_ids = sorted([str(x).strip() for x in clean_all_temp[id_c].unique() if str(x).strip() != ''])
    clean_statuses = sorted([str(x).strip() for x in df[st_c].unique() if str(x).strip() != ''])
except:
    clean_ids = ['D-ORD-1', 'D-ORD-2']
    clean_statuses = ['تسليم', 'قيد الشحن']
    df = pd.DataFrame()

if not df.empty:
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')].dropna(how='all', axis=1)
    p_cols = [c for c in df.columns if "السعر" in c or "الإجمالي" in c or "Price" in c or "Total" in c]
    p_col = p_cols[0] if p_cols else "السعر الصافي"
    if p_col not in df.columns: df[p_col] = 0
    name_cols = [c for c in df.columns if "اسم" in c or "الزبون" in c or "Name" in c]
    name_col = name_cols[0] if name_cols else df.columns[1]
    clean_all = df[df[id_c].fillna('').astype(str).str.strip().str.startswith('D-')].copy()
    clean_all[st_c] = clean_all[st_c].fillna("غير محدد / Unspecified").astype(str).str.strip()
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
    t_cols = [c for c in df.columns if "تاريخ" in c or "Timestamp" in c or "Date" in c]
    date_col = 'parsed_date_only' if t_cols else None
    if t_cols:
        clean_all['parsed_dt'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce')
        clean_all['parsed_date_only'] = clean_all['parsed_dt'].dt.date

st.markdown("<style>div[data-testid='stBlock'] { direction: rtl !important; text-align: right !important; }</style>", unsafe_allow_html=True)
st.markdown("<div style='background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white; font-family:tahoma; margin-bottom:20px;'><h2>📊 لوحة التحكم التنفيذية - متجر ذكريات الفاخر / Zekrayat Store Dashboard</h2></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='background-color:#5c2575; padding:8px; color:white; text-align:center; font-weight:bold; border-radius:4px;'>⚙️ لوحة الفرز والملاحة / Control Panel</div>", unsafe_allow_html=True)

mode = st.sidebar.radio("اختر وضع العرض المطلوب / Select View Mode:", ['🔍 تفاصيل طلبية واحدة / Single Order Inquiry', '📊 عرض المجموعات والتقارير / Executive Analytics'])

if st.sidebar.button("🔄 تحديث حياً وجلب البيانات الفورية / Live Fetch Sync", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if 'Single' in mode:
    selected_id = st.sidebar.selectbox
