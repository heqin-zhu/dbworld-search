![](images/dbworld.png)

# 搜索引擎实现
使用 Django-2.1.3, python3.6 实现的一个非常非常 naive 的搜索引擎.

我初学 django, 写得并不熟练, 所以此代码仅供参考.
## 需要
- 编程语言: python3
- 运行环境: linux, shell
- 使用工具:
    - Django-2.1.3
    - python3.6
        - summa (text-rank)
        - dj-pagination
        - BeautifulSoup

## 结果展示
- 首页
![](https://upload-images.jianshu.io/upload_images/7130568-09e5406d1ac7eaef.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

- 分页
![](https://upload-images.jianshu.io/upload_images/7130568-d82174d0f9e15cb4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


## 设计
### 设计数据结构
我们要保存一个倒排索引, 以及一个 主题对应的发送时间, 发送者, 主题, 主题链接等内容. 所以我设计了下面的数据库结构.

- Doc: 一个文件, 也就是一个网页, 包含一些主要信息.
- File: 外键是Doc, 包含了 网页文件的文本内容, 以及标记是否已经被索引(`isIndexed`)
- Wordindex: 这就是倒排索引中的一个项, 包含一个 term, 和倒排索引表,  倒排索引表设计成 hashtable 形式, 键为 Doc. id, 值为 在 Doc 中出现的次数. 为了简便,在数据库库中的存储形式是将上面的 hashtable (在 python 中 为 dict 类型) 用 json 格式保存为文本字符串形式.

需要注意的是增加一个键值对 **不能** 使用下面代码
```python
word.index [ doc.id] = num
word.save()
```
应该
```python
dic = word.index
dic[doc.id] = num
word.index = dic
word.save()
```

下面给出的是 django 中 model 的代码
```python
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
```
<a id="markdown-032-网页提取" name="032-网页提取"></a>
### 网页提取

![](https://upload-images.jianshu.io/upload_images/7130568-5a9807708ebd6746.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

首先是 [主页](https://research.cs.wisc.edu/dbworld/browse.html)
其结构是这样
```html
<TBODY>
<TR VALIGN=TOP>
<TD>03-Jan-2019 </TD>
<TD>conf. ann. </TD>
<TD>marta cimitile </TD>
<TD><A HREF="http://www.cs.wisc.edu/dbworld/messages/2019-01/1546520301.html" rel="nofollow">Call forFUZZ IEEE Special Session</A> </TD>
<TD>13-Jan-2019</TD>
<TD><A rel="nofollow" HREF="http://sites.ieee.org/fuzzieee-2019/special-sessions/">web page</A></TD>
</TR></TBODY>
```
有规律性, 可以直接提取. 在实现时, 我用的 python 的 BeautifulSoup 包来提取.

使用过程中, 关键是传递 解析器, 试过了 html, lxml 有问题, 最后用的 html5lib

然后是上面一行表格中的第四列(即第四个 td 标签), 其中的 `<a>`标签是 主题所在的网页链接. 也要进行提取

#### 提取时间, 地点
由于时间, 地点具有一般的模式,  可以列举出常见的模式, 使用正则表达式匹配
#### 提取摘要, 关键字
使用了 textrank 算法  
最开始我自己实现了一个很基础的 textrank 算法, 效果很差, 后来就使用了 text-rank 的官方版本.

### 建立索引
这部分就是按照 倒排索引的原理, 
将网页文本分词, 去除标点符号等,
然后使用上面介绍的数据库模型存储倒排索引.
<a id="markdown-034-设计网页" name="034-设计网页"></a>
### 设计网页
首先是标题
下面是一行是一排选项, 可以根据这些字段排序.
接着一行有一个 update 按钮, 一个搜索提交表格, 

下面的内容就是用 `div` 排列起来的搜索结果.

每个结果包含一个标题, 关键字, 时间,地点, 还有摘要.

### 查找排序
这里我自己实现了 `tf-idf`算法 来排序结果.
代码如下
```python
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
```
<a id="markdown-04-实验结果说明及演示" name="04-实验结果说明及演示"></a>
### 不足
1. 提取网页主题还需要改进, 提取地点方面, 有时可能提取不到.
2. 网页设计还可以更美观一点.
3. 还未对搜索引擎进行性能评估
