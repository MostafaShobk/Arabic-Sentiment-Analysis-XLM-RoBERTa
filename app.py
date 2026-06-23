import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import shutil

##############
import pandas as pd
import numpy as np
from sentiment_analyzer import Sentiment_Analyzer
from utils.data_pipeline import Data_Pipeline
################

# إعداد الصفحة
st.set_page_config(
    page_title="نظام التحليل",
    page_icon="📊",
    layout="centered"
)

# CSS


st.markdown("""
<style>


    /* ✅ الأساسيات - اتجاه عربي كامل */
html, body, [class*="css"] {
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: embed;
}

.stApp {
    background: linear-gradient(180deg, #f5f3ff 0%, #ede9fe 40%, #f8f9fa 100%);
}

/* ✅ عناصر Streamlit - من اليمين */
.stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
.stText, .stDataFrame, .stDataFrame th, .stDataFrame td,
.stTextInput input, .stSelectbox select, .stTextArea textarea,
.streamlit-expanderHeader, .stTooltip, .stHelpText,
.stRadio label, .stCheckbox label, .stDateInput label,
.stFileUploader label, .stNumberInput label {
    direction: rtl !important;
    text-align: right !important;
}

/* ✅ استثناءات - توسيط */
.btn-desc, .header-sub, .header-box, .header-box p, .header-box div,
 [data-testid="stMarkdown"] .btn-desc {
    text-align: center !important;
}

/* ✅ الأزرار - توسيط النص */
.stButton > button {
    direction: rtl !important;
    text-align: center !important;
}
    
    /* إخفاء الأشرطة */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }
    footer { display: none; }
    
    /* تقليل الهامش العلوي */
.block-container {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 25px;
    margin-top: 15px;
    position: relative;
    z-index: 1;
    
    border: 2px solid rgba(102, 126, 234, 0.3);
    
    box-shadow: 
        0 0 15px rgba(102, 126, 234, 0.2),
        0 0 35px rgba(102, 126, 234, 0.12),
        0 0 70px rgba(118, 75, 162, 0.08),
        inset 0 0 15px rgba(102, 126, 234, 0.05);
    
    animation: glowPulse 3s ease-in-out infinite alternate;
}

@keyframes glowPulse {
    0% {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 
            0 0 15px rgba(102, 126, 234, 0.2),
            0 0 35px rgba(102, 126, 234, 0.12);
    }
    50% {
        border-color: rgba(118, 75, 162, 0.5);
        box-shadow: 
            0 0 25px rgba(118, 75, 162, 0.3),
            0 0 55px rgba(102, 126, 234, 0.2);
    }
    100% {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 
            0 0 15px rgba(102, 126, 234, 0.2),
            0 0 35px rgba(102, 126, 234, 0.12);
    }
}

.block-container:hover {
    box-shadow: 
        0 25px 70px rgba(102, 126, 234, 0.1),
        0 10px 25px rgba(102, 126, 234, 0.06),
        0 3px 8px rgba(0, 0, 0, 0.03);
    transform: translateY(-2px);
}
    
    /* العنوان الرئيسي */
    h1 {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: #2c3e50;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        transform: translateX(-8px);
        
        
    }
    
    h2, h3 {
        text-align: right;
        color: #2c3e50;
    }
    .header-box .tagline {
        color: #7c3aed;
        font-size: 1rem;
        letter-spacing: 2px;
        font-weight: 600;
        margin-top: 8px;
    }
    .header-box .eng-name {
        color: #95a5a6;
        font-size: 0.9rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* جميع الأزرار بنفس الشكل */
    .stButton > button {
        width: 100%;
        border-radius: 15px;
        font-weight: 600;
        padding: 16px 24px;
        font-size: 18px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }


    
    /* زر الإلغاء بلون مختلف */
    .stButton > button[kind="secondary"] {
        background: #f8f9fa;
        color: #2c3e50;
        border: 2px solid #dee2e6;
    }
    
    /* الفواصل */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 25px 0;
    }
    
    /* الموسعات */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        font-weight: 600;
        font-size: 16px;
    }
    
    .streamlit-expanderHeader:hover {
        background: #667eea;
        color: white;
    }
    
    /* نموذج الإضافة */
    .form-box {
        background: #f8f9fa;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #dee2e6;
        margin-bottom: 20px;
    }
    
    /* رأس الصفحة */
    .header-box {
        text-align: center;
        padding: 20px 0 30px 0;
    }
    
    .header-sub {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-top: 10px;
    }
    
    /* وصف الأزرار */
    .btn-desc {
        text-align: center;
        color: #7f8c8d;
        font-size: 13px;
        margin-top: 8px;
    }
    
    /* تذييل */
    .footer-text {
        text-align: center;
        padding: 20px;
        color: #95a5a6;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# 🔗 وظائف قاعدة البيانات
def init_database():
    """تهيئة قاعدة البيانات والجداول"""
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    
    c.execute('PRAGMA foreign_keys = ON')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS dashboard_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            data_path TEXT,
            file_name TEXT,
            file_size INTEGER,
            created_date DATE DEFAULT (date('now'))
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS quick_analyses (
            quick_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            data_path TEXT,
            file_name TEXT,
            file_size INTEGER,
            created_date DATE DEFAULT (date('now'))
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_analyses_dash (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dashboard_id INTEGER NOT NULL,
            number_of_comments INTEGER DEFAULT 0,
            analysis_month TEXT NOT NULL,
            positive_percentage INTEGER CHECK (positive_percentage BETWEEN 0 AND 100),
            negative_percentage INTEGER CHECK (negative_percentage BETWEEN 0 AND 100),
            FOREIGN KEY (dashboard_id) REFERENCES dashboard_analyses(id) ON DELETE CASCADE,
            UNIQUE(dashboard_id, analysis_month)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_analyses_quick (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quick_id INTEGER NOT NULL,
            number_of_comments INTEGER DEFAULT 0,
            analysis_month TEXT NOT NULL,
            positive_percentage INTEGER CHECK (positive_percentage BETWEEN 0 AND 100),
            negative_percentage INTEGER CHECK (negative_percentage BETWEEN 0 AND 100),
            FOREIGN KEY (quick_id) REFERENCES quick_analyses(quick_id) ON DELETE CASCADE,
            UNIQUE(quick_id, analysis_month)
        )
    ''')
    
    conn.commit()
    conn.close()


def save_uploaded_file(uploaded_file, analysis_id, table_name):
    files_dir = "data_files"
    os.makedirs(files_dir, exist_ok=True)
    file_name = f"{table_name}_{analysis_id}_{uploaded_file.name}"
    file_path = os.path.join(files_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return os.path.abspath(file_path), uploaded_file.name, uploaded_file.size


def add_analysis_to_db(table_name, name, analysis_type, description, data_path, file_name=None, file_size=None):
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    c.execute(f'INSERT INTO {table_name} (name, type, description, data_path, file_name, file_size) VALUES (?, ?, ?, ?, ?, ?)',
              (name, analysis_type, description, data_path, file_name, file_size))
    analysis_id = c.lastrowid
    conn.commit()
    conn.close()
    return analysis_id


def add_analysis_to_db_dash(table_name, dashboard_id, number_of_comments, analysis_month, positive_percentage, negative_percentage):
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    c.execute(f'INSERT INTO {table_name} (dashboard_id, number_of_comments, analysis_month, positive_percentage, negative_percentage) VALUES (?, ?, ?, ?, ?)',
              (dashboard_id, number_of_comments, analysis_month, positive_percentage, negative_percentage))
    analysis_id = c.lastrowid
    conn.commit()
    conn.close()
    return analysis_id


def add_analysis_to_db_quick(table_name, quick_id, number_of_comments, analysis_month, positive_percentage, negative_percentage):
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    c.execute("SELECT quick_id FROM quick_analyses WHERE quick_id = ?", (quick_id,))
    if c.fetchone() is None:
        st.error(f"❌ quick_id {quick_id} غير موجود في quick_analyses!")
        conn.close()
        return None
    try:
        c.execute(f'INSERT INTO {table_name} (quick_id, number_of_comments, analysis_month, positive_percentage, negative_percentage) VALUES (?, ?, ?, ?, ?)',
                  (quick_id, number_of_comments, analysis_month, positive_percentage, negative_percentage))
        analysis_id = c.lastrowid
        conn.commit()
    except sqlite3.IntegrityError as e:
        st.error(f"❌ خطأ: قد يكون هناك تحليل موجود مسبقاً لنفس الشهر - {e}")
        analysis_id = None
    finally:
        conn.close()
    return analysis_id


def update_analysis_info_only(table_name, analysis_id, name, analysis_type, description):
    """✅ تعديل الاسم والنوع والوصف فقط"""
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    id_column = 'quick_id' if table_name == 'quick_analyses' else 'id'
    c.execute(f'UPDATE {table_name} SET name = ?, type = ?, description = ? WHERE {id_column} = ?',
              (name, analysis_type, description, analysis_id))
    conn.commit()
    conn.close()


def get_analyses_from_db(table_name):
    conn = sqlite3.connect('analyses.db')
    if table_name == 'quick_analyses':
        id_column = 'quick_id'
        df = pd.read_sql(f'SELECT {id_column} as id, name, type, description, data_path, file_name, file_size, date(created_date) as created_date FROM {table_name} ORDER BY created_date DESC', conn)
    else:
        df = pd.read_sql(f'SELECT id, name, type, description, data_path, file_name, file_size, date(created_date) as created_date FROM {table_name} ORDER BY created_date DESC', conn)
    conn.close()
    return df


def get_analysis_by_id(table_name, analysis_id):
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    id_column = 'quick_id' if table_name == 'quick_analyses' else 'id'
    c.execute(f'SELECT * FROM {table_name} WHERE {id_column} = ?', (analysis_id,))
    result = c.fetchone()
    conn.close()
    return result


def delete_analysis_from_db(table_name, analysis_id):
    """حذف تحليل من قاعدة البيانات مع حذف التحليلات المرتبطة"""
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    
    id_column = 'quick_id' if table_name == 'quick_analyses' else 'id'
    
    if table_name == 'dashboard_analyses':
        c.execute('DELETE FROM product_analyses_dash WHERE dashboard_id = ?', (analysis_id,))
    elif table_name == 'quick_analyses':
        c.execute('DELETE FROM product_analyses_quick WHERE quick_id = ?', (analysis_id,))
    
    c.execute(f'SELECT data_path FROM {table_name} WHERE {id_column} = ?', (analysis_id,))
    result = c.fetchone()
    if result and result[0] and os.path.exists(result[0]):
        try: os.remove(result[0])
        except: pass
    
    c.execute(f'DELETE FROM {table_name} WHERE {id_column} = ?', (analysis_id,))
    
    conn.commit()
    conn.close()


def perform_sentiment_analysis(file_path, analysis_id, analysis_type='dashboard', analysis_month=None):
    try:
        st.info("🔄 جاري تحليل المشاعر...")
        
        if file_path.endswith('.csv'): df_data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'): df_data = pd.read_excel(file_path)
        elif file_path.endswith('.json'): df_data = pd.read_json(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
            df_data = pd.DataFrame(lines, columns=['text'])
        else:
            st.error("❌ نوع الملف غير مدعوم")
            return None, None, None
        
        if 'text' in df_data.columns: texts = df_data['text'].tolist()
        elif 'Text' in df_data.columns: texts = df_data['Text'].tolist()
        elif 'comment' in df_data.columns: texts = df_data['comment'].tolist()
        elif 'Comment' in df_data.columns: texts = df_data['Comment'].tolist()
        else: texts = df_data.iloc[:, 0].tolist()
        
        texts = [str(t) for t in texts if pd.notna(t) and str(t).strip() != '']
        
        if len(texts) == 0:
            st.error("❌ لا توجد نصوص صالحة للتحليل في الملف")
            return None, None, None
        
        data_pipeline = Data_Pipeline()
        cleaned_texts = data_pipeline.clean_data(texts)
        
        sa = Sentiment_Analyzer(texts, cleaned_texts)
        total, positive_percentage, negative_percentage = sa.get_sentiments()
        
        if analysis_month is None:
            analysis_month = datetime.now().strftime('%Y-%m')
        
        if analysis_type == 'dashboard':
            add_analysis_to_db_dash('product_analyses_dash', analysis_id, total, analysis_month, positive_percentage, negative_percentage)
        elif analysis_type == 'quick':
            add_analysis_to_db_quick('product_analyses_quick', analysis_id, total, analysis_month, positive_percentage, negative_percentage)
            
        st.success(f"✅ تم تحليل {total} تعليق!")
        st.info(f"📊 إيجابي: {positive_percentage}% | سلبي: {negative_percentage}%")
        st.info(f"📅 شهر التحليل: {analysis_month}")
        
        return total, positive_percentage, negative_percentage
        
    except Exception as e:
        st.error(f"❌ خطأ في تحليل البيانات: {str(e)}")
        return None, None, None


# تهيئة قاعدة البيانات
init_database()

# رأس الصفحة
st.markdown("""
<div class="header-box">
    <h1>Sentiment Analyzer</h1>
    <p class="tagline" style="font-size: 1.0rem; letter-spacing: 3px;">Simple · Fast · Accurate</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# تهيئة session_state
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

# الخيارات الرئيسية
st.markdown("### الرجاء اختيار أحد الخيارات التالية :")
st.markdown("<br>", unsafe_allow_html=True) 

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📈 التحليل التراكمي", key="main_dash", use_container_width=True):
        st.session_state.current_page = "dashboard"
        st.rerun()
    st.markdown('<p class="btn-desc">تحليل شامل مع رسومات بيانية</p>', unsafe_allow_html=True)

with col2:
    if st.button("⚡ التحليل السريع", key="main_quick", use_container_width=True):
        st.session_state.current_page = "quick_analysis"
        st.rerun()
    st.markdown('<p class="btn-desc" >تحليل سريع ومباشر</p>', unsafe_allow_html=True)

with col3:
    if st.button("📁 أرشيف التحليلات", key="main_archive", use_container_width=True):
        st.session_state.current_page = "archive"
        st.rerun()
    st.markdown('<p class="btn-desc">تصفح جميع التحليلات السابقة</p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) 
st.markdown("---")

# ──────────────────────────────────────────────
# عرض المحتوى - التحليل التراكمي
# ──────────────────────────────────────────────
if st.session_state.current_page == "dashboard":
    st.header("📈 التحليل التراكمي")
    
    if not st.session_state.get("show_analysis_form_dashboard", False):
        if st.button("➕ إضافة تحليل", key="add_dashboard", use_container_width=True):
            st.session_state.show_analysis_form_dashboard = True
            st.session_state.editing_analysis_id = None
            st.rerun()
    
    if st.session_state.get("show_analysis_form_dashboard", False):
        is_editing = st.session_state.get("editing_analysis_id") is not None
        
        if is_editing:
            st.subheader("✏️ تعديل التحليل - 📈 التحليل التراكمي")
            analysis_data = get_analysis_by_id('dashboard_analyses', st.session_state.editing_analysis_id)
            default_name = analysis_data[1] if analysis_data else ""
            default_type = analysis_data[2] if analysis_data else "مالي"
            default_description = (analysis_data[3] or "") if analysis_data else ""
        else:
            st.subheader("إضافة تحليل جديد - التحليل التراكمي")
            default_name, default_type, default_description = "", "مالي", ""
        
        # ✅ حقول التعديل (الاسم، النوع، الوصف فقط)
        analysis_name = st.text_input("اسم التحليل:", value=default_name, key="name_dashboard")
        analysis_type = st.selectbox("نوع التحليل:", ["مالي", "تسويقي", "تقني", "إداري", "أخرى"], 
                                   index=["مالي", "تسويقي", "تقني", "إداري", "أخرى"].index(default_type) if default_type in ["مالي", "تسويقي", "تقني", "إداري", "أخرى"] else 0, 
                                   key="type_dashboard")
        analysis_description = st.text_area("وصف التحليل:", value=default_description, key="desc_dashboard")
        
        # ✅ حقول الإضافة فقط (تظهر فقط للإضافة الجديدة)
        if not is_editing:
            st.subheader("📅 تاريخ التحليل")
            selected_date = st.date_input("حدد الشهر والسنة:", value=datetime.now(), key="date_dashboard")
            analysis_month = selected_date.strftime('%Y-%m')
            st.info(f"📅 شهر التحليل المحدد: {analysis_month}")
            
            st.subheader("📁 إعدادات البيانات")
            data_path_option = st.radio("طريقة إدخال مسار البيانات:", ["📝 إدخال يدوي", "📤 رفع ملف"], key="data_option_dashboard", horizontal=True)
            
            if data_path_option == "📝 إدخال يدوي":
                data_path = st.text_input("مسار البيانات (مثال: C:/data/analysis.csv):", key="path_dashboard")
                if data_path: st.info(f"سيتم استخدام المسار: {data_path}")
                else: st.warning("⚠️ يرجى إدخال مسار البيانات")
            else:
                uploaded_file = st.file_uploader("اختر ملف البيانات:", type=['csv', 'xlsx', 'txt', 'json'], key="upload_dashboard")
                if uploaded_file:
                    st.success(f"تم تحميل الملف: {uploaded_file.name} ({uploaded_file.size} بايت)")
                else:
                    st.warning("⚠️ يرجى رفع ملف البيانات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            button_text = "💾 حفظ التعديلات" if is_editing else "💾 حفظ التحليل"
            if st.button(button_text, key="save_dashboard", use_container_width=True):
                if not analysis_name:
                    st.error("❌ يرجى إدخال اسم التحليل")
                else:
                    if is_editing:
                        # ✅ تعديل: تحديث الاسم والنوع والوصف فقط
                        update_analysis_info_only('dashboard_analyses', st.session_state.editing_analysis_id, 
                                                analysis_name, analysis_type, analysis_description)
                        st.session_state.show_analysis_form_dashboard = False
                        st.session_state.editing_analysis_id = None
                        st.success("✅ تم تحديث التحليل بنجاح!")
                        st.rerun()
                    else:
                        # ✅ إضافة جديدة
                        error_messages = []
                        if data_path_option == "📝 إدخال يدوي" and not data_path: error_messages.append("❌ يرجى إدخال مسار البيانات")
                        if data_path_option == "📤 رفع ملف" and not uploaded_file: error_messages.append("❌ يرجى رفع ملف البيانات")
                        
                        if error_messages:
                            for error in error_messages: st.error(error)
                        else:
                            if data_path_option == "📤 رفع ملف" and uploaded_file:
                                analysis_id = add_analysis_to_db('dashboard_analyses', analysis_name, analysis_type, analysis_description, "جاري الحفظ...", uploaded_file.name, uploaded_file.size)
                                actual_file_path, saved_name, saved_size = save_uploaded_file(uploaded_file, analysis_id, 'dashboard')
                                conn = sqlite3.connect('analyses.db')
                                conn.execute('UPDATE dashboard_analyses SET data_path = ? WHERE id = ?', (actual_file_path, analysis_id))
                                conn.commit()
                                conn.close()
                                perform_sentiment_analysis(actual_file_path, analysis_id, 'dashboard', analysis_month)
                            else:
                                analysis_id = add_analysis_to_db('dashboard_analyses', analysis_name, analysis_type, analysis_description, data_path, None, None)
                                perform_sentiment_analysis(data_path, analysis_id, 'dashboard', analysis_month)
                            
                            st.session_state.show_analysis_form_dashboard = False
                            st.session_state.editing_analysis_id = None
                            st.success("✅ تم حفظ التحليل بنجاح!")
                            st.rerun()
        
        with col2:
            if st.button("❌ إلغاء", key="cancel_dashboard", use_container_width=True):
                st.session_state.show_analysis_form_dashboard = False
                st.session_state.editing_analysis_id = None
                st.rerun()
    
    st.subheader("تحليلات التحليل التراكمي")
    df_dashboard = get_analyses_from_db('dashboard_analyses')
    
    if not df_dashboard.empty:
        for index, row in df_dashboard.iterrows():
            with st.expander(f"تحليل {row['id']}: {row['name']}"):
                st.write(f"**النوع:** {row['type']}")
                st.write(f"**الوصف:** {row['description']}")
                st.write(f"**مسار البيانات:** `{row['data_path']}`")
                if row['file_name']:
                    st.write(f"**اسم الملف:** {row['file_name']}")
                    st.write(f"**حجم الملف:** {row['file_size']} بايت")
                    if os.path.exists(row['data_path']):
                        with open(row['data_path'], "rb") as file:
                            st.download_button(label="📥 تحميل الملف", data=file, file_name=row['file_name'], key=f"download_dashboard_{row['id']}")
                st.write(f"**تاريخ الإضافة:** {row['created_date']}")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("👁️ عرض", key=f"view_dashboard_{row['id']}", use_container_width=True):
                        st.session_state.selected_analysis_id = row['id']
                        st.session_state.selected_analysis_table = 'dashboard_analyses'
                        st.switch_page("pages/analysis_display.py")
                with col_btn2:
                    if st.button("✏️ تعديل", key=f"edit_dashboard_{row['id']}", use_container_width=True):
                        st.session_state.show_analysis_form_dashboard = True
                        st.session_state.editing_analysis_id = row['id']
                        st.rerun()
                with col_btn3:
                    if st.button("🗑️ حذف", key=f"delete_dashboard_{row['id']}", use_container_width=True):
                        delete_analysis_from_db('dashboard_analyses', row['id'])
                        st.success("✅ تم حذف التحليل بنجاح!")
                        st.rerun()
    else:
        st.info("لم يتم إضافة أي تحليلات في التحليل التراكمي بعد")

# ──────────────────────────────────────────────
# عرض المحتوى - التحليل السريع
# ──────────────────────────────────────────────
elif st.session_state.current_page == "quick_analysis":
    st.header("⚡ التحليل السريع")
    
    if not st.session_state.get("show_analysis_form_quick", False):
        if st.button("➕ إضافة تحليل", key="add_quick", use_container_width=True):
            st.session_state.show_analysis_form_quick = True
            st.session_state.editing_analysis_id_quick = None
            st.rerun()
    
    if st.session_state.get("show_analysis_form_quick", False):
        is_editing = st.session_state.get("editing_analysis_id_quick") is not None
        
        if is_editing:
            st.subheader("✏️ تعديل التحليل - التحليل السريع")
            analysis_data = get_analysis_by_id('quick_analyses', st.session_state.editing_analysis_id_quick)
            default_name = analysis_data[1] if analysis_data else ""
            default_type = analysis_data[2] if analysis_data else "مالي"
            default_description = (analysis_data[3] or "") if analysis_data else ""
        else:
            st.subheader("إضافة تحليل جديد - التحليل السريع")
            default_name, default_type, default_description = "", "مالي", ""
        
        # ✅ حقول التعديل (الاسم، النوع، الوصف فقط)
        analysis_name = st.text_input("اسم التحليل:", value=default_name, key="name_quick")
        analysis_type = st.selectbox("نوع التحليل:", ["مالي", "تسويقي", "تقني", "إداري", "أخرى"], 
                                   index=["مالي", "تسويقي", "تقني", "إداري", "أخرى"].index(default_type) if default_type in ["مالي", "تسويقي", "تقني", "إداري", "أخرى"] else 0, 
                                   key="type_quick")
        analysis_description = st.text_area("وصف التحليل:", value=default_description, key="desc_quick")
        
        # ✅ حقول الإضافة فقط
        if not is_editing:
            st.subheader("📅 تاريخ التحليل")
            selected_date = st.date_input("حدد الشهر والسنة:", value=datetime.now(), key="date_quick")
            analysis_month = selected_date.strftime('%Y-%m')
            st.info(f"📅 شهر التحليل المحدد: {analysis_month}")
            
            st.subheader("📁 إعدادات البيانات")
            data_path_option = st.radio("طريقة إدخال مسار البيانات:", ["📝 إدخال يدوي", "📤 رفع ملف"], key="data_option_quick", horizontal=True)
            
            if data_path_option == "📝 إدخال يدوي":
                data_path = st.text_input("مسار البيانات (مثال: C:/data/analysis.csv):", key="path_quick")
                if data_path: st.info(f"سيتم استخدام المسار: {data_path}")
                else: st.warning("⚠️ يرجى إدخال مسار البيانات")
            else:
                uploaded_file = st.file_uploader("اختر ملف البيانات:", type=['csv', 'xlsx', 'txt', 'json'], key="upload_quick")
                if uploaded_file:
                    st.success(f"تم تحميل الملف: {uploaded_file.name} ({uploaded_file.size} بايت)")
                else:
                    st.warning("⚠️ يرجى رفع ملف البيانات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            button_text = "💾 حفظ التعديلات" if is_editing else "💾 حفظ التحليل"
            if st.button(button_text, key="save_quick", use_container_width=True):
                if not analysis_name:
                    st.error("❌ يرجى إدخال اسم التحليل")
                else:
                    if is_editing:
                        # ✅ تعديل: تحديث الاسم والنوع والوصف فقط
                        update_analysis_info_only('quick_analyses', st.session_state.editing_analysis_id_quick, 
                                                analysis_name, analysis_type, analysis_description)
                        st.session_state.show_analysis_form_quick = False
                        st.session_state.editing_analysis_id_quick = None
                        st.success("✅ تم تحديث التحليل بنجاح!")
                        st.rerun()
                    else:
                        # ✅ إضافة جديدة
                        error_messages = []
                        if data_path_option == "📝 إدخال يدوي" and not data_path: error_messages.append("❌ يرجى إدخال مسار البيانات")
                        if data_path_option == "📤 رفع ملف" and not uploaded_file: error_messages.append("❌ يرجى رفع ملف البيانات")
                        
                        if error_messages:
                            for error in error_messages: st.error(error)
                        else:
                            if data_path_option == "📤 رفع ملف" and uploaded_file:
                                analysis_id = add_analysis_to_db('quick_analyses', analysis_name, analysis_type, analysis_description, "جاري الحفظ...", uploaded_file.name, uploaded_file.size)
                                actual_file_path, saved_name, saved_size = save_uploaded_file(uploaded_file, analysis_id, 'quick')
                                conn = sqlite3.connect('analyses.db')
                                conn.execute('UPDATE quick_analyses SET data_path = ? WHERE quick_id = ?', (actual_file_path, analysis_id))
                                conn.commit()
                                conn.close()
                                perform_sentiment_analysis(actual_file_path, analysis_id, 'quick', analysis_month)
                            else:
                                analysis_id = add_analysis_to_db('quick_analyses', analysis_name, analysis_type, analysis_description, data_path, None, None)
                                perform_sentiment_analysis(data_path, analysis_id, 'quick', analysis_month)
                            
                            st.session_state.show_analysis_form_quick = False
                            st.session_state.editing_analysis_id_quick = None
                            st.success("✅ تم حفظ التحليل بنجاح!")
                            st.rerun()
        
        with col2:
            if st.button("❌ إلغاء", key="cancel_quick", use_container_width=True):
                st.session_state.show_analysis_form_quick = False
                st.session_state.editing_analysis_id_quick = None
                st.rerun()
    
    st.subheader("تحليلات التحليل السريع")
    df_quick = get_analyses_from_db('quick_analyses')
    
    if not df_quick.empty:
        for index, row in df_quick.iterrows():
            with st.expander(f"تحليل {row['id']}: {row['name']}"):
                st.write(f"**النوع:** {row['type']}")
                st.write(f"**الوصف:** {row['description']}")
                st.write(f"**مسار البيانات:** `{row['data_path']}`")
                if row['file_name']:
                    st.write(f"**اسم الملف:** {row['file_name']}")
                    st.write(f"**حجم الملف:** {row['file_size']} بايت")
                    if os.path.exists(row['data_path']):
                        with open(row['data_path'], "rb") as file:
                            st.download_button(label="📥 تحميل الملف", data=file, file_name=row['file_name'], key=f"download_quick_{row['id']}")
                st.write(f"**تاريخ الإضافة:** {row['created_date']}")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("👁️ عرض", key=f"view_quick_{row['id']}", use_container_width=True):
                        st.session_state.selected_analysis_id = row['id']
                        st.session_state.selected_analysis_table = 'quick_analyses'
                        st.switch_page("pages/‏‏analysis_display_quick.py")
                with col_btn2:
                    if st.button("✏️ تعديل", key=f"edit_quick_{row['id']}", use_container_width=True):
                        st.session_state.show_analysis_form_quick = True
                        st.session_state.editing_analysis_id_quick = row['id']
                        st.rerun()
                with col_btn3:
                    if st.button("🗑️ حذف", key=f"delete_quick_{row['id']}", use_container_width=True):
                        delete_analysis_from_db('quick_analyses', row['id'])
                        st.success("✅ تم حذف التحليل بنجاح!")
                        st.rerun()
    else:
        st.info("لم يتم إضافة أي تحليلات في التحليل السريع بعد")

# ──────────────────────────────────────────────
# عرض المحتوى - الأرشيف
# ──────────────────────────────────────────────
elif st.session_state.current_page == "archive":
    st.header("📁 أرشيف التحليلات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("تحليلات التحليل التراكمي")
        df_dashboard = get_analyses_from_db('dashboard_analyses')
        if not df_dashboard.empty:
            st.dataframe(df_dashboard[['name', 'type', 'created_date']])
        else:
            st.info("لا توجد تحليلات في التحليل التراكمي")
    
    with col2:
        st.subheader("تحليلات التحليل السريع")
        df_quick = get_analyses_from_db('quick_analyses')
        if not df_quick.empty:
            st.dataframe(df_quick[['name', 'type', 'created_date']])
        else:
            st.info("لا توجد تحليلات في التحليل السريع")

# ──────────────────────────────────────────────
# زر العودة
# ──────────────────────────────────────────────
if st.session_state.current_page != "main":
    st.markdown("---")
    if st.button("العودة إلى الصفحة الرئيسية", key="back_to_main", use_container_width=True):
        st.session_state.current_page = "main"
        st.rerun()
