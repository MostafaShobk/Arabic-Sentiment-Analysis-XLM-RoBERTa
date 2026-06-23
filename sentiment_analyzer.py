

 ###############################################################
#                                                               #
#                                                               #
#                    Abdalrhman Alquaary                        #
#  https://www.linkedin.com/in/abdalrhman-alquaary-2aa5a5233/   #
#                                                               #
#                                                               #
#                                                               #
#                                                               #
 ###############################################################





import pandas as pd
import numpy as np
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from transformers import pipeline
from scipy.special import softmax
import torch
from torch import nn  
from tqdm import tqdm
from utils.data_pipeline import *
import yaml
import os

class Sentiment_Analyzer:
    def __init__(self, df, cleaned_text = None) -> None:
        
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)

        self.df = df
        self.cleaned_text = cleaned_text
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"


        # Initialize Models 
        
        self.camel_bert_ar_tok = None
        self.camel_bert_ar_model = None


        self.cardiffnlp_en_tok = None
        self.cardiffnlp_en_model = None
    

        self.cardiffnlp_multi_tok = None
        self.cardiffnlp_multi_model = None


    def camel_bert_ar_analyze(self, data) -> None:

        if self.camel_bert_ar_tok is None or self.camel_bert_ar_model is None:

            camel_bert_ar_hf_path = f"CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment"
            camel_bert_ar_local_path = './models/' + camel_bert_ar_hf_path.split('/')[-1]
            self.camel_bert_ar_tok = AutoTokenizer.from_pretrained(camel_bert_ar_hf_path, cache_dir=camel_bert_ar_local_path)
            self.camel_bert_ar_model = AutoModelForSequenceClassification.from_pretrained(camel_bert_ar_hf_path, cache_dir=camel_bert_ar_local_path)

        labels = ['positive', 'negative', 'neutral']
        encoded_input = self.camel_bert_ar_tok(data, return_tensors='pt').to(self.device)
        self.camel_bert_ar_model = self.camel_bert_ar_model.to(self.device)
        output = self.camel_bert_ar_model(**encoded_input)
        scores = output[0][0].cpu().detach().numpy()
        scores = softmax(scores)
        
        s = scores.tolist()
        max_index = s.index(max(s))
        sentiment = labels[max_index]
        return sentiment

    def cardiffnlp_en_analyze(self, data) -> None:

        if self.cardiffnlp_en_tok is None or self.cardiffnlp_en_model is None:
            cardiffnlp_en_hf_path = f"cardiffnlp/twitter-roberta-base-sentiment" # modify the path
            cardiffnlp_en_local_path =  './models/' + cardiffnlp_en_hf_path.split('/')[-1]
            self.cardiffnlp_en_tok = AutoTokenizer.from_pretrained(cardiffnlp_en_hf_path, cache_dir=cardiffnlp_en_local_path)
            self.cardiffnlp_en_model = AutoModelForSequenceClassification.from_pretrained(cardiffnlp_en_hf_path, cache_dir=cardiffnlp_en_local_path)

        labels = ['negative', 'neutral', 'positive']
        encoded_input = self.cardiffnlp_en_tok(data, return_tensors='pt').to(self.device)
        self.cardiffnlp_en_model = self.cardiffnlp_en_model.to(self.device)
        output = self.cardiffnlp_en_model(**encoded_input)
        scores = output[0][0].cpu().detach().numpy()
        scores = softmax(scores)
        
        s = scores.tolist()
        max_index = s.index(max(s))
        sentiment = labels[max_index]
        return sentiment



    def cardiffnlp_multi_analyze(self, data) -> None:

        if self.cardiffnlp_multi_tok is None or self.cardiffnlp_multi_model is None:
        # ✅ المسار المحلي الصحيح
            local_path = './models/twitter-xlm-roberta-base-sentiment'
        
            print("📦 تحميل النموذج من الملفات المحلية...")
        
        # ✅ تحميل من الملفات المحلية فقط - بدون إنترنت
            self.cardiffnlp_multi_tok = AutoTokenizer.from_pretrained(
            local_path,
            local_files_only=True
        )
            self.cardiffnlp_multi_model = AutoModelForSequenceClassification.from_pretrained(
            local_path,
            local_files_only=True,
            use_safetensors=False
        )
            self.cardiffnlp_multi_model = self.cardiffnlp_multi_model.to(self.device)
            print("✅ تم تحميل النموذج محلياً!")

        labels = ['negative', 'neutral', 'positive']
        encoded_input = self.cardiffnlp_multi_tok(data, return_tensors='pt').to(self.device)
    
        with torch.no_grad():
            output = self.cardiffnlp_multi_model(**encoded_input)
    
        scores = output.logits[0].cpu().detach().numpy()
        scores = softmax(scores)
    
        s = scores.tolist()
        max_index = s.index(max(s))
        sentiment = labels[max_index]
        return sentiment


    def get_sentiments(self):
        
        name_function_map = {
            'CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment': self.camel_bert_ar_analyze,
            'cardiffnlp/twitter-roberta-base-sentiment': self.cardiffnlp_en_analyze,
            'cardiffnlp/twitter-xlm-roberta-base-sentiment': self.cardiffnlp_multi_analyze
        }
        
        output_sentiments = []
        analyzing_model = name_function_map[self.config['analyzing_model']]

        for i in tqdm(range(len(self.df))):
            text = self.df[i]
            try:
                predict = analyzing_model(text)
            except:
                text = text[:500]
                predict = analyzing_model(text)
            output_sentiments.append(predict)
            
        total = len(output_sentiments)
        positive_count = output_sentiments.count('positive')
        negative_count = output_sentiments.count('negative')
        neutral_count = output_sentiments.count('neutral')
        
        positive_percentage = round((positive_count / total) * 100, 2) if total > 0 else 0
        negative_percentage = round((negative_count / total) * 100, 2) if total > 0 else 0
        neutral_percentage = round((neutral_count / total) * 100, 2) if total > 0 else 0
        
        
        
        if self.config['clean_data']: 

            text_sentiment = {
                'Text': self.df,
                'Cleaned_Text': self.cleaned_text,
                'Sentiments': output_sentiments
            }
        else:
            text_sentiment = {
                'Text': self.df,
                'Sentiments': output_sentiments
            }
    

        current_path = os.getcwd()
        full_output_path = os.path.join(current_path, "output")
        os.makedirs(full_output_path, exist_ok=True)

        output_df = pd.DataFrame(text_sentiment)
        writer = pd.ExcelWriter("output/sentiment_text" + '.xlsx', engine='xlsxwriter', engine_kwargs={'options':{'strings_to_urls': False}})
        output_df.to_excel(writer, index=False)
        writer.close()
        return total,positive_percentage,negative_percentage
        print(f"Positive: {positive_count} ({positive_percentage}%)")
        print(f"Negative: {negative_count} ({negative_percentage}%)")
        print(f"Neutral: {neutral_count} ({neutral_percentage}%)")


    
