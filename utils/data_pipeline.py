

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
from openpyxl import load_workbook
import re
import pyarabic.araby as araby
import time
import os
import yaml


class Data_Pipeline:
    
    @staticmethod
    def fetch_data():
        
        cleaned_data = None
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        file_path = config['file']['path']
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No file found at {file_path}")
        # Start time
        start_time = time.time()
        if file_path.endswith('.xlsx'):
            df =  pd.read_excel(file_path)[config['file']['columnName']]
        elif file_path.endswith('.csv'):
            df =  pd.read_csv(file_path)[config['file']['columnName']]
        # End time
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken to read the file: {elapsed_time:.4f} seconds")        
        if config['clean_data']:
            cleaned_data = Data_Pipeline.clean_data(df.copy())
        return df, cleaned_data
    


    @staticmethod
    def remove_user_names(text):
        new_text = []
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            new_text.append(t)
        return " ".join(new_text)
    
    @staticmethod
    def clean_data(df):
        
        for i in range(len(df)):
            x = str(df[i])
            x = araby.strip_diacritics(x)
            x = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", x)
            x = re.sub('[\[\]\{\}\-\(\)\!\?\؟\:\،\.\”\“\|\"\•]', ' ', x) # check it with - ## important
            x = re.sub('\[.*?\]',' ', x)
            x = x.replace("#", " ").replace(".", " ").replace('\n',' ')
            x = Data_Pipeline.remove_user_names(x)
            x = x.lower()
            x = re.sub(' +', ' ', x)

            df[i] = x
        return df