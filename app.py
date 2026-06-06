 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re
import arabic_reshaper
from bidi.algorithm import get_display

# 1. إعدادات الصفحة
st.set_page_config(page_title="Zekrayat Dashboard", layout="wide")

# 2. دوال المعالجة (التعريب والتنظيف)
def get_arabic(text):
    return get_display(arabic_reshaper.reshape(str(text)))

def clean_emojis(text):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text)).strip()

# 3. جلب البيانات
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
    st.error("خطأ في جلب البيانات من قوقل شيت")
    st.stop()

# 4. الواجهة والفرز
st.title("📊 لوحة تحكم متجر ذكريات")

if st.sidebar.button("🔄 تحديث البيانات"):
    st.cache_data.clear()
    st.rerun()

selected_status = st.sidebar.selectbox("فلترة الحالة:", ['الكل'] + sorted(df[st_c].unique().tolist()))
selected_city = st.sidebar.selectbox("فلترة المدينة:", ['الكل'] + sorted(df[city_c].unique().tolist()))

# تطبيق الفلترة
tbl = df.copy()
if selected_status != 'الكل': tbl = tbl[tbl[st_c] == selected_status]
if selected_city != 'الكل': tbl = tbl[tbl[city_c] == selected_city]

# 5. الإحصائيات (Metrics)
c1, c2, c3 = st.columns(3)
c1.metric("الطلبات", len(tbl))
c2.metric("الإيرادات", f"{tbl[p_col].sum():,.0f} LYD")
c3.metric("المدن المغطاة", len(tbl[city_c].unique()))

# 6. توزيع المدن (Pie Chart) مع دعم العربية
st.subheader("📍 التوزيع الجغرافي")
city_counts = tbl[city_c].value_counts()
fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
ax_pie.pie(city_counts.values, labels=[get_arabic(x) for x in city_counts.index], autopct='%1.1f%%', startangle=140)
ax_pie.set_title(get_arabic("توزيع الطلبات حسب المدينة"), fontsize=12)
st.pyplot(fig_pie)

# 7. صدارة الكتب (لطلبيات التسليم فقط)
st.subheader("📈 صدارة الكتب الأكثر طلباً (طلبات التسليم)")
delivered = tbl[tbl[st_c].str.contains('تسليم|تم|مستلم', na=False, case=False)]

if not delivered.empty:
    book_cols = [c for c in df.columns if "Book type" in c or "كتاب" in c]
    data = []
    for col in book_cols:
        qty = pd.to_numeric(delivered[col], errors='coerce').fillna(0).sum()
        if qty > 0:
            name = re.search(r'\[(.*?)\]', col).group(1) if "[" in col else col
            data.append({"Book": name, "Qty": int(qty)})
    
    if data:
        df_b = pd.DataFrame(data).sort_values("Qty", ascending=False)
        fig_b, ax_b = plt.subplots(figsize=(8, 4))
        ax_b.bar([get_arabic(x) for x in df_b["Book"]], df_b["Qty"], color='#117a65')
        ax_b.set_title(get_arabic("الكتب الأكثر طلباً"), fontsize=12)
        plt.xticks(rotation=15)
        st.pyplot(fig_b)
    else:
        st.info("لا توجد مبيعات كتب في طلبات التسليم.")
else:
    st.warning("لا توجد طلبيات تسليم لعرض صدارة الكتب.")

# 8. الجدول
st.subheader("📋 التفاصيل")
st.table(tbl)
