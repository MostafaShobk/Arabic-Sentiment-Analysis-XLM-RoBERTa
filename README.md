# Sentiment_Analyzer
 
Sentiment Analyzer is a powerful tool designed for users who need to perform sentiment analysis on customer data or social media content. It provides an easy-to-use interface for analyzing sentiments using state-of-the-art AI models for Arabic, English, and multilingual texts.

Scope
This project integrates three robust sentiment analysis models:

Arabic Model: Utilizes a specialized model trained for Arabic text sentiment analysis.
English Model: Uses a model optimized for sentiment analysis in English text.
Multilingual Model: Capable of analyzing sentiment in multiple languages, offering flexibility for diverse text sources.
These models are renowned for their accuracy and have been integrated into the project to simplify sentiment analysis tasks without requiring users to delve into complex AI implementations.

Installation
To get started with Sentiment Analyzer, follow these steps:

Clone the repository:

bash
```
git clone https://github.com/apoalquaary/Sentiment_Analyzer.git
cd sentiment-analyzer
```

Install dependencies:
```
pip install -r requirements.txt
```

# Configuration
Configure the config.yaml file to tailor the program to your needs:

<b>1- File Details:</b> Specify the path to your data file (excel_file_path or csv_file_path) and the name of the column containing text to analyze (text_column_name).

Example:

yaml
```
file:
  path: docs/microblogging.xlsx
  columnName: Text
```
  
<b>2- Data Cleaning:</b> Enable data cleaning (clean_data: 1) if your data requires preprocessing for social media text. Disable it (clean_data: 0) for other types of data.

<b>3- Model Selection:</b> Uncomment one of the models (arabic_model, english_model, multilingual_model) to specify which sentiment analysis model to use. The selected model will be automatically downloaded to the models/ folder.

Example:

yaml
Uncomment one of the following models:
```
# analyzing_model: CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment 
# analyzing_model: cardiffnlp/twitter-roberta-base-sentiment 
analyzing_model: cardiffnlp/twitter-xlm-roberta-base-sentiment 
```

Upon running the program, the output will be saved as an Excel file named sentiment_text.xlsx within a folder named output located in the same directory. This file will contain the original data along with the corresponding sentiments analyzed by the selected model (the cleaned data as well if the cleaned_data flag was on). Each row in the Excel file will display the input text alongside its sentiment classification, facilitating easy analysis and interpretation of sentiment trends across the dataset.

## Usage 1
Using File Input
Run the test_1.py script:
```
python test_1.py
```
This will read the Text Column from the file specified in the yaml (excel_file_path or csv_file_path) and analyze sentiments based on the chosen model.


## Using 2
Direct Input
```
python test_2.py
```
Prepare a list of texts:
Run the script (test_2.py) and provide a list of texts as input to the Sentiment Analyzer.

python
```
from sentiment_analyzer import Sentiment_Analyzer
from utils.data_pipeline import Data_Pipeline

def main():

	texts = [
		'You have a good heart',
		"he didn't seem very well"
	]

	sa = Sentiment_Analyzer(texts)
	sa.get_sentiments()

if __name__ == '__main__':
	main()
```

# Contributing
Contributions to Sentiment Analyzer are welcome!.

# License
This project is licensed under the MIT License.

