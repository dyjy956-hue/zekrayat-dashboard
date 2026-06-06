 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة
st.set_page_config(page_title="Zekrayat Dashboard", layout="wide")

def get_icon(col_name):
    c = str(col_name).lower()
    if 'كود' in c: return '🆔'
    if 'اسم' in c: return '👤'
    if 'سعر' in c or 'إجمالي' in c: return '💰'
    if 'حالة' in c: return '🚦'
    if 'مدينة' in c or 'عنوان' in c: return '📍'
    return '📚'

# --- جلب البيانات ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", engine='openpyxl')
    id_c = [c for c in df.columns if "كود" in c][0]
    st_c = [c for c in df.columns if "حالة" in c][0]
    p_col = [c for c in df.columns if "سعر" in c or "إجمالي" in c][0]
    city_c = [c for c in df.columns if any(k in str(c) for k in ["مدينة", "عنوان"])][0]
    
    df[id_c] = df[id_c].astype(str).str.strip()
    df[st_c] = df[st_c].fillna("Unspecified").astype(str)
    df[city_c] = df[city_c].fillna("Unspecified").astype(str)
    df[p_col] = pd.to_numeric(df[p_col], errors='coerce').fillna(0)
except:
    st.error("خطأ في قراءة البيانات من الشيت")
    st.stop()

# --- الواجهة ---
st.title("📊 لوحة تحكم متجر ذكريات")

if st.sidebar.button("🔄 تحديث البيانات"):
    st.cache_data.clear()
    st.rerun()

status_list = ['الكل'] + sorted(df[st_c].unique().tolist())
selected_status = st.sidebar.selectbox("فلترة الحالة:", status_list)

tbl = df.copy()
if selected_status != 'الكل':
    tbl = tbl[tbl[st_c] == selected_status]

# إحصائيات علوية
c1, c2, c3 = st.columns(3)
c1.metric("إجمالي الطلبات", len(tbl))
c2.metric("الإيرادات", f"{tbl[p_col].sum():,.0f} LYD")
c3.metric("المدن المغطاة", len(tbl[city_c].unique()))

# رسم بياني للمدن
st.subheader("📍 التوزيع الجغرافي")
city_counts = tbl[city_c].value_counts()
fig, ax = plt.subplots()
ax.pie(city_counts.values, labels=city_counts.index, autopct='%1.1f%%')
st.pyplot(fig)

# صدارة الكتب (لطلبيات التسليم فقط)
st.subheader("📈 صدارة الكتب (طلبات التسليم)")
delivered = tbl[tbl[st_c].str.contains('تسليم|تم|مستلم', na=False, case=False)]

if not delivered.empty:
    book_cols = [c for c in df.columns if "Book type" in c or "كتاب" in c]
    data = []
    for col in book_cols:
        qty = pd.to_numeric(delivered[col], errors='coerce').fillna(0).sum()
        if qty > 0:
            data.append({"Book": col, "Qty": int(qty)})
    
    if data:
        df_b = pd.DataFrame(data)
        st.bar_chart(df_b.set_index("Book"))
    else:
        st.info("لا توجد مبيعات كتب في التسليم.")
else:
    st.warning("لا توجد طلبيات تسليم.")

# الجدول
st.table(tbl)
