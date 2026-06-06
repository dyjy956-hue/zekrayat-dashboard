 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# 1. إعدادات الصفحة
st.set_page_config(page_title="Zekrayat Dashboard", layout="wide")

# 2. الدوال المساعدة
def clean_emojis(text):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text)).strip()

# 3. جلب البيانات
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"
try:
    df = pd.read_excel(f"{base_url}&cache_bust={int(time.time())}", engine='openpyxl')
    # تحديد الأعمدة الأساسية
    id_c = [c for c in df.columns if "كود" in c][0]
    st_c = [c for c in df.columns if "حالة" in c][0]
    p_col = [c for c in df.columns if "سعر" in c or "إجمالي" in c][0]
    city_c = [c for c in df.columns if any(k in str(c) for k in ["مدينة", "عنوان"])][0]
    
    df[id_c] = df[id_c].astype(str).str.strip()
    df[st_c] = df[st_c].fillna("Unspecified").astype(str)
    df[city_c] = df[city_c].fillna("Unspecified").astype(str)
    df[p_col] = pd.to_numeric(df[p_col], errors='coerce').fillna(0)
except:
    st.error("خطأ في قراءة البيانات من قوقل شيت")
    st.stop()

# 4. الواجهة والفرز
st.title("📊 لوحة تحكم متجر ذكريات")
selected_status = st.sidebar.selectbox("فلترة الحالة:", ['الكل'] + sorted(df[st_c].unique().tolist()))
selected_city = st.sidebar.selectbox("فلترة المدينة:", ['الكل'] + sorted(df[city_c].unique().tolist()))

tbl = df.copy()
if selected_status != 'الكل': tbl = tbl[tbl[st_c] == selected_status]
if selected_city != 'الكل': tbl = tbl[tbl[city_c] == selected_city]

# 5. الإحصائيات (Metrics)
c1, c2, c3 = st.columns(3)
c1.metric("الطلبات", len(tbl))
c2.metric("الإيرادات", f"{tbl[p_col].sum():,.0f} LYD")
c3.metric("المدن", len(tbl[city_c].unique()))

# 6. الرسم البياني (Pie Chart - المدن)
st.subheader("📍 التوزيع الجغرافي حسب المدينة")
city_counts = tbl[city_c].value_counts()
fig, ax = plt.subplots(figsize=(6, 4))
ax.pie(city_counts.values, labels=city_counts.index, autopct='%1.1f%%', startangle=140)
st.pyplot(fig)

# 7. صدارة الكتب
st.subheader("📈 صدارة الكتب (طلبات التسليم)")
delivered = tbl[tbl[st_c].str.contains('تسليم|تم|مستلم', na=False, case=False)]
if not delivered.empty:
    book_cols = [c for c in df.columns if "Book type" in c or "كتاب" in c]
    data = [{"Book": c, "Qty": pd.to_numeric(delivered[c], errors='coerce').fillna(0).sum()} for c in book_cols]
    df_b = pd.DataFrame(data).query("Qty > 0").sort_values("Qty", ascending=False)
    if not df_b.empty:
        st.bar_chart(df_b.set_index("Book"))
    else:
        st.info("لا توجد مبيعات كتب في طلبات التسليم.")
else:
    st.warning("لا توجد طلبات تسليم لعرض صدارة الكتب.")

# 8. الجدول
st.table(tbl)
