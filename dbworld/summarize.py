#coding: utf-8
''' mbinary
#######################################################################
# File : summarize.py
# Author: mbinary
# Mail: zhuheqin1@gmail.com
# Blog: https://mbinary.coding.me
# Github: https://github.com/mbinary
# Created Time: 2018-12-31  20:33
# Description: 
    Inspired by PageRank alogorithm, this algorithm can summarize an article by extracting a sentence.
#######################################################################
'''
#from . import process
import process
from math import log,fabs
from itertools import product
from heapq import nlargest

import re
sent_pt = re.compile(r'[-\'\"\w\., ]+')

def similarity(sent1,sent2):
    '''calculate the similarity of two sentences'''
    s = log(len(sent1))+log(len(sent2))
    return  len(set(sent1).intersection(sent2)) / s if s!=0 else 0

def textRank(weights):
    n = len(weights)
    score = [0.5 for i in range(n)]
    old_score  = [0 for i in range(n)]
    while all(fabs(i-j)>=0.001 for i,j in zip(score,old_score)):
        old_score = score
        score = [updateScore(weights,i,old_score) for i in range(n)]
    return score

def updateScore(weights,i,score):
    n = len(weights)
    d = 0.85
    inc = 0
    for j in range(n):
        s = sum(weights[j])
        if s!=0:inc += (weights[j][i]*score[j])/s
    return (1-d)+d*inc

def summarize(text,n=4):
    sents = sent_pt.findall(text)
    wordSent = [process.tokenize(s) for s in sents]
    data = [(i,process.process(j)) for i,j in zip(sents,wordSent) if len(j)>1]
    num = len(data)
    weights = [[0]*num for i in range(num)]
    for i,j in product(range(num),repeat=2):
        if i!=j:
            weights[i][j] = similarity(data[i][1],data[j][1])
    score = textRank(weights)
    dic = {data[i][0]:score[i] for i in range(num)}
    return '\n'.join(i for  i in nlargest(n,dic))


if __name__=='__main__':
    text = '''
Middle-aged people in England face a health crisis because of unhealthy lifestyles, experts have warned.

Desk jobs, fast food and the daily grind are taking their toll, says Public Health England.

Eight in every 10 people aged 40 to 60 in England are overweight, drink too much or get too little exercise, the government body warns.

PHE wants people to turn over a new leaf in 2017 and make a pledge to get fit.

Health officials say the "sandwich generation" of people caring for children and ageing parents do not take enough time to look after themselves.

Exercises you can do at your desk
Do fitness apps actually work?
We are living longer, but are in poorer health because we store up problems as we age.

The campaign's clinical adviser, Prof Muir Gray, said it was about trying to make people have a different attitude to an"environmental problem".

"Modern life is dramatically different to even 30 years ago," Prof Gray told Radio 4's Today programme."People now drive to work and sit at work."

"By taking action in mid-life... you can reduce your risk not only of type 2 diabetes, which is a preventable condition, but you can also reduce your risk of dementia and disability and, being a burden to your family," he added.

Many people no longer recognise what a healthy body weight looks like, say the officials - and obesity, which greatly increases the risk of type 2 diabetes, is increasingly considered normal.

The PHE website and app has a quiz that gives users a health score based on their lifestyle habits by asking questions such as, "Which snacks do you eat in a normal day?" and "How much exercise do you get every day?"

Wake up call
The questions are simple, but the results are revealing, says Prof Kevin Fenton, director of Health and Wellbeing at PHE.

"The How Are You Quiz will help anyone who wants to take a few minutes to take stock and find out quickly where they can take a little action to make a big difference to their health."

Speaking to BBC Breakfast, Dr Ellie Cannon said PHE recognised that the "sandwich generation" was "incredibly busy".

"This is about making small changes that can have this really big improvement for your long-term health," she added.

"People want this, people want the help... it is not encouraging people to take on board anything expensive or anything complicated."


Media playback is unsupported on your device
Media captionLee Parker used to weigh more than 22 stone
More than a million people have taken the quiz so far.

One of them is Lee Parker, who is 41 and from Bolton. He did the quiz in March before starting a diet in August.

He says it was his son who provided a much-needed wake-up call. Lee's son, who is now eight, told him he loved him"even though you are fat".

This was the final nudge that Lee says he needed.

Weighing more than 22 stone, Lee started to diet and exercise and lost just over five stone in 16 weeks.

His partner has joined in and has lost two and a half stone.

In April 2017, Lee will be taking part in the Manchester marathon. He says: "You can become very complacent when you are in your forties. You kind of think you've done everything and so you can relax and eat pizzas and Chinese in the week.

"I've still got another stone to go to my target weight. It's been very, very difficult.

"I'm missing all the cakes and the crisps and the biscuits.... I still have them, I still enjoy them, but I know when to say no and I know how much I've had."

Another quiz participant, Penny Henderson, says her bad habits "slowly crept up" on her with how much she was drinking and that she was not really exercising.

"When I took the test, I actually was not that honest and I kind of lied... I think I just did not say exactly how much I was drinking and that was quite a wake up call.

"I realised if I was lying to myself then it must be bad," Ms Henderson told Breakfast.

After cutting down on alcohol, Ms Henderson said she had more time for things, was less stressed, coped with work better and, that family life was more pleasant.

"The thing is to keep it always achievable and then you can keep it up," she added.

Healthier ageing
The NHS has a number of apps and websites that can help you make healthy changes:
    '''
    print(summarize(text))

