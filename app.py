 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime, time, re

st.set_page_config(page_title="متجر ذكريات", layout="wide", initial_sidebar_state="expanded")

# --- جلب البيانات السحابية حياً من قوقل شيت ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", sheet_name=0)
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    p_col = [c for c in df.columns if any(k in c for k in ["سعر", "إجمالي", "Price", "Total"])][0]
    name_col = [c for c in df.columns if any(k in c for k in ["اسم", "زبون", "عميل", "Name"])][0]
    
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد").astype(str).str.strip()
    clean_all = df[df[id_c] != ''].copy()
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
    clean_ids = sorted([str(x).strip() for x in clean_all[id_c].unique() if str(x).strip() != ''])
    clean_statuses = sorted([str(x).strip() for x in clean_all[st_c].unique() if str(x).strip() != ''])
except Exception as e:
    st.error(f"⚠️ خطأ في قراءة أعمدة الشيت: {e}")
    st.stop()

t_cols = [c for c in clean_all.columns if any(k in c for k in ["تاريخ", "Timestamp", "Date"])]
clean_all['p_date'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce').dt.date if t_cols else None

st.markdown("<style>div[data-testid='stBlock'] { direction: rtl !important; text-align: right !important; }</style>", unsafe_allow_html=True)
st.markdown("<div style='background:#2c3e50; padding:12px; border-radius:8px; text-align:center; color:white; margin-bottom:15px;'><h2>📊 لوحة تحكم متجر ذكريات الفاخر / Zekrayat Dashboard</h2></div>", unsafe_allow_html=True)

mode = st.sidebar.radio("اختر وضع العرض:", ['🔍 تفاصيل طلبية واحدة', '📊 عرض المجموعات والتقارير'])
if st.sidebar.button("🔄 تحديث البيانات حياً"):
    st.cache_data.clear()
    st.rerun()

if 'Single' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب:", clean_ids)
    row = clean_all[clean_all[id_c] == selected_id].iloc[0]
    st.markdown(f"<div style='background:#5c2575; padding:8px; color:white; border-radius:4px; margin-bottom:10px;'><b>📌 تفاصيل الطلب الحالي: {selected_id}</b></div>", unsafe_allow_html=True)
    for col in df.columns:
        if "Unnamed" in str(col) or col == 'p_date': continue
        val = str(row[col]).strip() if pd.notna(row[col]) else "—"
        if any(k in col.lower() for k in ["book", "كتاب", "ألبوم"]) and val in ["0", "0.0"]: continue
        st.markdown(f"<div style='direction:ltr; text-align:left; padding:8px; margin-bottom:4px; background:#fff; border-left:4px solid #5c2575; border-radius:4px;'><b>{col}:</b> {val}</div>", unsafe_allow_html=True)
else:
    selected_status = st.sidebar.selectbox("اختر الحالة للفرز:", clean_statuses)
    selected_time = st.sidebar.selectbox("اختر النطاق الزمني:", ['كل الأوقات', 'طلبات اليوم فقط', 'طلبات هذا الأسبوع'])
    
    tbl = clean_all[clean_all[st_c] == selected_status].copy()
    period_data = clean_all.copy()
    today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)).date()
    
    if 'p_date' in clean_all.columns:
        if 'اليوم' in selected_time:
            tbl, period_data = tbl[tbl['p_date'] == today], period_data[period_data['p_date'] == today]
        elif 'الأسبوع' in selected_time:
            tbl, period_data = tbl[tbl['p_date'] >= (today - datetime.timedelta(days=7))], period_data[period_data['p_date'] >= (today - datetime.timedelta(days=7))]

    u_period = period_data.drop_duplicates(subset=[id_c])
    c_del = len(u_period[u_period[st_c].str.contains('تسليم|تم|مستلم', na=False)])
    c_shp = len(u_period[u_period[st_c].str.contains('شحن|طريق|مندوب', na=False)])
    c_prp = len(u_period[u_period[st_c].str.contains('تجهيز|تحضير|ورشة', na=False)])
    
    cb1, cb2, cb3 = st.columns(3)
    cb1.markdown(f"<div style='background:linear-gradient(135deg, #2ecc71, #27ae60); padding:12px; border-radius:6px; text-align:center; color:white;'><h3>{c_del}</h3><b>📦 المستلمة / Delivered</b></div>", unsafe_allow_html=True)
    cb2.markdown(f"<div style='background:linear-gradient(135deg, #e67e22, #d35400); padding:12px; border-radius:6px; text-align:center; color:white;'><h3>{c_shp}</h3><b>🚚 في الشحن / Shipping</b></div>", unsafe_allow_html=True)
    cb3.markdown(f"<div style='background:linear-gradient(135deg, #3498db, #2980b9); padding:12px; border-radius:6px; text-align:center; color:white;'><h3>{c_prp}</h3><b>🛠️ قيد التجهيز / Preparing</b></div>", unsafe_allow_html=True)
    
    r_sales = u_period[u_period[st_c].str.contains('تسليم|تم|مستلم', na=False)][p_col].sum()
    p_sales = u_period[~u_period[st_c].str.contains('تسليم|تم|مستلم', na=False)][p_col].sum()
    
    st.markdown("<br>", unsafe_allow_html=True)
    ck1, ck2 = st.columns(2)
    ck1.markdown(f"<div style='background:#2ecc71; padding:10px; color:white; border-radius:4px;'><b>💵 كاش مستلم فعلياً بالخزينة: {r_sales:,} LYD</b></div>", unsafe_allow_html=True)
    ck2.markdown(f"<div style='background:#e67e22; padding:10px; color:white; border-radius:4px;'><b>⏳ مبالغ معلقة قيد التوص
