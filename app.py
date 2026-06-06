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
    
    id_c = [c for c in df.columns if any(k in c for k in ["كود", "Code"])][0] if [c for c in df.columns if any(k in c for k in ["كود", "Code"])] else df.columns[0]
    st_c = [c for c in df.columns if any(k in c for k in ["حالة", "Status"])][0] if [c for c in df.columns if any(k in c for k in ["حالة", "Status"])] else df.columns[4]
    p_col = [c for c in df.columns if any(k in c for k in ["سعر", "إجمالي", "Price", "Total"])][0] if [c for c in df.columns if any(k in c for k in ["سعر", "إجمالي", "Price", "Total"])] else df.columns[-1]
    name_col = [c for c in df.columns if any(k in c for k in ["اسم", "زبون", "عميل", "Name"])][0] if [c for c in df.columns if any(k in c for k in ["اسم", "زبون", "عميل", "Name"])] else df.columns[1]
    
    df[id_c] = df[id_c].fillna('').astype(str).str.strip()
    df[st_c] = df[st_c].fillna("غير محدد").astype(str).str.strip()
    
    clean_all = df[df[id_c] != ''].copy()
    clean_all[p_col] = pd.to_numeric(clean_all[p_col], errors='coerce').fillna(0)
    
    clean_ids = sorted([str(x).strip() for x in clean_all[id_c].unique() if str(x).strip() != ''])
    clean_statuses = sorted([str(x).strip() for x in clean_all[st_c].unique() if str(x).strip() != ''])
except:
    clean_ids, clean_statuses, df, clean_all = ['1'], ['تسليم'], pd.DataFrame(), pd.DataFrame()

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
    st.error("⚠️ لم يتم العثور على بيانات حية. تأكد من صلاحيات الشيت.")
