 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime, time, re

st.set_page_config(page_title="Zekrayat Dashboard", layout="wide", initial_sidebar_state="expanded")

def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

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
    st.error(f"Error loading columns: {e}")
    st.stop()

t_cols = [c for c in clean_all.columns if any(k in c for k in ["تاريخ", "Timestamp", "Date"])]
clean_all['p_date'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce').dt.date if t_cols else None

# إعداد الواجهة الرسمية للمنظومة
st.title("📊 لوحة تحكم متجر ذكريات الفاخر / Zekrayat Dashboard")
st.markdown("---")

mode = st.sidebar.radio("اختر وضع العرض:", ['🔍 تفاصيل طلبية واحدة', '📊 عرض المجموعات والتقارير'])
if st.sidebar.button("🔄 تحديث البيانات حياً"):
    st.cache_data.clear()
    st.rerun()

if 'Single' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب المستهدف:", clean_ids)
    row = clean_all[clean_all[id_c] == selected_id].iloc[0]
    st.subheader(f"📌 كشف التفاصيل الكاملة للطلب: {selected_id}")
    
    # عرض تفاصيل الكود بشكل منظم جداً وبدون أخطاء
    for col in df.columns:
        if "Unnamed" in str(col) or col == 'p_date': continue
        val = str(row[col]).strip() if pd.notna(row[col]) else "—"
        if any(k in col.lower() for k in ["book", "كتاب", "ألبوم"]) and val in ["0", "0.0"]: continue
        st.info(f"🔹 {col}: {val}")
else:
    selected_status = st.sidebar.selectbox("اختر الحالة للفرز الحركي:", clean_statuses)
    selected_time = st.sidebar.selectbox("اختر النطاق الزمني:", ['كل الأوقات', 'طلبات اليوم فقط', 'طلبات هذا الأسبوع'])
    
    tbl = clean_all[clean_all[st_c] == selected_status].copy()
    period_data = clean_all.copy()
    today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)).date()
    
    if 'p_date' in clean_all.columns:
        if 'اليوم' in selected_time:
            tbl = tbl[tbl['p_date'] == today]
            period_data = period_data[period_data['p_date'] == today]
        elif 'الأسبوع' in selected_time:
            tbl = tbl[tbl['p_date'] >= (today - datetime.timedelta(days=7))]
            period_data = period_data[period_data[p_date] >= (today - datetime.timedelta(days=7))]

    u_period = period_data.drop_duplicates(subset=[id_c])
    c_del = len(u_period[u_period[st_c].str.contains('تسليم|تم|مستلم', na=False)])
    c_shp = len(u_period[u_period[st_c].str.contains('شحن|طريق|مندوب', na=False)])
    c_prp = len(u_period[u_period[st_c].str.contains('تجهيز|تحضير|ورشة', na=False)])
    
    # 🏗️ عرض العدادات الثلاثة الأصلية لـ
