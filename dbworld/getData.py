# coding:utf8
import re
import os
import datetime
import requests
from bs4 import BeautifulSoup as bs

from .models import Wordindex,Doc,File
from .process import process

#from .summarize import summarize as mysumma

from summa.summarizer import summarize
from summa.keywords import keywords

URL = "https://research.cs.wisc.edu/dbworld/browse.html"

months={'Jan':1,'Feb':2,'Mar':3,'Apr':4,
     'May':5,'Jun':6,'Jul':7,'Aug':8,
     'Sep':9,'Oct':10,'Nov':11,'Dec':12}

def str2date(dateStr):
    d,m,y = dateStr.split('-')
    return datetime.date(int(y),months[m],int(d)) #strptime

def crawl():
    r = requests.get(URL)
    if r.status_code !=200:
        print('[Error] internet error, got status_code:',r.status_code)
        return
    cols =['sendTime','messageType','sender','subject','deadline','subjectUrl','webpageUrl']
    obj =bs(r.text,'html5lib') #weird, the origin format is html. lxml, html parse have bugs and they won't find all
    for tbody in obj.findAll('tbody'):
        tds = tbody.findAll('td')
        li = [td.text.strip() for td in tds[:-1]]
        try:
            li.append( tds[3].a.attrs['href']) #subject url
        except Exception as e:
            print(e)
            print(tds)
            continue
        webpageUrl = li[-1] if tds[-1].a is  None else   tds[-1].a.attrs['href']
        li.append(webpageUrl)
        dic = dict(zip(cols,li))
        yield dic
    '''
    cols =['sendTime','messageType','sender','subjectUrl','subject','deadline','webpageUrl']
    pt = re.compile(r'\<TBODY\>\s*\<TR VALIGN=TOP\>\s*\<TD\>(?P<sent>\d\d-[A-Z][a-z][a-z]-\d{4})\s*\</TD\>\s*\<TD\>(?P<messageType>.*?)\</TD\>\s*\<TD\>(?P<sender>.*?)\</TD\>\s*\<TD\>\<A HREF\=\"(?P<subjectUrl>.*?)\".*?\>(?P<subject>.*?)\</A\>\s*\</TD\>\s*\<TD\>(?P<deadline>\d\d-[A-Z][a-z][a-z]-\d{4})\s*\</TD\>\s*\<TD\>(?P<webpageUrl>\s+|\<A.*?HREF\=\"(.*?)\"\>web page\</A\>)\</TD\>\s*\</TR\>\</TBODY\>')
    #urlpt = re.compile(r'HREF=\"(?P<url>.*?)\"')
    for tp in pt.findall(r.text):
        li = list(tp[:-2])
        li.append(tp[-1])
        dic = dict(zip(cols,li))
        yield dic
    '''

def genDoc():
    visited = set([d.subjectUrl for d in Doc.objects.all()])
    for dic in crawl():
        if dic['subjectUrl'] in visited:continue
        dic['sendTime'] =  str2date(dic['sendTime'])
        dic['begin'] =  dic['sendTime']
        if dic['deadline']:dic['deadline'] =  str2date(dic['deadline'])
        else:dic['deadline'] = datetime.date(2019,3,1)
        dic['desc'] = dic['loc']= dic['keywords']=''
        d = Doc.objects.create(**dic)
        File.objects.create(doc=d,content='')

locs = ['Albania', 'Congo', 'Algeria', 'Denmark', 'Angola', 'Dominican', 'Anguilla', 'Dominica','Argentina', 'Ecuador', 'Armenia', 'Egypt', 'Aruba', 'El Salvador', 'Australia', 'Eritrea', 'Austria', 'Estonia', 'Azerbaijan', 'Ethiopia', 'Bahamas', 'Fiji', 'Bahrain', 'Finland', 'Bangladesh', 'France', 'Barbados', 'Gabon', 'Belarus', 'Georgia', 'Belgium', 'Germany', 'Belize', 'Ghana', 'Benin', 'Gibraltar', 'Bermuda', 'United Kingdom of Great Britain and Northern Ireland', 'Bhutan', 'Greece', 'Bolivia', 'Grenada', 'Bosnia','Herzegovina', 'Guatemala', 'Botswana', 'Guinea', 'Brazil', 'Guyana', 'Brunei Darussalam', 'Haiti', 'Bulgaria', 'Honduras', 'Burkina Faso',  'Burundi', 'Hungary', 'Cambodia', 'Iceland', 'Cameroon', 'India', 'Canada', 'Indonesia', 'Cape Verde', 'Iran', 'Cayman Islands', 'Iraq', 'Central African', 'Ireland', 'Chad', 'Israel', 'Chile', 'Italy', 'China', 'Jamaica', 'Colombia', 'Japan', 'Congo', 'Jordan', 'Cook Islands', 'Kenya', 'Costa Rica', 'Korea','Ivoire', 'Kuwait', 'Croatia', 'Lao People', 'Cyprus', 'Latvia', 'Czech', 'Lesotho', 'Luxembourg', 'Saint Lucia', 'Macao', 'Macedonia', 'Sao Tome and Principe', 'Madagascar', 'Saudi Arabia', 'Malawi', 'Senegal', 'Malaysia', 'Seychelles', 'Maldives', 'Sierra Leone', 'Mali', 'Singapore', 'Malta', 'Slovakia', 'Mauritius', 'Slovenia', 'Mauritania', 'Solomon Islands', 'Mexico', 'Somalia', 'Moldova', 'South Africa', 'Mongolia', 'Spain', 'Morocco', 'Sri Lanka', 'Myanmar', 'Sudan', 'Namibia', 'Suriname', 'Nauru', 'Swaziland', 'Nepal', 'Sweden', 'Netherlands', 'Switzerland', 'New Caledonia', 'Syrian', 'New Zealand', 'Tanzania', 'Niger', 'Thailand', 'Nigeria', 'Togo', 'Norway',  'Oman', 'Tunisia', 'Pakistan', 'Turkey', 'Panama', 'Uganda','Ukraine', 'Paraguay', 'United Arab Emirates', 'Peru', 'United States of America', 'Philippines', 'Uruguay', 'Poland', 'Venezuela', 'Portugal', 'Viet Nam', 'Qatar', 'Western Samoa', 'Romania', 'Yemen', 'Russia', 'Yugoslavia', 'Rwanda', 'Zambia', 'Saint Christopher', 'Kitts', 'Nevis', 'Zimbabwe','USA','UK','Europe','Asia','U.S.A','University','School']

