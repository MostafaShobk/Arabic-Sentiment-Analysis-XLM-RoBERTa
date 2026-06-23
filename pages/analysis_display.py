# analysis_display.py - ملف منفصل لعرض تحليلات المنتجات مع الرسومات (لوحة التحكم فقط)

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
import sys

# إضافة المسار لاستيراد Sentiment_Analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentiment_analyzer import Sentiment_Analyzer
from utils.data_pipeline import *

# إعداد الصفحة
st.set_page_config(
    page_title="عرض التحليل التفصيلي",
    page_icon="📊",
    layout="wide"
)

# ──────────────────────────────────────────────
# CSS للتنسيق الكامل للصفحة
# ──────────────────────────────────────────────

st.markdown("""
<style>
    /* ── الأساسيات ── */
    .stApp {
        margin-top: -80px;
        direction: rtl;
        text-align: right;
        background: 	#fafafa;
    }
    
    /* ── العناوين ── */
     h1 {
    text-align: right;        
    font-size: 2.8rem;
    font-weight: 800;
    color: #2c3e50;            
    margin-bottom: 5px;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #667eea;
}
    
    h2, h3, h4, h5, h6 {
        text-align: right;
        direction: rtl;
        color: #2c3e50;
    }
    
    .stMarkdown {
        text-align: right;
        direction: rtl;
    }
    
    /* ── الحاوية الرئيسية ── */
    .main-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 10px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* ── بطاقة معلومات التحليل ── */
    .analysis-info-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 25px;
    border-radius: 20px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    position: relative;
    overflow: hidden;
}

.analysis-info-card::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: 
        linear-gradient(rgba(255,255,255,0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.12) 1px, transparent 1px);
    background-size: 30px 30px;
    animation: gridMove 5s linear infinite;
}
@keyframes gridMove {
    0% { transform: translate(0, 0); }
    100% { transform: translate(30px, 30px); }
}







    
    .analysis-info-card .info-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 15px;
        position: relative;
        z-index: 1;
    }
    
    .analysis-info-card .info-details {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    
    .analysis-info-card .info-item {
        background: rgba(255, 255, 255, 0.2);
        padding: 10px 20px;
        border-radius: 15px;
        backdrop-filter: blur(5px);
    }
    
    /* ── البطاقات المترية ── */
    .metrics-container {
        display: flex;
        gap: 15px;
        margin: 20px 0;
    }
    
    .metric-card {
        background: white;
        padding: 25px 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 150px;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card:hover::after {
        transform: scaleX(1);
    }
    
    .metric-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }
    
    .metric-label {
        font-size: 12px;
        color: #7f8c8d;
        margin-bottom: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #2c3e50;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    
    .metric-subtitle {
        font-size: 11px;
        color: #95a5a6;
    }
    
    /* ── شارات المؤشرات ── */
    .metric-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 25px;
        font-size: 12px;
        font-weight: 700;
        margin-top: 8px;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    
    .metric-badge:hover {
        transform: scale(1.05);
    }
    
    /* ── ملاحظة الجودة ── */
    .quality-note {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        margin: 20px 0;
        text-align: center;
        position: relative;
        box-shadow: 0 10px 30px rgba(243, 156, 18, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .quality-note .note-icon {
        font-size: 40px;
        display: block;
        margin-bottom: 12px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .quality-note .note-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .quality-note .note-text {
        font-size: 15px;
        opacity: 0.95;
        line-height: 1.8;
    }
    
    .quality-note .note-highlight {
        background: rgba(255, 255, 255, 0.3);
        padding: 4px 12px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    /* ── الأزرار ── */
    .stButton > button {
        border-radius: 15px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* ── الموسعات (Expander) ── */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* ── فواصل ── */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 25px 0;
        border-radius: 2px;
    }
    
    /* ── تذييل ── */
    .footer {
        text-align: center;
        padding: 20px;
        color: #95a5a6;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# إعدادات التحليل
# ──────────────────────────────────────────────

RECOMMENDED_COMMENTS = 100

# ──────────────────────────────────────────────
# دوال حساب الاتجاه
# ──────────────────────────────────────────────

def calculate_trend(df):
    """حساب الاتجاه باستخدام الانحدار الخطي"""
    if len(df) < 2:
        return 0, 0, "لا يوجد بيانات كافية", "#95a5a6", "#ecf0f1"
    
    df = df.sort_values('analysis_month')
    x = np.arange(len(df))
    y = df['positive_percentage'].values
    slope, intercept = np.polyfit(x, y, 1)
    total_change = slope * (len(df) - 1)
    
    if slope > 1:
        trend_text = f"📈 تحسن"
        trend_color = "#2ecc71"
        trend_bg = "#d4edda"
    elif slope < -1:
        trend_text = f"📉 تراجع"
        trend_color = "#e74c3c"
        trend_bg = "#f8d7da"
    else:
        trend_text = "➡️ استقرار"
        trend_color = "#3498db"
        trend_bg = "#d6eaf8"
    
    return total_change, slope, trend_text, trend_color, trend_bg

# ──────────────────────────────────────────────
# دوال قاعدة البيانات - لوحة التحكم فقط
# ──────────────────────────────────────────────

def get_product_analyses(analysis_id):
    """جلب تحليلات المنتجات المرتبطة بتحليل لوحة التحكم"""
    conn = sqlite3.connect('analyses.db')
    
    query = '''
        SELECT 
            pa.*,
            da.name as analysis_name
        FROM product_analyses_dash pa
        LEFT JOIN dashboard_analyses da ON pa.dashboard_id = da.id
        WHERE pa.dashboard_id = ?
        ORDER BY pa.analysis_month
    '''
    
    df = pd.read_sql(query, conn, params=(analysis_id,))
    conn.close()
    return df

def get_analysis_info(analysis_id):
    """جلب معلومات تحليل لوحة التحكم"""
    conn = sqlite3.connect('analyses.db')
    query = "SELECT * FROM dashboard_analyses WHERE id = ?"
    df = pd.read_sql(query, conn, params=(analysis_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def delete_product_analysis(analysis_id, product_analysis_id):
    """حذف تحليل منتج محدد من لوحة التحكم"""
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM product_analyses_dash WHERE analysis_id = ? AND dashboard_id = ?', 
                 (product_analysis_id, analysis_id))
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        return deleted_count > 0
    except Exception as e:
        conn.close()
        st.error(f"❌ خطأ في حذف التحليل: {str(e)}")
        return False

def update_analysis_month(analysis_id, product_analysis_id, new_month):
    """تحديث شهر التحليل"""
    conn = sqlite3.connect('analyses.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            UPDATE product_analyses_dash 
            SET analysis_month = ? 
            WHERE analysis_id = ? AND dashboard_id = ?
        ''', (new_month, product_analysis_id, analysis_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        st.error(f"❌ خطأ في تحديث التاريخ: {str(e)}")
        return False

# ──────────────────────────────────────────────
# دوال معالجة الملفات والتحليل
# ──────────────────────────────────────────────

def save_uploaded_file(uploaded_file, analysis_id):
    """حفظ الملف المرفوع وإرجاع المسار الفعلي"""
    files_dir = "data_files"
    os.makedirs(files_dir, exist_ok=True)
    
    file_name = f"dashboard_{analysis_id}_{uploaded_file.name}"
    file_path = os.path.join(files_dir, file_name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    absolute_path = os.path.abspath(file_path)
    return absolute_path, uploaded_file.name, uploaded_file.size

def perform_sentiment_analysis(data_path, analysis_id, analysis_month):
    """تنفيذ تحليل المشاعر على الملف وحفظ النتائج في قاعدة البيانات"""
    try:
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        elif data_path.endswith('.xlsx'):
            df = pd.read_excel(data_path)
        elif data_path.endswith('.json'):
            df = pd.read_json(data_path)
        elif data_path.endswith('.txt'):
            df = pd.read_csv(data_path, sep='\t')
        else:
            st.warning(f"⚠️ نوع الملف غير مدعوم: {data_path}")
            return False
        
        text_column = None
        for col in df.columns:
            if col.lower() in ['text', 'review', 'comment', 'نص', 'تعليق', 'مراجعة', 'description', 'content']:
                text_column = col
                break
        
        if text_column is None:
            text_column = df.select_dtypes(include=['object']).columns[0] if len(df.select_dtypes(include=['object']).columns) > 0 else df.columns[0]
        
        texts = df[text_column].astype(str).tolist()
        number_of_comments = len(texts)
        
        try:
            cleaned_texts = [clean_text(text) for text in texts]
        except:
            cleaned_texts = texts
        
        with st.spinner("🔄 جاري تحليل المشاعر... يرجى الانتظار"):
            sa = Sentiment_Analyzer(texts, cleaned_texts)
            total, positive_percentage, negative_percentage = sa.get_sentiments()
        
        conn = sqlite3.connect('analyses.db')
        c = conn.cursor()
        
        c.execute('DELETE FROM product_analyses_dash WHERE dashboard_id = ? AND analysis_month = ?', 
                 (analysis_id, analysis_month))
        
        c.execute('''
            INSERT INTO product_analyses_dash 
            (dashboard_id, number_of_comments, analysis_month, 
             positive_percentage, negative_percentage)
            VALUES (?, ?, ?, ?, ?)
        ''', (analysis_id, number_of_comments, analysis_month,
             round(positive_percentage), round(negative_percentage)))
        
        conn.commit()
        conn.close()
        
        st.success(f"""
        ✅ **تم تحليل البيانات بنجاح!**
        - 📊 عدد التعليقات: **{total}**
        - 😊 نسبة الإيجابية: **{positive_percentage}%**
        - 😞 نسبة السلبية: **{negative_percentage}%**
        """)
        
        return True
        
    except Exception as e:
        st.error(f"❌ خطأ في تحليل البيانات: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False

# ──────────────────────────────────────────────
# دوال الرسومات البيانية
# ──────────────────────────────────────────────

def create_sentiment_bar(positive, negative):
    """إنشاء شريط تقدم للمشاعر"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=['المشاعر'],
        x=[positive],
        name='إيجابي',
        orientation='h',
        marker=dict(color='#2ecc71'),
        text=f'{positive}%',
        textposition='inside',
        insidetextanchor='middle'
    ))
    
    fig.add_trace(go.Bar(
        y=['المشاعر'],
        x=[negative],
        name='سلبي',
        orientation='h',
        marker=dict(color='#e74c3c'),
        text=f'{negative}%',
        textposition='inside',
        insidetextanchor='middle'
    ))
    
    fig.update_layout(
        barmode='stack',
        height=100,
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_simple_scatter_plot(df):
    """إنشاء رسم بياني نقطي مع خط الانحدار"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['analysis_month'],
        y=df['positive_percentage'],
        mode='lines+markers',
        name='نسبة الإيجابية',
        line=dict(color='#667eea', width=3),
        marker=dict(size=12, color='#667eea', line=dict(width=2, color='white')),
        hovertemplate='<b>Month:</b> %{x}<br><b>positive_percent:</b> %{y}%<extra></extra>'
    ))
    
    if len(df) > 1:
        df_sorted = df.sort_values('analysis_month')
        x = np.arange(len(df_sorted))
        y = df_sorted['positive_percentage'].values
        slope, intercept = np.polyfit(x, y, 1)
        trend_line = slope * x + intercept
        
        fig.add_trace(go.Scatter(
            x=df_sorted['analysis_month'],
            y=trend_line,
            mode='lines',
            name='خط الاتجاه',
            line=dict(color='#e74c3c', width=2, dash='dash'),
            hovertemplate='<b>Trend:</b> %{y:.1f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text="📈 نسبة الإيجابية لكل شهر مع خط الاتجاه",
            font=dict(size=20, color='#2c3e50'),
            x=0.5,
            xref='container', 
            xanchor='center'   
        ),
        height=450,
        xaxis_title="شهر التحليل",
        yaxis_title="نسبة الإيجابية (%)",
        yaxis=dict(range=[0, 100], gridcolor='#ecf0f1'),
        xaxis=dict(gridcolor='#ecf0f1'),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial, sans-serif')
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig

def display_kpi_metrics(df):
    """عرض المؤشرات الإجمالية مع الاتجاه والتباين"""
    
    total_change, slope, trend_text, trend_color, trend_bg = calculate_trend(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # بطاقة 1: عدد الأشهر
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📅</div>
            <div class="metric-label">عدد الأشهر</div>
            <div class="metric-value">{len(df)}</div>
            <div class="metric-subtitle">شهر تحليل</div>
        </div>
        """, unsafe_allow_html=True)
    
    # بطاقة 2: إجمالي التعليقات
    with col2:
        total_comments = df['number_of_comments'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💬</div>
            <div class="metric-label">إجمالي التعليقات</div>
            <div class="metric-value">{total_comments:,}</div>
            <div class="metric-subtitle">تعليق محلل</div>
        </div>
        """, unsafe_allow_html=True)
    
    # بطاقة 3: متوسط الإيجابية + التباين
    with col3:
        avg_positive = df['positive_percentage'].mean()
        
        if len(df) > 1:
            std_value = df['positive_percentage'].std()
            
            if std_value <= 5:
                variance_color = "#2ecc71"
                variance_bg = "#d4edda"
                variance_text = "مستقر ✅"
            elif std_value <= 15:
                variance_color = "#f39c12"
                variance_bg = "#fff3cd"
                variance_text = "متذبذب ⚠️"
            else:
                variance_color = "#e74c3c"
                variance_bg = "#f8d7da"
                variance_text = "غير مستقر ❌"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">😊</div>
                <div class="metric-label">متوسط الإيجابية</div>
                <div class="metric-value">{avg_positive:.1f}%</div>
                <div class="metric-badge" style="background: {variance_bg}; color: {variance_color};">
                    {variance_text} ±{std_value:.1f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">😊</div>
                <div class="metric-label">متوسط الإيجابية</div>
                <div class="metric-value">{avg_positive:.1f}%</div>
                <div class="metric-subtitle">شهر واحد فقط</div>
            </div>
            """, unsafe_allow_html=True)
    
    # بطاقة 4: معدل التغير الشهري + الاتجاه
    with col4:
        if len(df) > 1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-label">معدل التغير الشهري</div>
                <div class="metric-value" style="color: {trend_color};">{slope:+.1f}%</div>
                <div class="metric-badge" style="background: {trend_bg}; color: {trend_color};">
                    {trend_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-label">معدل التغير الشهري</div>
                <div class="metric-value" style="color: #95a5a6;">—</div>
                <div class="metric-subtitle">تحتاج شهرين فأكثر</div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# الكود الرئيسي للتطبيق
# ──────────────────────────────────────────────

def main():


    st.markdown("""
    <style>
        /* الشريط الجانبي */
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none; }
        
        /* الشريط العلوي و Deploy */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stDecoration"] { display: none; }
        [data-testid="stToolbar"] { display: none; }
        

    </style>
    """, unsafe_allow_html=True)
    # ✅ رأس الصفحة بتنسيق جميل
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 30px 0;">
        <h1 style=" font-size: 2.8rem; margin-bottom: 5px;">عرض التحليل</h1>
        <p style="color: #7f8c8d; font-size: 1.1rem;">لوحة تحكم متكاملة لتحليل مشاعر </p>
   </div>
    """, unsafe_allow_html=True)
    
    # التحقق من وجود تحليل محدد في session_state
    if 'selected_analysis_id' not in st.session_state:
        st.warning("⚠️ لم يتم تحديد تحليل للعرض. الرجاء العودة واختيار تحليل.")
        if st.button("🔙 العودة للقائمة الرئيسية", use_container_width=True):
            st.switch_page("app.py")
        return
    
    analysis_id = st.session_state.selected_analysis_id
    
    # جلب معلومات التحليل
    analysis_info = get_analysis_info(analysis_id)
    
    if analysis_info is None:
        st.error("❌ لم يتم العثور على التحليل المطلوب")
        return
    
    # ✅ بطاقة معلومات التحليل الرئيسي بتنسيق جميل
    st.markdown(f"""
    <div class="analysis-info-card">
        <div class="info-title">📋 {analysis_info['name']}</div>
        <div class="info-details">
            <div class="info-item">📌 النوع: <strong>{analysis_info['type']}</strong></div>
            <div class="info-item">📅 تاريخ الإنشاء: <strong>{analysis_info['created_date']}</strong></div>
            {"<div class='info-item'>📁 الملف: <strong>" + analysis_info['file_name'] + "</strong></div>" if analysis_info['file_name'] else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if analysis_info['description']:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 15px; margin-bottom: 20px; border-right: 4px solid #667eea;">
            <strong>📝 الوصف:</strong> {analysis_info['description']}
        </div>
        """, unsafe_allow_html=True)
    
    # جلب تحليلات المنتجات
    df_products = get_product_analyses(analysis_id)
    
    if df_products.empty:
        st.info("📭 لا توجد تحليلات منتجات مرتبطة بهذا التحليل")
    
    # عرض المؤشرات الإجمالية
    if not df_products.empty:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 المؤشرات الإجمالية")
        display_kpi_metrics(df_products)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ✅ ملاحظة جودة البيانات بتنسيق جميل
    if not st.session_state.get("hide_quality_note", False):
        col_note, col_close = st.columns([20, 1])
        
        with col_note:
            st.markdown(f"""
            <div class="quality-note">
                <span class="note-icon">💡</span>
                <div class="note-title">نصيحة للحصول على نتائج دقيقة</div>
                <div class="note-text">
                    يفضل أن يكون عدد التعليقات في كل تحليل 
                    <span class="note-highlight">{RECOMMENDED_COMMENTS} تعليق</span> 
                    على الأقل للحصول على نتائج ذات دلالة إحصائية موثوقة
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_close:
            if st.button("✕", key="close_quality_note", help="إخفاء الملاحظة"):
                st.session_state.hide_quality_note = True
                st.rerun()
    
    # ✅ زر إضافة تحليل بتنسيق جميل
    if not st.session_state.get("show_add_product_analysis", False):
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("➕ إضافة تحليل شهر جديد", use_container_width=True, type="primary"):
                st.session_state.show_add_product_analysis = True
                st.rerun()
    
    # نموذج إضافة تحليل شهر جديد
    if st.session_state.get("show_add_product_analysis", False):
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 20px; border-radius: 20px; margin-bottom: 20px;">
            <h3 style="text-align: center; color: #2c3e50;">📝 إضافة تحليل شهر جديد</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # أداة اختيار التاريخ
        st.markdown("#### 📅 تاريخ التحليل")
        selected_date = st.date_input(
            "حدد الشهر والسنة:",
            value=datetime.now(),
            key="date_product_analysis"
        )
        analysis_month = selected_date.strftime('%Y-%m')
        st.info(f"📅 شهر التحليل المحدد: **{analysis_month}**")
        
        # إعدادات البيانات
        st.markdown("#### 📁 إعدادات البيانات")
        data_path_option = st.radio(
            "طريقة إدخال مسار البيانات:",
            ["📝 إدخال يدوي", "📤 رفع ملف"],
            key="data_option_product_analysis",
            horizontal=True
        )
        
        data_path = ""
        uploaded_file = None
        
        if data_path_option == "📝 إدخال يدوي":
            data_path = st.text_input("مسار البيانات:", placeholder="مثال: C:/data/analysis.csv", key="path_product_analysis")
            if data_path:
                st.info(f"📂 سيتم استخدام المسار: `{data_path}`")
            else:
                st.warning("⚠️ يرجى إدخال مسار البيانات")
        else:
            uploaded_file = st.file_uploader("اختر ملف البيانات:", type=['csv', 'xlsx', 'txt', 'json'], key="upload_product_analysis")
            if uploaded_file:
                st.success(f"✅ تم تحميل الملف: **{uploaded_file.name}** ({uploaded_file.size:,} بايت)")
            else:
                st.warning("⚠️ يرجى رفع ملف البيانات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 تحليل وحفظ", key="save_product_analysis", use_container_width=True, type="primary"):
                error_messages = []
                
                if data_path_option == "📝 إدخال يدوي" and not data_path:
                    error_messages.append("❌ يرجى إدخال مسار البيانات")
                if data_path_option == "📤 رفع ملف" and not uploaded_file:
                    error_messages.append("❌ يرجى رفع ملف البيانات")
                
                if error_messages:
                    for error in error_messages:
                        st.error(error)
                else:
                    if data_path_option == "📤 رفع ملف" and uploaded_file:
                        actual_file_path, saved_name, saved_size = save_uploaded_file(uploaded_file, analysis_id)
                        st.success(f"💾 تم حفظ الملف في: `{actual_file_path}`")
                        success = perform_sentiment_analysis(actual_file_path, analysis_id, analysis_month)
                    else:
                        success = perform_sentiment_analysis(data_path, analysis_id, analysis_month)
                    
                    if success:
                        st.session_state.show_add_product_analysis = False
                        st.balloons()
                        st.success("🎉 تم حفظ التحليل بنجاح!")
                        st.rerun()
        
        with col2:
            if st.button("❌ إلغاء", key="cancel_product_analysis", use_container_width=True):
                st.session_state.show_add_product_analysis = False
                st.rerun()
    
    # عرض جدول المنتجات
    if not df_products.empty:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 تحليلات المنتجات")
        
        for idx, row in df_products.iterrows():
            with st.expander(f"📌 شهر {row['analysis_month']} | {row['number_of_comments']} تعليق"):
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**📋 معلومات التحليل:**")
                    st.write(f"- 💬 عدد التعليقات: **{row['number_of_comments']}**")
                    
                    if row['number_of_comments'] < RECOMMENDED_COMMENTS:
                        st.warning(f"⚠️ عدد التعليقات أقل من {RECOMMENDED_COMMENTS} (الموصى به)")
                    
                    if st.session_state.get(f"edit_month_{row['analysis_id']}", False):
                        new_date = st.date_input(
                            "تعديل الشهر:",
                            value=datetime.strptime(row['analysis_month'], '%Y-%m'),
                            key=f"date_edit_{row['analysis_id']}"
                        )
                        new_month = new_date.strftime('%Y-%m')
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 حفظ", key=f"save_month_{row['analysis_id']}", use_container_width=True):
                                success = update_analysis_month(analysis_id, row['analysis_id'], new_month)
                                if success:
                                    st.success("✅ تم تحديث التاريخ بنجاح!")
                                    st.session_state[f"edit_month_{row['analysis_id']}"] = False
                                    st.rerun()
                        with col_cancel:
                            if st.button("❌ إلغاء", key=f"cancel_month_{row['analysis_id']}", use_container_width=True):
                                st.session_state[f"edit_month_{row['analysis_id']}"] = False
                                st.rerun()
                    else:
                        st.write(f"- 📅 شهر التحليل: **{row['analysis_month']}**")
                
                with col2:
                    st.markdown("توزيع المشاعر:")
                    sentiment_chart = create_sentiment_bar(row['positive_percentage'], row['negative_percentage'])
                    st.plotly_chart(sentiment_chart, use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)  #
                
                st.markdown("---")
                col_btn1, col_btn2 = st.columns([1, 1])
                
                with col_btn1:
                    if not st.session_state.get(f"edit_month_{row['analysis_id']}", False):
                        if st.button("📅 تعديل التاريخ", key=f"edit_month_btn_{row['analysis_id']}", use_container_width=True):
                            st.session_state[f"edit_month_{row['analysis_id']}"] = True
                            st.rerun()
                
                with col_btn2:
                    delete_key = f"delete_{row['analysis_id']}"
                    if delete_key not in st.session_state:
                        st.session_state[delete_key] = False
                    
                    if not st.session_state[delete_key]:
                        if st.button("🗑️ حذف", key=f"delete_btn_{row['analysis_id']}", use_container_width=True):
                            st.session_state[delete_key] = True
                            st.rerun()
                    else:
                        st.error(f"⚠️ هل أنت متأكد من حذف تحليل شهر {row['analysis_month']}؟")
                        col_confirm1, col_confirm2 = st.columns(2)
                        
                        with col_confirm1:
                            if st.button("✅ نعم، احذف", key=f"confirm_delete_{row['analysis_id']}", use_container_width=True):
                                success = delete_product_analysis(analysis_id, row['analysis_id'])
                                if success:
                                    st.success(f"✅ تم حذف تحليل شهر {row['analysis_month']} بنجاح!")
                                    st.session_state[delete_key] = False
                                    st.rerun()
                                else:
                                    st.error("❌ فشل في حذف التحليل")
                        
                        with col_confirm2:
                            if st.button("❌ إلغاء", key=f"cancel_delete_{row['analysis_id']}", use_container_width=True):
                                st.session_state[delete_key] = False
                                st.rerun()
        
        # رسم بياني
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
 
        
        if len(df_products) > 0:
            scatter = create_simple_scatter_plot(df_products)
            st.plotly_chart(scatter, use_container_width=True)
    
    # ✅ تذييل الصفحة
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col_footer1, col_footer2, col_footer3 = st.columns([1, 2, 1])
    with col_footer2:
        if st.button("🔙 العودة إلى القائمة الرئيسية", use_container_width=True, type="secondary"):
            if "hide_quality_note" in st.session_state:
                del st.session_state.hide_quality_note
            st.switch_page("app.py")

if __name__ == "__main__":
    main()
