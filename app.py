 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime, time, re

st.set_page_config(page_title="لوحة تحكم متجر ذكريات", layout="wide", initial_sidebar_state="expanded")

def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

# --- جلب البيانات السحابية حياً من قوقل شيت ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", sheet_name=0)
    
    # تحديد الأعمدة بالاسم أو بالترتيب الاحتياطي لمنع الاختفاء تماماً
    id_c = [c for c in df.columns if any(k in c for k in ["كود", "Code"])][0] if [c for c in df.columns if any(k in c for k in ["كود", "Code"])] else df.columns[0]
    st_c = [c for c in df.columns if any(k in c for k in ["حالة", "Status"])][0] if [c for c in df.columns if any(k in c for k in ["حالة", "Status"])] else df.columns[4]
    p_col = [c for c in df.columns if any(k in c for k in ["سعر", "إجمالي", "Price", "Total"])][0] if [c for c in df.columns if any(k in c for k in ["سعر", "إجمالي", "Price", "Total"])] else df.columns[-1]
    name_col = [c for c in df.columns if any(k in c for k in ["اسم", "زبون", "عميل", "Name"])][0] if [c for c in df.columns if any(k in c for k in ["اسم", "زبون", "عميل", "Name"])] else df.columns[1]
    
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد / Unspecified").astype(str).str.strip()
    
    clean_all = df[df[id_c].astype(str).str.startswith('D-')].copy()
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
    
    clean_ids = sorted([str(x).strip() for x in clean_all[id_c].unique() if str(x).strip() != ''])
    clean_statuses = sorted([str(x).strip() for x in clean_all[st_c].unique() if str(x).strip() != ''])
except:
    clean_ids, clean_statuses, df, clean_all = ['D-ORD-1'], ['تسليم'], pd.DataFrame(), pd.DataFrame()

# ضبط التواريخ بشكل مجرد
date_col = None
if not clean_all.empty:
    t_cols = [c for c in clean_all.columns if any(k in c for k in ["تاريخ", "Timestamp", "Date"])]
    if t_cols:
        date_col = 'parsed_date_only'
        clean_all['parsed_date_only'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce').dt.date

st.markdown("<style>div[data-testid='stBlock'] { direction: rtl !important; text-align: right !important; }</style>", unsafe_allow_html=True)
st.markdown("<div style='background:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white; margin-bottom:20px;'><h2>📊 لوحة تحكم متجر ذكريات الفاخر / Zekrayat Dashboard</h2></div>", unsafe_allow_html=True)

mode = st.sidebar.radio("اختر وضع العرض:", ['🔍 تفاصيل طلبية واحدة', '📊 عرض المجموعات والتقارير'])
if st.sidebar.button("🔄 تحديث البيانات حياً"):
    st.cache_data.clear()
    st.rerun()

if clean_all.empty:
    st.error("⚠️ فشل الاتصال برابط الشيت أو لا توجد أك