loc_pt = re.compile(r'([A-Z][a-zA-Z]+[, ]+){0,3}('+'|'.join(locs)+')')
def getLoc(text):
    s = loc_pt.search(text)
    return s.group(0) if s else 'Earth'  # (x_x)

abbr = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
month_pt ='('+abbr+'[a-z]*)'
day_pt = r'(\d{1,2}(th){0,1}(-\d{1,2}(th|nd|st|rd){0,1}){0,1})'
sep_pt = r'([ \.,]+)'
dates = [[month_pt,sep_pt,day_pt,sep_pt,'(201[89])'],[day_pt,sep_pt,month_pt,sep_pt,'(201[89])']]
dates = [''.join(i) for i in dates]
dates+=[r'(\d{1,2}-'+abbr+'-201[89])',abbr+r'-\d{1,2}-201[89]',r'(201[89]-'+abbr+'-\d{1,2})']

date_pt = re.compile('|'.join(dates))
def setDate(doc):
    text =doc.file.content
    s = date_pt.search(text)
    if s:
        s = re.sub('\.|,| |th|nd|st|rd','-',s.group(0))
        s = re.sub('-+','-',s)
        li = s.split('-')
        y,m,d = 2019,3,1
        if '2018' in li:
            y = 2018
            li.remove('2018')
        elif '2019' in li:
            li.remove('2019')
        try:
            for i in li:
                if i.isalpha():
                    m = months[i[:3]]
                    li.remove(i)
                    break
            if len(li)==2:
                doc.begin = datetime.date(y,m,int(li[0]))
                doc.deadline = datetime.date(y,m,int(li[1]))
            elif li:
                doc.begin = datetime.date(y,m,int(li[0]))
            if doc.begin>doc.deadline:
                doc.begin,doc.deadline = doc.deadline,doc.begin
            doc.save()
        except Exception as e:
            print(e)



d = {'_v':"|",'_r':'>','_l':'<','_y':'\"','_q':'?','_x':'*','_c':':','_d':'/','_s':'  ','_b':'_'}
li = ['_v','_r','_l','_y','_q','_x','_c','_d','_s','_b']
def nameUrl(name):
    for i in li:
        name = name.replace(i,d[i])
    return name
def urlName(url):
    for i in li:
        url = url.replace(d[i],i)
    return url

cached =set(os.listdir('dbworld/raw') )
def setContent(fi):
    if not fi.content:
        d = fi.doc
        name = urlName(d.subjectUrl)
        text = ''
        if name in cached:
            with open('dbworld/raw/'+name,encoding ='utf-8',errors='ignore') as f:
                text = f.read()
        else:
            try:
                text = requests.get(d.subjectUrl).text
                with open('dbworld/raw/'+name,'w',encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                print(e)
                print('[Error]: subject',d.subjectUrl)
        if not text:raise Exception('[Error]: get no content for {}'.format(d.subjectUrl))
        b = bs(text,'html5lib')
        fi.content= b.body.text
        fi.save()

def indexing():
    genDoc()
    ct = 0
    for fi in File.objects.filter(isIndexed=False):
        try:
            setContent(fi)
        except:continue
        d = fi.doc
        if not d.desc: d.desc=summarize(fi.content,words=50)
        d.keywords = keywords(fi.content,words=5)
        setDate(d)
        d.loc = getLoc(fi.content)
        words = process(fi.content)
        for word, num in words.items():
            idx = None
            li = Wordindex.objects.filter(word=word)
            if li.exists():
                idx = li[0]
            else:
                idx = Wordindex.objects.create(word=word,index={})
            saved = idx.index # Warning:  'idx.index[d.id] = num'  is wrong
            saved[d.id] = num
            idx.index = saved
            idx.save()
        d.save()
        fi.isIndexed = True
        fi.save()
        if ct%20==0:print(ct)
        ct+=1
    return ct
