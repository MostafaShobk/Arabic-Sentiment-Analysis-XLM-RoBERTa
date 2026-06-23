# analysis_display_quick.py - عرض تحليلات المنتجات للتحليل السريع

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentiment_analyzer import Sentiment_Analyzer
from utils.data_pipeline import *

st.set_page_config(page_title="عرض التحليل السريع", page_icon="⚡", layout="wide")

# ── إعدادات ──
RECOMMENDED_COMMENTS = 100

# ── CSS ──
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; background: #fafafa; }
    
    h1 { text-align: right; font-size: 2.5rem; font-weight: 800; color: #2c3e50; margin-bottom: 5px; padding-bottom: 0.5rem; border-bottom: 3px solid #667eea; }
    h2, h3 { text-align: right; color: #2c3e50; }
    .stMarkdown { text-align: right; direction: rtl; }
    
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    footer { display: none; }
    
    .analysis-info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px; border-radius: 20px; color: white; margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3); position: relative; overflow: hidden;
    }
    .analysis-info-card::before {
        content: ''; position: absolute; width: 100%; height: 100%;
        background: linear-gradient(rgba(255,255,255,0.12) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.12) 1px, transparent 1px);
        background-size: 30px 30px; animation: gridMove 5s linear infinite;
    }
    @keyframes gridMove { 0% { transform: translate(0, 0); } 100% { transform: translate(30px, 30px); } }
    .analysis-info-card .info-title { font-size: 1.8rem; font-weight: bold; margin-bottom: 15px; position: relative; z-index: 1; }
    .analysis-info-card .info-details { display: flex; gap: 20px; flex-wrap: wrap; position: relative; z-index: 1; }
    .analysis-info-card .info-item { background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 15px; }
    
    /* بطاقات المؤشرات */
    .metric-card {
        background: white; padding: 25px 15px; border-radius: 20px; text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.06); border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease; min-height: 140px;
        display: flex; flex-direction: column; justify-content: center;
        position: relative; overflow: hidden;
    }
    .metric-card::after {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0); transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    .metric-card:hover::after { transform: scaleX(1); }
    .metric-icon { font-size: 28px; margin-bottom: 8px; }
    .metric-label { font-size: 12px; color: #7f8c8d; margin-bottom: 8px; font-weight: 600; }
    .metric-value { font-size: 32px; font-weight: 800; color: #2c3e50; }
    .metric-subtitle { font-size: 11px; color: #95a5a6; margin-top: 5px; }
    
    /* عنوان الشهر */
    .simple-month {
        background: white; padding: 15px 20px; border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06); margin-bottom: 12px;
        border: 1px solid #eee; text-align: center;
        font-size: 1.1rem; font-weight: 600; color: #667eea;
        transition: all 0.3s ease;
        position: relative; overflow: hidden;
    }
    .simple-month::after {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0); transition: transform 0.3s ease;
    }
    .simple-month:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102,126,234,0.2); }
    .simple-month:hover::after { transform: scaleX(1); }
    
    /* ✅ ملاحظة الجودة */
    .quality-note {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        padding: 25px; border-radius: 20px; color: white; margin: 20px 0;
        text-align: center; position: relative;
        box-shadow: 0 10px 30px rgba(243, 156, 18, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    .quality-note .note-icon { font-size: 40px; display: block; margin-bottom: 12px; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
    .quality-note .note-title { font-size: 20px; font-weight: bold; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .quality-note .note-text { font-size: 15px; opacity: 0.95; line-height: 1.8; }
    .quality-note .note-highlight {
        background: rgba(255, 255, 255, 0.3); padding: 4px 12px;
        border-radius: 25px; font-weight: bold; font-size: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .stButton > button {
        border-radius: 15px; font-weight: 600; padding: 12px 24px; font-size: 16px;
        border: none; background: linear-gradient(135deg, #667eea, #764ba2); color: white;
        transition: all 0.3s ease;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102,126,234,0.4); }
    
    .divider { height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent); margin: 25px 0; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── دوال قاعدة البيانات ──
def get_product_analyses(analysis_id):
    conn = sqlite3.connect('analyses.db')
    query = '''
        SELECT pa.*, qa.name as analysis_name
        FROM product_analyses_quick pa
        LEFT JOIN quick_analyses qa ON pa.quick_id = qa.quick_id
        WHERE pa.quick_id = ?
        ORDER BY pa.analysis_month
    '''
    df = pd.read_sql(query, conn, params=(analysis_id,))
    conn.close()
    return df

def get_analysis_info(analysis_id):
    conn = sqlite3.connect('analyses.db')
    df = pd.read_sql("SELECT * FROM quick_analyses WHERE quick_id = ?", conn, params=(analysis_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None

# ── دوال الرسومات ──
def create_sentiment_bar(positive, negative):
    fig = go.Figure()
    fig.add_trace(go.Bar(y=['المشاعر'], x=[positive], name='إيجابي', orientation='h',
                        marker=dict(color='#2ecc71'), text=f'{positive}%', textposition='inside'))
    fig.add_trace(go.Bar(y=['المشاعر'], x=[negative], name='سلبي', orientation='h',
                        marker=dict(color='#e74c3c'), text=f'{negative}%', textposition='inside'))
    fig.update_layout(barmode='stack', height=80, margin=dict(l=10, r=10, t=30, b=10),
                     showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="right", x=1),
                     xaxis=dict(range=[0,100], showticklabels=False, showgrid=False),
                     yaxis=dict(showticklabels=False, showgrid=False),
                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

# ── الكود الرئيسي ──
def main():
    st.markdown('<div style="text-align:center;padding:20px 0 30px 0;"><h1 style="text-align:center;">⚡ عرض التحليل السريع</h1></div>', unsafe_allow_html=True)
    
    if 'selected_analysis_id' not in st.session_state:
        st.warning("⚠️ لم يتم تحديد تحليل للعرض")
        if st.button("🔙 العودة", use_container_width=True): st.switch_page("app.py")
        return
    
    analysis_id = st.session_state.selected_analysis_id
    analysis_info = get_analysis_info(analysis_id)
    
    if analysis_info is None:
        st.error("❌ لم يتم العثور على التحليل")
        return
    
    # بطاقة المعلومات الرئيسية
    st.markdown(f"""
    <div class="analysis-info-card">
        <div class="info-title">📋 {analysis_info['name']}</div>
        <div class="info-details">
            <div class="info-item">📌 النوع: <strong>{analysis_info['type']}</strong></div>
            <div class="info-item">📅 تاريخ الإنشاء: <strong>{analysis_info['created_date']}</strong></div>
            {"<div class='info-item'>📁 الملف: <strong>" + str(analysis_info['file_name']) + "</strong></div>" if analysis_info['file_name'] else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if analysis_info['description']:
        st.markdown(f'<div style="background:#f8f9fa;padding:15px;border-radius:15px;margin-bottom:20px;border-right:4px solid #667eea;"><strong>📝 الوصف:</strong> {analysis_info["description"]}</div>', unsafe_allow_html=True)
    
    df_products = get_product_analyses(analysis_id)
    
    if df_products.empty:
        st.info("📭 لا توجد تحليلات مرتبطة")
        if st.button("🔙 العودة للقائمة الرئيسية", use_container_width=True): st.switch_page("app.py")
        return
    
    # ✅ ملاحظة الجودة
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
    
    # المؤشرات الإجمالية
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 المؤشرات الإجمالية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        total_comments = df_products['number_of_comments'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💬</div>
            <div class="metric-label">إجمالي التعليقات</div>
            <div class="metric-value">{total_comments:,}</div>
            <div class="metric-subtitle">تعليق محلل</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_positive = df_products['positive_percentage'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">😊</div>
            <div class="metric-label">متوسط الإيجابية</div>
            <div class="metric-value">{avg_positive:.1f}%</div>
            <div class="metric-subtitle">نسبة عامة</div>
        </div>
        """, unsafe_allow_html=True)
    
    # عرض الشهور
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📋 التحليلات الشهرية")
    
    for idx, row in df_products.iterrows():
        st.markdown(f'<div class="simple-month">📌 {row["analysis_month"]}</div>', unsafe_allow_html=True)
        
        # ✅ تحذير إذا كان عدد التعليقات أقل من الموصى به
        if row['number_of_comments'] < RECOMMENDED_COMMENTS:
            st.warning(f"⚠️ عدد التعليقات ({row['number_of_comments']}) أقل من الموصى به ({RECOMMENDED_COMMENTS})")
        
        sentiment_chart = create_sentiment_bar(row['positive_percentage'], row['negative_percentage'])
        st.plotly_chart(sentiment_chart, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if st.button("🔙 العودة إلى القائمة الرئيسية", use_container_width=True):
        if "hide_quality_note" in st.session_state:
          del st.session_state.hide_quality_note
        st.switch_page("app.py")

if __name__ == "__main__":
    main()
