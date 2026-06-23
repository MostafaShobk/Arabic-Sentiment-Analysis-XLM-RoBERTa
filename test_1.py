
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
from sentiment_analyzer import Sentiment_Analyzer
from utils.data_pipeline import Data_Pipeline



def main():

	data, cleaned_data = Data_Pipeline.fetch_data()

	sa = Sentiment_Analyzer(data, cleaned_data)
	sa.get_sentiments()


if __name__ == '__main__':
	main()
	print("Done")