else:
    if 'Single' in mode:
        selected_id = st.sidebar.selectbox("اختر كود الطلب المستهدف:", clean_ids)
        # إصلاح وتأمين جلب تفاصيل السطر بالكامل وعرضه بشكل فاخر ومباشر
        matching_data = clean_all[clean_all[id_c] == selected_id]
        if not matching_data.empty:
            row = matching_data.iloc[0]
            st.markdown(f"<div style='background:#5c2575; padding:10px; color:white; border-radius:6px; margin-bottom:15px;'><b>📌 كشف التفاصيل الكاملة لكود الطلب: {selected_id}</b></div>", unsafe_allow_html=True)
            
            for col in df.columns:
                if "Unnamed" in str(col) or col in ['parsed_date_only', 'parsed_dt']: continue
                val = str(row[col]).strip() if pd.notna(row[col]) else "—"
                
                # إخفاء الخانات الصفرية للكتب لتبدو الفاتورة نظيفة ومريحة
                if any(k in col.lower() for k in ["book", "كتاب", "ألبوم"]) and val in ["0", "0.0", "0.00"]: continue
                
                st.markdown(f"""
                <div style='direction:ltr; text-align:left; padding:12px 16px; margin-bottom:6px; background:#fff; border-left:5px solid #5c2575; border-radius:4px; box-shadow:0 1px 3px rgba(0,0,0,0.05);'>
                    <span style='color:#7f8c8d; font-weight:bold;'>{col}:</span> 
                    <span style='color:#2c3e50; font-weight:bold; margin-left:10px;'>{val}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("لم يتم العثور على تفاصيل لهذا الكود.")
    else:
        selected_status = st.sidebar.selectbox("اختر الحالة للفرز:", clean_statuses)
        selected_time = st.sidebar.selectbox("اختر النطاق الزمني:", ['كل الأوقات', 'طلبات اليوم فقط', 'طلبات هذا الأسبوع'])
        
        tbl = clean_all[clean_all[st_c] == selected_status].copy()
        today_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)).date()
        
        if date_col and not tbl.empty:
            if 'اليوم' in selected_time: tbl = tbl[tbl[date_col] == today_date]
            elif 'الأسبوع' in selected_time: tbl = tbl[tbl[date_col] >= (today_date - datetime.timedelta(days=7))]
            
        period_data = clean_all.copy()
        if date_col:
            if 'اليوم' in selected_time: period_data = period_data[period_data[date_col] == today_date]
            elif 'الأسبوع' in selected_time: period_data = period_data[period_data[date_col] >= (today_date - datetime.timedelta(days=7))]

        u_period = period_data.drop_duplicates(subset=[id_c])
        c_del = len(u_period[u_period[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)])
        c_shp = len(u_period[u_period[st_c].str.contains('شحن|طريق|مندوب|Shipping', na=False, case=False)])
        c_prp = len(u_period[u_period[st_c].str.contains('تجهيز|تحضير|ورشة|Preparing', na=False, case=False)])
        
        cb1, cb2, cb3 = st.columns(3)
        cb1.markdown(f"<div style='background:linear-gradient(135deg, #2ecc71, #27ae60); padding:15px; border-radius:8px; text-align:center; color:white;'><h3>{c_del}</h3><b>📦 المستلمة / Delivered</b></div>", unsafe_allow_html=True)
        cb2.markdown(f"<div style='background:linear-gradient(135deg, #e67e22, #d35400); padding:15px; border-radius:8px; text-align:center; color:white;'><h3>{c_shp}</h3><b>🚚 في الشحن / Shipping</b></div>", unsafe_allow_html=True)
        cb3.markdown(f"<div style='background:linear-gradient(135deg, #3498db, #2980b9); padding:15px; border-radius:8px; text-align:center; color:white;'><h3>{c_prp}</h3><b>🛠️ قيد التجهيز / Preparing</b></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        r_sales = u_period[u_period[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)][p_col].sum()
        p_sales = u_period[~u_period[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)][p_col].sum()
        
        st.markdown(f"<div style='background:#5c2575; padding:10px; color:white; text-align:right; font-weight:bold; border-radius:4px;'>📊 تقرير الحزمة الحالية: {selected_status} | العدد: {len(tbl.drop_duplicates(subset=[id_c]))}</div>", unsafe_allow_html=True)
        ck1, ck2 = st.columns(2)
        ck1.markdown(f"<div style='background:#2ecc71; padding:12px; color:white; text-align:right;'><b>💵 كاش مستلم فعلياً بالخزينة:<br><span style='font-size:18px;'>{r_sales:,} LYD</span></b></div>", unsafe_allow_html=True)
        ck2.markdown(f"<div style='background:#e67e22; padding:12px; color:white; text-align:right;'><b>⏳ مبالغ معلقة قيد التوصيل:<br><span style='font-size:18px;'>{p_sales:,} LYD</span></b></div>", unsafe_allow_html=True)

        st.markdown("<br><b>💎 كشف الحساب التفصيلي للطلبيات الحالية:</b>", unsafe_allow_html=True)
        t_rows = ""
        for idx, row in tbl.drop_duplicates(subset=[id_c]).iterrows():
            b_summary = " + ".join([re.search(r'\[(.*?)\]', col).group(1) if re.search(r'\[(.*?)\]', col) else col for col in clean_all.columns if any(k in col for k in ["Book", "كتاب", "ألبوم"]) if str(row[col]).strip() not in ["0", "0.0", "", "—", "nan", "NaN"]])
            b_summary = b_summary if b_summary else "مبيعات متنوعة"
            t_rows += f"<tr><td style='padding:8px; border-bottom:1px solid #eee;'>{row[id_c]}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{row[name_col]}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{b_summary}</td><td style='padding:8px; border-bottom:1px solid #eee; text-align:center;'>{row[p_col]:,.0f} LYD</td></tr>"
        
        if t_rows:
            st.markdown(f"<table style='width:100%; border-collapse:collapse; direction:rtl;'><thead><tr style='background:#5c2575; color:white;'><th style='padding:10px; text-align:right;'>🆔  الكود</th><th style='padding:10px; text-align:right;'>👤 الاسم</th><th style='padding:10px; text-align:right;'>📚 تفاصيل المنتجات</th><th style='padding:10px; text-align:center;'>💰 السعر</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='padding:10px; background:#fff; border:1px solid #eee;'>لا توجد طلبيات مسجلة في هذه الحالة حالياً.</div>", unsafe_allow_html=True)

        st.markdown("<br><b>📊 التحليلات البيانية المتقدمة / Financial Analytics:</b>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            if r_sales > 0 or p_sales > 0:
                fig1, ax1 = plt.subplots(figsize=(5, 3.5))
                ax1.pie([r_sales, p_sales], labels=['Received', 'Pending'], autopct='%1.1f%%', startangle=140, colors=['#2ecc71', '#e67e22'])
                ax1.set_title("Cashflow Split (LYD)", fontsize=9, weight='bold')
                st.pyplot(fig1)
        with cc2:
            raw_counts = u_period[st_c].replace('', 'Other')
            status_counts = raw_counts.apply(clean_emojis_for_chart).value_counts()
            if not status_counts.empty:
                fig2, ax2 = plt.subplots(figsize=(5, 3.5))
                eng_lbls = ['Delivered' if 'تسليم' in x or 'تم' in x else 'Shipping' if 'شحن' in x else 'Preparing' if 'تجهيز' in x else 'Other' for x in status_counts.index]
                ax2.bar(eng_lbls, status_counts.values, color=['#2ecc71' if x=='Delivered' else '#e67e22' for x in eng_lbls], width=0.3)
                ax2.set_title("Operational Workspace Load", fontsize=9, weight='bold')
                ax2.grid(axis='y', linestyle='--', alpha=0.5)
                st.pyplot(fig2)

        st.markdown("<br><div style='background:#117a65; padding:6px; color:white; text-align:center; border-radius:4px;'><b>📈 لوحة صدارة مبيعات الكتب وعوائدها (المستلمة فقط) / Delivered Books Leaderboard</b></div>", unsafe_allow_html=True)
        b_cols = [c for c in clean_all.columns if any(k in c.lower() for k in ["book", "كتاب", "ألبوم"])]
        
        if b_cols:
            del_orders = u_period[u_period[st_c].str.contains('تسليم|تم|Done|Delivered|مستلم', na=False, case=False)]
            b_list = []
            for col_b in b_cols:
                m_head = re.search(r'\[(.*?)\]', col_b)
                ar_name = m_head.group(1).strip() if m_head else col_b.replace('Book type', '').strip()
                
                lbl = "Custom Item"
                if "كبير" in ar_name: lbl = "Large Album"
                elif "وسط" in ar_name: lbl = "Medium Album"
                elif "صغير" in ar_name: lbl = "Small Album"
                elif "مخمل" in ar_name: lbl = "Velvet Album"
                elif "جلد" in ar_name: lbl = "Leather Album"
                
                t_qty = pd.to_numeric(del_orders[col_b], errors='coerce').fillna(0).sum()
                t_rev = del_orders[pd.to_numeric(del_orders[col_b], errors='coerce').fillna(0) > 0][p_col].sum()
                if t_qty > 0: b_list.append({'Arabic': ar_name, 'Label': lbl, 'Qty': int(t_qty), 'Rev': t_rev})
                
            if b_list:
                df_b = pd.DataFrame(b_list).sort_values(by='Qty', ascending=False)
                ch_b, tb_b = st.columns([3, 2])
                with ch_b:
                    fig3, ax3 = plt.subplots(figsize=(7, 4))
                    ax3.bar(df_b['Label'], df_b['Qty'], color='#117a65', width=0.3)
                    ax3.set_title("Delivered Volumes (Descending Order)", fontsize=9, weight='bold')
                    plt.xticks(rotation=10, fontsize=8)
                    st.pyplot(fig3)
                with tb_b:
                    sub_rows = "".join([f"<tr><td style='padding:6px; border-bottom:1px solid #eee;'>{r['Arabic']}</td><td style='padding:6px; border-bottom:1px solid #eee; text-align:center;'>{r['Qty']} قطعة</td><td style='padding:6px; border-bottom:1px solid #eee; text-align:center; color:#117a65;'>{r['Rev']:,.0f} LYD</td></tr>" for i, r in df_b.iterrows()])
                    st.markdown(f"<table style='width:100%; border-collapse:collapse; direction:rtl; font-size:12px; margin-top:20px;'><thead><tr style='background:#117a65; color:white;'><th style='padding:8px; text-align:right;'>📚 نوع المنتج</th><th style='padding:8px; text-align:center;'>🔢 الكمية</th><th style='padding:8px; text-align:center;'>💰 الصافي</th></tr></thead><tbody>{sub_rows}</tbody></table>", unsafe_allow_html=True)
