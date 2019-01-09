from collections import Counter as CT
from nltk import WordNetLemmatizer as WNL, PorterStemmer as PT
from nltk.tokenize import word_tokenize as TK
from nltk.corpus import stopwords as STOP
from string  import punctuation as punc

stopWords =set([i for i in  STOP.words()])

def tokenize(text):
    text = [' ' if i in punc else i for i in text]
    text = ''.join(text).lower()
    tks = TK(text)
    return tks
    #建立索引的时候不去除停用词, 在搜索排序的时候去除
    #return [w for w in tks if w and w not in stopWords]

def process(text):
    words = tokenize(text)
    stem = PT()
    words = [stem.stem(word) for word in words]
    #wnl = WNL()
    #words = [wnl.lemmatize(i) for i in words]
    return CT(words)

if __name__=='__main__':
    text = '''
I have the same error message , this is my code, can you help please: import nltk from nltk.corpus import names nltk.download('stopwords') nltk.download('wordnet') import warnings warnings.filterwarnings('ignore') from nltk.corpus import stopwords def cleaning(article): one = "".join([i for i in article.lower().split() if i not in stopwords]) two = "".join(i for i in one if i not in punctuation) three = "".join(lemmatize.lemmatize(i) for i in two.split()) return three text = Search.applymap(cleaning)['Q2'] text_list = [i.split() for i in text]
	'''
    while 1:
        print(process(text))
        text = input('>> ')
