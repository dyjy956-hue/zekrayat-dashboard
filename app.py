 # -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import re

# إعدادات الصفحة
st.set_page_config(page_title="لوحة تحكم متجر ذكريات", layout="wide")

# دالة تطهير الإيموجي للرسم
def clean_emojis_for_chart(text_str):
    return re.sub(r'[^\w\s\(\)\-\/:]', '', str(text_str)).strip()

def get_icon(col_name):
    c = str(col_name).lower()
    if 'كود' in c or 'code' in c: return '🆔'
    if 'اسم' in c or 'name' in c or 'زبون' in c: return '👤'
    if 'سعر' in c or 'إجمالي' in c or 'price' in c: return '💰'
    if 'حالة' in c or 'status' in c: return '🚦'
    return '📚'

# --- جلب البيانات السحابية ---
base_url = "https://docs.google.com/spreadsheets/d/1i7lTyW3PIcryPWgdpS8hr_43ZJ1aEYHrW0PFl8oxM5Q/export?format=xlsx"

@st.cache_data(ttl=300)
def fetch_data(url):
    try:
        cache_url = f"{url}&cache_bust={int(time.time())}"
        df = pd.read_excel(cache_url, sheet_name=0)
        return df, True
    except Exception as e:
        st.warning(f"⚠️ تعذر الاتصال بالسحابة: {e}.")
        return pd.DataFrame(), False

df, success = fetch_data(base_url)

# إعداد البيانات
if success and not df.empty:
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
    id_c = [c for c in df.columns if "كود" in c or "Code" in c][0]
    st_c = [c for c in df.columns if "حالة" in c or "Status" in c][0]
    p_col = [c for c in df.columns if "السعر" in c or "Price" in c][0]
    name_col = [c for c in df.columns if "اسم" in c or "Name" in c][0]
    
    clean_all = df.copy()
    clean_ids = sorted(df[id_c].dropna().astype(str).unique())
    clean_statuses = sorted(df[st_c].dropna().astype(str).unique())
else:
    st.error("البيانات غير متاحة حالياً.")
    st.stop()

# الواجهة
st.markdown("<h2 style='text-align:center;'>📊 لوحة التحكم التنفيذية - متجر ذكريات</h2>", unsafe_allow_html=True)
mode = st.sidebar.radio("وضع العرض:", ['تفاصيل طلبية', 'عرض التقارير'])

if 'تفاصيل' in mode:
    selected_id = st.sidebar.selectbox("اختر كود الطلب:", clean_ids)
    row = df[df[id_c] == selected_id].iloc[0]
    for col in df.columns:
        st.info(f"**{col}**: {row[col]}")
else:
    # التقارير
    st.write("### 📈 التحليلات")
    status_counts = df[st_c].value_counts()
    fig, ax = plt.subplots()
    ax.bar(status_counts.index, status_counts.values)
    st.pyplot(fig)
