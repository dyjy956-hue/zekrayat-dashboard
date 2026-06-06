 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة الافتراضية لواجهة الويب الفاخرة
st.set_page_config(
    page_title="Zekrayat Dashboard",
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
    if 'عنوان' in c or 'مكان' in c or 'مدينة' in c or 'address' in c or 'city' in c: return '📍'
    return '📚'

# --- جلب البيانات السحابية حياً من قوقل شيت ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    live_url = f"{base_url}&cache_bust={int(time.time())}"
    df = pd.read_excel(live_url, sheet_name=0)
    
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_cols = [c for c in df.columns if "حالة" in c or "Status" in c]
    st_c = st_cols[0] if st_cols else "الحالة"
    
    # البحث الذكي عن عمود المدينة أو العنوان
    city_cols = [c for c in df.columns if any(k in str(c).lower() for k in ["مدينة", "عنوان", "city", "address", "منطقة"])]
    city_c = city_cols[0] if city_cols else None
    
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد / Unspecified").astype(str).str.strip()
    
    if city_c:
        df[city_c] = df[city_c].fillna("غير محدد / Unspecified").astype(str).str.strip()
        clean_cities = sorted([str(x).strip() for x in df[city_c].unique() if str(x).strip() != ''])
    else:
        clean_cities = ['كل المدن / All Cities']

    clean_all_temp = df[df[id_c].str.startswith('D-', na=False)]
    clean_ids = sorted([str(x).strip() for x in clean_all_temp[id_c].unique() if str(x).strip() != ''])
    clean_statuses = sorted([str(x).strip() for x in df[st_c].unique() if str(x).strip() != ''])
except:
    clean_ids = ['D-ORD-1', 'D-ORD-2']
    clean_statuses = ['تسليم', 'قيد الشحن']
    clean_cities = ['طرابلس', 'بنغازي', 'مصراتة']
    city_c = "المدينة"
    df = pd.DataFrame()

# تصفية وتجهيز الأعمدة
if not df.empty:
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
    df = df.dropna(how='all', axis=1)
    
    p_cols = [c for c in df.columns if "السعر" in c or "الإجمالي" in c or "Price" in c or "Total" in c]
    p_col = p_cols[0] if p_cols else "السعر الصافي"
    if p_col not in df.columns: df[p_col] = 0
    
    name_cols = [c for c in df.columns if "اسم" in c or "الزبون" in c or "العميل" in c or "Name" in c]
    name_col = name_cols[0] if name_cols else df.columns[1]
    
    clean_all = df[df[id_c].fillna('').astype(str).str.strip().str.startswith('D-')].copy()
    clean_all[st_c] = clean_all[st_c].fillna("غير محدد / Unspecified").astype(str).str.strip()
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
    
    if city_c:
        clean_all[city_c] = clean_all[city_c].fillna("غير محدد / Unspecified").astype(str).str.strip()

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
        }
        div[data-testid="stBlock"] { direction: rtl !important; text-align: right !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center; color:white; font-family:tahoma; margin-bottom:20px;'>
    <h2>📊 لوحة التحكم التنفيذية - متجر ذكريات الفاخر</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='background-color:#5c2575; padding:8px; color:white; text-align:center; font-weight:bold; border-radius:4px;'>
    ⚙️ لوحة الفرز والملاحة / Control Panel
</div>
""", unsafe_allow_html=True)

mode = st.sidebar.radio(
    "اختر وضع العرض المطلوب / Select View Mode:",
    ['📊 عرض المجموعات والتقارير / Executive Analytics', '🔍 تفاصيل طلبية واحدة / Single Order Inquiry']
)

if st.sidebar.button("🔄 تحديث حياً وجلب البيانات الفورية / Live Fetch Sync", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if 'Single' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب المستهدف / Select Order Code:", clean_ids)
    delivered_global_mask = clean_all[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم|مقبول', na=False, case=False)
    tot_o = len(clean_all.drop_duplicates(subset=[id_c]))
    unique_delivered = clean_all[delivered_global_mask].drop_duplicates(subset=[id_c])
    tot_m = unique_delivered[p_col].sum()
    
    st.markdown(f"""
    <div style='background:linear-gradient(135deg, #5c2575, #7d3c98); padding:14px; color:white; text-align:right; font-family:tahoma; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.1);'>
        <b>📊 إجمالي الطلبات الفريدة بالمنظومة: {tot_o} | 💰 مبيعات الخزينة الكلية المحققة: {tot_m:,} LYD</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background:#2c3e50; padding:10px; color:white; text-align:right; margin-top:10px; border-radius:6px; font-family:tahoma;'>
        <b>📌 تفاصيل كود الطلب الحالي: {selected_id}</b>
    </div>
    """, unsafe_allow_html=True)
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
                val_element = f"<span style='background:#e8f8f5; color:#117a65; padding:6px 14px; border-radius:20px; font-weight:bold; border:1px solid #117a65; font-size:12px;'>{v_str} 🟢</span>"
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
    selected_status = st.sidebar.selectbox("اختر حالة المجموعة بالتصفية / Filter by Status:", clean_statuses)
    
    # فلتر المدينة الجديد في القائمة الجانبية
    expanded_cities = ['كل المدن / All Cities'] + clean_cities
    selected_city = st.sidebar.selectbox("📍 اختر فرز المدينة / Filter by City:", expanded_cities)
    
    selected_time = st.sidebar.selectbox("اختر النطاق الزمني للتقرير / Select Period:", ['كل الأوقات / All Times (All)', 'طلبات اليوم فقط / Today Only (Today)', 'طلبات هذا الأسبوع / This Week Only (This Week)'])
    
    clean_status_val = str(selected_status).replace('✔', '').replace('🟢', '').replace('🟠', '').replace('🔵', '').strip()
    
    # الفلترة الأساسية بناءً على الحالة
    tbl = clean_all[clean_all[st_c].astype(str).str.contains(clean_status_val, na=False, case=False)].copy()
    
    # تفعيل فلتر المدينة إذا لم يتم اختيار "كل المدن"
    if city_c and selected_city != 'كل المدن / All Cities':
        tbl = tbl[tbl[city_c].astype(str).str.strip() == str(selected_city).strip()]
    
    today_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)).date()
    start_of_week_date = today_date - datetime.timedelta(days=7)
    
    period_data = clean_all.copy()

    if date_col and not tbl.empty:
        if 'Today' in selected_time: tbl = tbl[tbl[date_col] == today_date]
        elif 'This Week' in selected_time: tbl = tbl[(tbl[date_col] >= start_of_week_date) & (tbl[date_col] <= today_date)]
            
    if date_col and not period_data.empty:
        if 'Today' in selected_time: period_data = period_data[period_data[date_col] == today_date]
        elif 'This Week' in selected_time: period_data = period_data[(period_data[date_col] >= start_of_week_date) & (period_data[date_col] <= today_date)]

    # --- حساب الأعداد الإحصائية للأزرار الملونة ---
    unique_all_period = period_data.drop_duplicates(subset=[id_c])
    count_delivered = len(unique_all_period[unique_all_period[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم|مقبول', na=False, case=False)])
    count_shipping = len(unique_all_period[unique_all_period[st_c].str.contains('شحن|طريق|مندوب|Shipping|Shipped', na=False, case=False)])
    count_preparing = len(unique_all_period[unique_all_period[st_c].str.contains('تجهيز|تحضير|ورشة|Preparing|Process', na=False, case=False)])
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        st.markdown(f"<div style='background: linear-gradient(135deg, #2ecc71, #27ae60); padding: 20px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(46, 204, 113, 0.2);'><span style='font-size: 28px; font-weight: bold; display: block;'>{count_delivered}</span><span style='font-size: 14px; font-family: tahoma; font-weight: bold;'>📦 عدد الطلبات المستلمة / Delivered</span></div>", unsafe_allow_html=True)
    with col_btn2:
        st.markdown(f"<div style='background: linear-gradient(135deg, #e67e22, #d35400); padding: 20px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(230, 126, 34, 0.2);'><span style='font-size: 28px; font-weight: bold; display: block;'>{count_shipping}</span><span style='font-size: 14px; font-family: tahoma; font-weight: bold;'>🚚 في الشحن والتوصيل / In Shipping</span></div>", unsafe_allow_html=True)
    with col_btn3:
        st.markdown(f"<div style='background: linear-gradient(135deg, #3498db, #2980b9); padding: 20px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2);'><span style='font-size: 28px; font-weight: bold; display: block;'>{count_preparing}</span><span style='font-size: 14px; font-family: tahoma; font-weight: bold;'>🛠️ طلبات تحت التجهيز / Preparing</span></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    grp_o = len(tbl.drop_duplicates(subset=[id_c]))
    tbl_delivered_unique = tbl[tbl[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم|مقبول', na=False, case=False)].drop_duplicates(subset=[id_c])
    grp_m = tbl_delivered_unique[p_col].sum()

    delivered_unique_period = period_data[period_data[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم|مقبول', na=False, case=False)].drop_duplicates(subset=[id_c])
    pending_unique_period = period_data[~period_data[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم|مقبول', na=False, case=False)].drop_duplicates(subset=[id_c])
    received_sales = delivered_unique_period[p_col].sum()
    pending_sales = pending_unique_period[p_col].sum()

    clean_time_display = clean_emojis_for_chart(selected_time)

    st.markdown(f"""
    <div style='background:#5c2575; padding:10px; color:white; text-align:right; font-family:tahoma; border-radius:6px; font-weight:bold;'>
        📋 كشف أداء حزمة: {selected_status} | المدينة: {selected_city} ({clean_time_display}) | العدد: {grp_o} | القيمة المستلمة: {grp_m:,} LYD 💰
    </div>
    """, unsafe_allow_html=True)
    
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.markdown(f"""
        <div style='background:#2ecc71; padding:15px; color:white; border-radius:6px; text-align:right; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-top:8px;'>
            <b>💵 إجمالي السيولة المستلمة بالخزينة:<br><span style='font-size:20px;'>{received_sales:,} LYD</span></b>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div style='background:#e67e22; padding:15px; color:white; border-radius:6px; text-align:right; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-top:8px;'>
            <b>⏳ إجمالي أرباح معلقة في التوصيل:<br><span style='font-size:20px;'>{pending_sales:,} LYD</span></b>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><div style='background:#2c3e50; padding:6px; color:white; text-align:center; font-family:tahoma; border-radius:4px;'><b>💎 لوحة التقارير المالية التفصيلية لطلبيات الحزمة / Detailed Financial Statement</b></div>", unsafe_allow_html=True)
    
    table_rows = ""
    grand_total_rev = 0
    target_orders = tbl.drop_duplicates(subset=[id_c])

    for idx, row in target_orders.iterrows():
        order_code = str(row[id_c]).strip()
        customer_name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else "—"
        order_price = row[p_col]
        grand_total_rev += order_price

        row_books = []
        for col_b in clean_all.columns:
            if "Book type" in col_b or "نوع الكتاب" in col_b:
                b_val = str(row[col_b]).strip()
                if b_val not in ["0", "0.0", "0.00", "", "—", "nan", "NaN"]:
                    m_head = re.search(r'\[(.*?)\]', col_b)
                    b_title = m_head.group(1).strip() if m_head else col_b
                    row_books.append(f"{b_title} ({int(float(b_val))})")

        books_summary_str = " + ".join(row_books) if row_books else "مبيعات متنوعة / Misc Items"
        price_display = f"{order_price:,.0f} LYD" if order_price > 0 else "⚠️ 0 LYD"

        table_rows += f"""
        <tr>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:right;'><span style='background:#eaf2f8; color:#2471a3; padding:4px 8px; border-radius:4px; font-weight:bold;'>{order_code}</span></td>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:right; font-weight:bold;'>{customer_name}</td>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:right; color:#5c2575; font-weight:bold;'>{books_summary_str}</td>
            <td style='padding:10px; border-bottom:1px solid #eee; text-align:center;'><span style='background:#e8f8f5; color:#117a65; padding:4px 8px; border-radius:4px; font-weight:bold;'>{price_display}</span></td>
        </tr>
        """
    
    if not target_orders.empty:
        total_html_row = f"""
        <tr style='background-color:#ebdef0; font-weight:bold; color:#5c2575;'>
            <td colspan='3' style='padding:12px; text-align:right;'>📊 إجمالي صافي إيرادات الخزينة الكلية لهذه الحزمة</td>
            <td style='padding:12px; text-align:center;'><span style='background:#7d3c98; color:white; padding:5px 12px; border-radius:4px;'>{grand_total_rev:,.0f} LYD</span></td>
        </tr>
        """
        
        html_table = f"""
        <table style='width:100%; border-collapse:collapse; margin-top:10px; font-family:tahoma; direction:rtl; box-shadow:0 4px 12px rgba(0,0,0,0.05); border-radius:6px; overflow:hidden;'>
            <thead>
                <tr style='background-color:#5c2575; color:white;'>
                    <th style='padding:12px; text-align:right;'>🆔 كود الطلبية</th>
                    <th style='padding:12px; text-align:right;'>👤 اسم الزبون</th>
                    <th style='padding:12px; text-align:right;'>📚 مواصفات الحزمة</th>
                    <th style='padding:12px; text-align:center;'>💰 إجمالي السعر</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
                {total_html_row}
            </tbody>
        </table>
        """
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("لا توجد طلبيات مطابقة تماماً لخيارات الفرز الحالية للبلدية/المدينة المحددة.")

    st.markdown("<br><div style='background:#5c2575; padding:6px; color:white; text-align:center; font-family:tahoma; border-radius:4px;'><b>📊 الرسوم البيانية الجغرافية والمالية / Executive Visual Analytics</b></div>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # 1️⃣ رسم بياني مالي (التدفقات المالية للسيولة)
        if received_sales > 0 or pending_sales > 0:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            ax1.pie([received_sales, pending_sales], labels=['Received Cash', 'Pending Cash'], 
                    autopct=lambda p: f'{(p/100)*(received_sales+pending_sales):,.0f} LYD\n({p:.1f}%)' if p > 0 else '',
                    startangle=140, colors=['#2ecc71', '#e67e22'], textprops={'fontsize':9, 'weight':'bold'})
            ax1.set_title("Financial Cashflow Distribution (LYD)", fontsize=10, weight='bold', color='#5c2575', pad=15)
            st.pyplot(fig1)
            plt.close(fig1)
            
    with col_chart2:
        # 2️⃣ الرسم البياني الجغرافي لتوزيع الطلبات حسب المدينة
        if city_c and not period_data.empty:
            city_counts = period_data.drop_duplicates(subset=[id_c])[city_c].value_counts()
            if not city_counts.empty:
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                # تنظيف وحساب النسب المئوية للمدن لعرضها بالإنجليزية نقية في الـ Chart
                geo_labels = [clean_emojis_for_chart(x) for x in city_counts.index]
                ax2.pie(city_counts.values, labels=geo_labels, 
                        autopct='%1.1f%%', startangle=90, 
                        colors=['#3498db', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c'],
                        textprops={'fontsize':9, 'weight':'bold'})
                ax2.set_title("Geographic Orders Distribution (By City)", fontsize=10, weight='bold', color='#5c2575', pad=15)
                st.pyplot(fig2)
                plt.close(fig2)

    # --- 📊 4️⃣ لوحة صدارة الكتب الأكثر طلباً ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='background:#117a65; padding:6px; color:white; text-align:center; font-family:tahoma; border-radius:4px;'><b>📈 لوحة صدارة الكتب الأكثر طلباً (حسب الوحدات المباعة والمستلمة فقط) / Most Requested Books Leaderboard</b></div>", unsafe_allow_html=True)
    
    book_columns = [c for c in clean_all.columns if "book type" in c.lower() or "نوع الكتاب" in c or "كتاب" in c]
    
    if book_columns and not period_data.empty:
        mask_delivered_strict = period_data[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم|مقبول', na=False, case=False)
        strict_delivered_orders = period_data[mask_delivered_strict].drop_duplicates(subset=[id_c])
        
        book_data_list = []
        kw = ["عرس", "زواج", "wedding", "سفر", "سياحة", "travel", "مخمل", "velvet", "جلد", "leather", "كبير", "large", "وسط", "medium", "صغير", "small"]
        en = ["Wedding Album", "Wedding Album", "Wedding Album", "Travel Album", "Travel Album", "Travel Album", "Velvet Album", "Velvet Album", "Leather Album", "Leather Album", "Large Book", "Large Book", "Medium Book", "Medium Book", "Small Book", "Small Book"]
        
        for col_b in book_columns:
            m_head = re.search(r'\[(.*?)\]', col_b)
            arabic_book_name = m_head.group(1).strip() if m_head else col_b.replace('Book type', '').strip()
            
            name_lower = arabic_book_name.lower()
            english_chart_label = "Custom Album"
            
            for k_word, e_label in zip(kw, en):
                if k_word in name_lower:
                    english_chart_label = e_label
                    break
            
            total_qty = pd.to_numeric(strict_delivered_orders[col_b], errors='coerce').fillna(0).sum()
            
            if total_qty > 0:
                book_data_list.append({
                    'Arabic Name': arabic_book_name,
                    'Chart Label': english_chart_label,
                    'Quantity': int(total_qty)
                })
        
        if book_data_list:
            df_books = pd.DataFrame(book_data_list).sort_values(by='Quantity', ascending=False)
            col_chart_b, col_table_b = st.columns([3, 2])
            
            with col_chart_b:
                fig3, ax3 = plt.subplots(figsize=(7, 4.5))
                chart_labels = df_books['Chart Label'].tolist()
                chart_values = df_books['Quantity'].tolist()
                
                bars3 = ax3.bar(chart_labels, chart_values, color='#117a65', width=0.4, zorder=3)
                ax3.set_title("Delivered Book Volumes (Highest Demand Leaderboard)", fontsize=10, weight='bold', color='#117a65', pad=15)
                ax3.set_ylabel("Units Delivered (Pcs)", fontsize=9, weight='bold')
                ax3.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
                
                ax3.set_xticks(range(len(chart_labels)))
                ax3.set_xticklabels(chart_labels, rotation=15, ha='right', fontsize=8, weight='bold')
                
                for bar in bars3:
                    yval = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, f'{int(yval)} Pcs', ha='center', va='bottom', weight='bold', color='#2c3e50', fontsize=8)
                st.pyplot(fig3)
                plt.close(fig3)
                
            with col_table_b:
                sub_table_rows = ""
                for idx_b, r_b in df_books.iterrows():
                    sub_table_rows += f"""
                    <tr>
                        <td style='padding:12px; border-bottom:1px solid #eee; text-align:right; font-weight:bold; color:#117a65;'>{r_b['Arabic Name']}</td>
                        <td style='padding:12px; border-bottom:1px solid #eee; text-align:center; font-weight:bold; color:#2c3e50;'>{r_b['Quantity']} قطعة</td>
                    </tr>
                    """
                
                html_book_table = f"""
                <table style='width:100%; border-collapse:collapse; margin-top:25px; font-family:tahoma; direction:rtl; box-shadow:0 4px 12px rgba(0,0,0,0.05); border-radius:6px; overflow:hidden;'>
                    <thead>
                        <tr style='background-color:#117a65; color:white;'>
                            <th style='padding:12px; text-align:right;'>📚 نوع المنتج الأكثر طلباً</th>
                            <th style='padding:12px; text-align:center;'>🔢 إجمالي كمية المبيعات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sub_table_rows}
                    </tbody>
                </table>
                """
                st.markdown(html_book_table, unsafe_allow_html=True)
        else:
            st.warning("لا توجد كميات كتب مباعة ومستلمة لعرض صدارتها حالياً في النطاق الجغرافي المحدد.")
    else:
        st.markdown("أعمدة مبيعات الكتب غير متوفرة في شيت قوقل حالياً.")
