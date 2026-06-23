
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


from sentiment_analyzer import Sentiment_Analyzer

def main():

	texts = [

		'You have a good heart',
		"he didn't seem very well"
	]

	sa = Sentiment_Analyzer(texts)
	sa.get_sentiments()

if __name__ == '__main__':
	main()


