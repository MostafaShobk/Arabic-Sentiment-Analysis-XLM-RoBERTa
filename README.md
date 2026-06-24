# 📊 Sentiment_Analyzer & Forecasting System

Sentiment Analyzer is a powerful, end-to-end engineered system designed for deep sentiment analysis and predictive trend forecasting on customer data, social media content, and time-series data. It features an interactive analytical dashboard and automated official report generation tailored for decision-makers.

---
▶️ **[شاهد فيديو استعراض النظام على إنستغرام | Watch the Demo Video on Instagram](https://www.instagram.com/reel/DZ99zrQtpMi/?igsh=N2RsMmt4MTdtdHRv)

---
## 🚀 Key Implementation Features
* **Unified Python Ecosystem:** Seamlessly integrates Deep Learning backend frameworks with analytical capabilities.
* **Multilingual AI Backed:** Driven by state-of-the-art architectures (**XLM-RoBERTa**, CAMeL-BERT) optimizing cross-lingual contextual understanding for mixed Arabic/English social media dialects.
* **Predictive Analytical Core:** Implements a Built-in Linear Regression mathematical module ($y = mx + c$) to compute satisfaction trendlines and forecast future monthly metrics.
* **Automated Word Reporting:** Features a standalone automation engine (`python-docx`) that dynamically compiles analytical outputs, charts, and forecasts into standard operational Microsoft Word documents.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/engmostafashobak-png/Arabic-Sentiment-Analysis-XLM-RoBERTa.git](https://github.com/engmostafashobak-png/Arabic-Sentiment-Analysis-XLM-RoBERTa.git)
   cd Arabic-Sentiment-Analysis-XLM-RoBERTa
   pip install -r requirements.txt
   pip install -r requirements.txt
   # analyzing_model: CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment 
# analyzing_model: cardiffnlp/twitter-roberta-base-sentiment 
analyzing_model: cardiffnlp/twitter-xlm-roberta-base-sentiment
streamlit run app.py
python test_1.py
from sentiment_analyzer import Sentiment_Analyzer

texts = ['اليوم كانت الخدمة ممتازة جداً ومثالية', "he didn't seem very well"]
sa = Sentiment_Analyzer(texts)
sa.get_sentiments()
