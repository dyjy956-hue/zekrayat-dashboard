 import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة الافتراضية لواجهة الويب الفاخرة
st.set_page_config(
    page_title="لوحة تحكم متجر ذكريات",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دالة تحويل النصوص العربية للرسم البياني
def fix_arabic(text):
    return str(text)

# دالة تطهير الإيموجي للرسم
def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

# دالة تحديد ألوان الحالات لبطاقات الأداء
def get_color_style(status_text):
    st_str = str(status_text).strip().lower()
    if any(k in st_str for k in ['تسليم', 'تم', 'done', 'delivered', 'مستلم']):
        return 'linear-gradient(135deg, #2ecc71, #117a65)', '#e8f8f5'
    elif any(k in st_str for k in ['شحن', 'طريق', 'مندوب', 'shipping', 'shipped', 'route']):
        return 'linear-gradient(135deg, #e67e22, #b9770e)', '#fef5e7'
    return 'linear-gradient(135deg, #3498db, #2471a3)', '#eaf2f8'

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
    date_col = 'parsed_dt' if t_cols else None
    if t_cols: clean_all['parsed_dt'] = pd.to_datetime(clean_all[t_cols[0]], errors='coerce')

# تنسيق أزرار الاختيار عبر CSS لتكون ضخمة جداً ومريحة للعين (font-size: 16px)
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

st.markdown("<div style='background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white; font-family:tahoma; margin-bottom:20px;'><h2>📊 لوحة التحكم التنفيذية - متجر ذكريات الفاخر</h2></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='background-color:#5c2575; padding:8px; color:white; text-align:center; font-weight:bold; border-radius:4px;'>⚙️ لوحة الفرز والملاحة</div>", unsafe_allow_html=True)

mode = st.sidebar.radio(
    "اختر وضع العرض المطلوب:",
    ['🔍 تفاصيل طلبية واحدة / Single Order Inquiry', '📊 عرض المجموعات والتقارير / Executive Analytics']
)

# زر التحديث الحي المباشر من السحاب
if st.sidebar.button("🔄 تحديث حياً وجلب البيانات الفورية / Live Fetch Sync", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if 'Single' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب المستهدف:", clean_ids)
    
    delivered_global_mask = clean_all[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)
    tot_o = len(clean_all.drop_duplicates(subset=[id_c]))
    unique_delivered = clean_all[delivered_global_mask].drop_duplicates(subset=[id_c])
    tot_m = pd.to_numeric(unique_delivered[p_col], errors='coerce').fillna(0).sum()
    
    st.markdown(f"<div style='background:linear-gradient(135deg, #5c2575, #7d3c98); padding:14px; color:white; text-align:right; font-family:tahoma; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><b>📊 إجمالي الطلبات الفريدة بالمنظومة: {tot_o} | 💰 مبيعات الخزينة الكلية المحققة: {tot_m:,} LYD</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#2c3e50; padding:10px; color:white; text-align:right; margin-top:10px; border-radius:6px; font-family:tahoma;'><b>📌 تفاصيل كود الطلب الحالي: {selected_id}</b></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    
    matching_rows = df[df[id_c].fillna('').astype(str).str.strip() == str(selected_id).strip()]
    if not matching_rows.empty:
        row = matching_rows.iloc[0]
        for col in df.columns:
            if "رابط" in col or col == 'parsed_dt' or "Unnamed" in str(col) or "Product type" in col: continue
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
                val_element = get_status_badge(v_str)
            else:
                clr = '#117a65' if col == p_col else '#2c3e50'
                fsz = '14px' if col == p_col else '13px'
                val_element = f"<span style='color:{clr}; font-weight:bold; font-size:{fsz}; font-family:tahoma;'>{v_str}</span>"
            
            st.markdown(f"""
            <div style="direction: ltr; text-align: left; padding: 12px 16px; margin-bottom: 8px; background: #ffffff; border-left: 5px solid #5c2575; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); display: flex; align-items: center;">
                <div style="font-size: 16px; margin-right: 12px;">{ico}</div>
                <div style="min-width: 220px; color: #7f8c8d; font-weight: bold; font-family: tahoma; font-size: 13px;">{clean_display_header}</div>
                <div style="flex-grow: 1;">{val_element}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    selected_status = st.sidebar.selectbox("اختر حالة المجموعة للتصفية:", clean_statuses)
    selected_time = st.sidebar.selectbox("اختر النطاق الزمني للتقرير:", ['كل الأوقات (All)', 'طلبات اليوم فقط (Today)', 'طلبات هذا الأسبوع (This Week)'])
    
    clean_status_val = str(selected_status).replace('✔', '').replace('🟢', '').replace('🟠', '').replace('🔵', '').strip()
    tbl = clean_all[clean_all[st_c].str.contains(clean_status_val, na=False, case=False)].copy()
    
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    libya_now = now_utc + datetime.timedelta(hours=2)
    today_start = datetime.datetime(libya_now.year, libya_now.month, libya_now.day, 0, 0, 0)
    today_end = datetime.datetime(libya_now.year, libya_now.month, libya_now.day, 23, 59, 59)
    start_of_week = today_start - datetime.timedelta(days=7)
    period_data = clean_all.copy()

    if date_col and not tbl.empty:
        if 'Today' in selected_time: tbl = tbl[(tbl[date_col] >= today_start) & (tbl[date_col] <= today_end)]
        elif 'This Week' in selected_time: tbl = tbl[(tbl[date_col] >= start_of_week) & (tbl[date_col] <= today_end)]
    if date_col and not period_data.empty:
        if 'Today' in selected_time: period_data = period_data[(period_data[date_col] >= today_start) & (period_data[date_col] <= today_end)]
        elif 'This Week' in selected_time: period_data = period_data[(period_data[date_col] >= start_of_week) & (period_data[date_col] <= today_end)]

    grp_o = len(tbl.drop_duplicates(subset=[id_c]))
    tbl_delivered_unique = tbl[tbl[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)].drop_duplicates(subset=[id_c])
    grp_m = pd.to_numeric(tbl_delivered_unique[p_col], errors='coerce').fillna(0).sum()

    delivered_unique_period = period_data[period_data[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)].drop_duplicates(subset=[id_c])
    pending_unique_period = period_data[~period_data[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)].drop_duplicates(subset=[id_c])
    received_sales = pd.to_numeric(delivered_unique_period[p_col], errors='coerce').fillna(0).sum()
    pending_sales = pd.to_numeric(pending_unique_period[p_col], errors='coerce').fillna(0).sum()

    clean_time_display = clean_emojis_for_chart(selected_time)

    # 1️⃣ التقرير الأول: كشف التدفق النقدي الفوري
    st.markdown(f"<div style='background:#e67e22; padding:10px; color:white; text-align:right; font-family:tahoma; border-radius:6px; font-weight:bold;'>📋 كشف الأداء: {selected_status} ({clean_time_display}) | العدد: {grp_o} طلبيات | القيمة: {grp_m:,} LYD 💰</div>", unsafe_allow_html=True)
    
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.markdown(f"<div style='background:#2ecc71; padding:15px; color:white; border-radius:6px; text-align:right; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-top:8px;'><b>💵 أرباح مستلمة فعلياً بالخزينة:<br><span style='font-size:20px;'>{received_sales:,} LYD</span></b></div>", unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"<div style='background:#e67e22; padding:15px; color:white; border-radius:6px; text-align:right; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-top:8px;'><b>⏳ أرباح معلقة في التوصيل:<br><span style='font-size:20px;'>{pending_sales:,} LYD</span></b></div>", unsafe_allow_html=True)

    # 2️⃣ التقرير الثاني: جدول الأستاذ المالي التفصيلي
    st.markdown("<br><div style='background:#5c2575; padding:6px; color:white; text-align:center; font-family:tahoma; border-radius:4px;'><b>💎 لوحة التقارير المالية التفصيلية لطلبيات الحزمة</b></div>", unsafe_allow_html=True)
    
    table_rows = ""
    grand_total_rev = 0
    target_orders = tbl.drop_duplicates(subset=[id_c])

    for idx, row in target_orders.iterrows():
        order_code = str(row[id_c]).strip()
        customer_name = str(row[name_col]).strip() if name_col else "—"
        order_price = pd.to_numeric(row[p_col], errors='coerce') or 0
        grand_total_rev += order_price

        row_books = []
        for col_b in clean_all.columns:
            if "Book type" in col_b or "نوع الكتاب" in col_b:
                b_val = str(row[col_b]).strip()
                if b_val not in ["0", "0.0", "0.00", "", "—", "nan", "NaN"]:
                    m_head = re.search(r'\[(.*?)\]', col_b)
                    b_title = m_head.group(1).strip() if m_head else col_b
                    row_books.append(f"{b_title} ({int(float(b_val))})")

        books_summary_str = " + ".join(row_books) if row_books else "مبيعات متنوعة"
        table_rows += f"""
        <tr>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:right;'><span style='background:#eaf2f8; color:#2471a3; padding:4px 8px; border-radius:4px; font-weight:bold;'>{order_code}</span></td>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:right; font-weight:bold;'>{customer_name}</td>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:right; color:#5c2575; font-weight:bold;'>{books_summary_str}</td>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:center;'><span style='background:#e8f8f5; color:#117a65; padding:4px 8px; border-radius:4px; font-weight:bold;'>{order_price:,.0f} LYD</span></td>
        </tr>
        """
    
    if grand_total_rev > 0:
        table_rows
