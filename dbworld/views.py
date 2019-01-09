from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse as HR
from .models import Doc,Wordindex

from .getData import indexing
from .process import process,stopWords

from math import log10



keys = ['sendTime','begin','deadline','sender','subject']
docs = [d.__dict__ for d in Doc.objects.all()]
return_dic = {'info':'','keys':keys,'docs':docs}


'''response  functions'''
def index(request):
    return_dic['docs'] = docs
    return_dic['info']=''
    return render(request,'dbworld/index.html',return_dic)

def sortData(request,key):
    return_dic['docs'] = sorted(return_dic['docs'],key=lambda dic:dic[key])
    return render(request,'dbworld/index.html',return_dic)



def update(request):
    n = indexing()
    return_dic['docs']=  [d.__dict__ for d in Doc.objects.all()]
    return_dic['info'] = ': {} documents'.format(n)
    return render(request,'dbworld/index.html',return_dic)

def search(request):
    words = request.POST['search']
    return_dic['docs']= tfidf(words)
    return render(request,'dbworld/index.html',return_dic)



''' utils functions'''

def tfidf(words):
    if not words:return docs
    ct = process(words)
    weight = {}
    tf = {}
    for term in ct:
        try:
            tf[term] = Wordindex.objects.get(word=term).index
        except Exception as e:
            print(e)
            tf[term]={}
            continue
        for docid in tf[term]:
            if docid not in weight:
                weight[docid]=0
    N = len(weight)
    for term in ct:
        dic = tf[term]
        for docid, freq in dic.items():
            w = (1+log10(freq))*(log10(N/len(dic)))*ct[term]
            if term in stopWords:
                w*=0.3
            weight[docid]+=w
    ids = sorted(weight,key = lambda k:weight[k],reverse=True)
    if len(ids)<8: pass #???
    return [Doc.objects.get(id=int(i)).__dict__ for i in ids]

