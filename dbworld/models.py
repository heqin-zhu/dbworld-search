from django.db import models
class Doc(models.Model):
    sendTime= models.DateField() # 2018-12-12 ,  differ from DateTimeField which can be datetime or date
    sender = models.CharField(max_length=20)
    messageType = models.CharField(max_length = 20) # Journal, conf, et al
    subject = models.CharField(max_length=100)
    begin= models.DateField()
    deadline= models.DateField()
    subjectUrl= models.CharField(max_length=100)
    webpageUrl= models.CharField(max_length=100)
    desc = models.CharField(max_length= 250,default='')
    loc = models.CharField(max_length=40,default='')
    keywords = models.CharField(max_length=200,default='')

    def __str__(self):
        return self.subjectUrl

import json
class Wordindex(models.Model):
    word= models.CharField(max_length=45)

    # model to store a list, another way is to create a custom field
    _index = models.TextField(null=True)
    @property
    def index(self):
        return json.loads(self._index)
    @index.setter
    def index(self,li):
        self._index = json.dumps(li)
    def __str__(self):
        return self.word
class File(models.Model):
    doc = models.OneToOneField(Doc,on_delete=models.CASCADE)
    content = models.TextField(null=True)
    isIndexed = models.BooleanField(default=False)
    def __str__(self):
        return 'file: {} -> doc: {}'.format(self.id,self.doc.id)

'''
class Word(models.Model):
    word = models.CharField(max_length=45) # english word
    def __str__(self):
        return self.word
class Info(models.Model):
    position = models.IntegerField(default=0)
    doc = models.ForeignKey(Doc,on_delete=models.CASCADE)
    word = models.ForeignKey(Word,on_delete=models.CASCADE)
    #word = models.ManyToManyField(Word)
'''
