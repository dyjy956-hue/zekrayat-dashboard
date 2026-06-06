 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime, time, re

st.set_page_config(page_title="لوحة تحكم متجر ذكريات", layout="wide", initial_sidebar_state="expanded")

# --- دالات المساعدة الذكية ---
def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

def get_icon(c):
    c = str(c).lower()
    if 'كود' in c or 'code' in c: return '🆔'
    if 'اسم' in c or 'name' in c: return '👤'
    if 'سعر' in c or 'إجمالي' in c or 'total' in c: return '💰'
    if 'حالة' in c or 'status' in c: return '🚦'
    return '📚'

# --- جلب البيانات السحابية حياً ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", sheet_name=0)
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد / Unspecified").astype(str).str.strip()
    clean_ids = sorted([str(x).strip() for x in df[df[id_c].str.startswith('D-', na=False)][id_c].unique() if str(x).strip() != ''])
    clean_statuses = sorted([str(x).strip() for x in df[st_c].unique() if str(x).strip() != ''])
except:
    clean_ids, clean_statuses, df = ['D-ORD-1'], ['تسليم'], pd.DataFrame()

if not df.empty:
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')].dropna(how='all', axis=1)
    p_col = [c for c in df.columns if any(k in c for k in ["السعر", "الإجمالي", "Price", "Total"])][0]
    name_col = [c for c in df.columns if any(k in c for k in ["اسم", "الزبون", "العميل", "Name"])][0]
    clean_all = df[df[id_c].astype(str).str.startswith('D-')].copy()
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
    t_cols = [c for c in df.columns if any(k in c for k in ["تاريخ", "Timestamp", "Date"])]
    date_col = 'parsed_date_only' if t_cols else None
    if t_cols:
        clean_all['parsed_date_only'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce').dt.date

st.markdown("<style>div[data-testid='stBlock'] { direction: rtl !important; text-align: right !important; }</style>", unsafe_allow_html=True)
st.markdown("<div style='background:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white; margin-bottom:20px;'><h2>📊 لوحة تحكم متجر ذكريات الفاخر / Zekrayat Dashboard</h2></div>", unsafe_allow_html=True)

mode = st.sidebar.radio("اختر وضع العرض:", ['🔍 تفاصيل طلبية واحدة', '📊 عرض المجموعات والتقارير'])
if st.sidebar.button("🔄 تحديث البيانات حياً"):
    st.cache_data.clear()
    st.rerun()

if 'Single' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب:", clean_ids)
    matching_rows = df[df[id_c].astype(str).str.strip() == str(selected_id).strip()]
    if not matching_rows.empty:
        row = matching_rows.iloc[0]
        for col in df.columns:
            if "رابط" in col or "parsed" in col or "Unnamed" in str(col): continue
            v_str = str(row[col]).strip() if pd.notna(row[col]) else '—'
            ico = get_icon(col)
            st.markdown(f"<div style='direction:ltr; text-align:left; padding:10px; margin-bottom:5px; background:#fff; border-left:5px solid #5c2575; border-radius:4px;'>{ico} <b>{col}:</b> {v_str}</div>", unsafe_allow_html=True)
else:
    selected_status = st.sidebar.selectbox("اختر الحالة للفرز:", clean_statuses)
    selected_time = st.sidebar.selectbox("اختر النطاق الزمني:", ['كل الأوقات', 'طلبات اليوم فقط', 'طلبات هذا الأسبوع'])
    
    tbl = clean_all[clean_all[st_c].str.contains(str(selected_status).strip(), na=False, case=False)].copy()
    today_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)).date()
    
    if date_col and not tbl.empty:
        if 'اليوم' in selected_time: tbl = tbl[tbl[date_col] == today_date]
        elif 'الأسبوع' in selected_time: tbl = tbl[tbl[date_col] >= (today_date - datetime.timedelta(days=7))]
        
    period_data = clean_all.copy()
    if date_col:
        if 'اليوم' in selected_time: period_data = period_data[period_data[date_col] == today_date]
        elif 'الأسبوع' in selected_time: period_data = period_data[period_data[date_col] >= (today_date - datetime.timedelta(days=7))]

    # --- 🏗️ الأزرار الملونة الثلاثة علوياً ---
    u_period = period_data.drop_duplicates(subset=[id_c])
    c_del = len(u_period[u_period[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)])
    c_shp = len(u_period[u_period[st_c].str.contains('شحن|طريق|مندوب|Shipping', na=False, case=False)])
    c_prp = len(u_period[u_period[st_c].str.contains('تجهيز|تحضير|ورشة|Preparing', na=False, case=False)])
    
    cb1, cb2, cb3 = st.columns(3)
    cb1.markdown(f"<div style='background:linear-gradient(135deg, #2ecc71, #27ae60); padding:15px; border-radius:8px; text-align:center; color:white;'><h3>{c_del}</h3><b>📦 المستلمة / Delivered</b></div>", unsafe_allow_html=True)
    cb2.markdown(f"<div style='background:linear-gradient(135deg, #e67e22, #d35400); padding:15px; border-radius:8px; text-align:center; color:white;'><h3>{c_shp}</h3><b>🚚 في الشحن / Shipping</b></div>", unsafe_allow_html=True)
    cb3.markdown(f"<div style='background:linear-gradient(135deg, #3498db, #2980b9); padding:15px; border-radius:8px; text-align:center; color:white;'><h3>{c_prp}</h3><b>🛠️ قيد التجهيز / Preparing</b></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- حسابات السيولة النقدية ---
    r_sales = period_data[period_data[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)].drop_duplicates(subset=[id_c])[p_col].sum()
    p_sales = period_data[~period_data[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)].drop_duplicates(subset=[id_c])[p_col].sum()
    
    st.markdown(f"<div style='background:#5c2575; padding:10px; color:white; text-align:right; font-weight:bold; border-radius:4px;'>📊 تقرير الحزمة الحالية: {selected_status} | العدد: {len(tbl.drop_duplicates(subset=[id_c]))}</div>", unsafe_allow_html=True)
    ck1, ck2 = st.columns(2)
    ck1.markdown(f"<div style='background:#2ecc71; padding:12px; color:white; border-radius:6px; text-align:right;'><b>💵 كاش مستلم فعلياً بالخزينة:<br><span style='font-size:18px;'>{r_sales:,} LYD</span></b></div>", unsafe_allow_html=True)
    ck2.markdown(f"<div style='background:#e67e22; padding:12px; color:white; border-radius:6px; text-align:right;'><b>⏳ مبالغ معلقة قيد التوصيل:<br><span style='font-size:18px;'>{p_sales:,} LYD</span></b></div>", unsafe_allow_html=True)

    # --- جدول تفاصيل الطلبيات الحالية ---
    st.markdown("<br><b>💎 كشف الحساب التفصيلي للطلبيات الحالية:</b>", unsafe_allow_html=True)
    t_rows = ""
    for idx, row in tbl.drop_duplicates(subset=[id_c]).iterrows():
        b_summary = " + ".join([re.search(r'\[(.*?)\]', col).group(1) if re.search(r'\[(.*?)\]', col) else col for col in clean_all.columns if any(k in col for k in ["Book", "كتاب", "ألبوم"]) if str(row[col]).strip() not in ["0", "0.0", "", "—", "nan", "NaN"]])
        b_summary = b_summary if b_summary else "مبيعات متنوعة"
        t_rows += f"<tr><td style='padding:8px; border-bottom:1px solid #eee;'>{row[id_c]}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{row[name_col]}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{b_summary}</td><td style='padding:8px; border-bottom:1px solid #eee; text-align:center;'>{row[p_col]:,.0f} LYD</td></tr>"
    
    if t_rows:
        st.markdown(f"<table style='width:100%; border-collapse:collapse; direction:rtl;'><thead><tr style='background:#5c2575; color:white;'><th style='padding:10px; text-align:right;'>🆔 الكود</th><th style='padding:10px; text-align:right;'>👤 الاسم</th><th style='padding:10px; text-align:right;'>📚 تفاصيل المنتجات</th><th style='padding:10px; text-align:center;'>💰 السعر</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
    else:
        st.markdown("<div>لا توجد بيانات متاحة حالياً.</div>", unsafe_allow_html=True)

    # --- الرسوم البيانية القياسية الإنجليزية ---
    st.markdown("<br><b>📊 التحليلات البيانية المتقدمة / Analytics:</b>", unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)
    with cc1:
        if r_sales > 0 or p_sales > 0:
            fig1, ax1 = plt.subplots(figsize=(5, 3.5))
            ax1.pie([r_sales, p_sales], labels=['Received', 'Pending'], autopct='%1.1f%%', startangle=140, colors=['#2ecc71', '#e67e22'])
            ax1.set_title("Cashflow Split (LYD)", fontsize=9, weight='bold')
            st.pyplot(fig1)
