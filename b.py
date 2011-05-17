#!/usr/bin/python
# -*- coding: utf-8 -*-
import bngram
import operator
from multiprocessing import Process, Queue

sten=["就是不想再提起這碗害他下台的蕃薯粥","什麼？你在等 Palm Pre，那你要留意囉！","指揮中心公布新流感疫苗接種順序 災民優先","現在救災第一，不滿情緒應等到救災告一段落再溝通。"]


q = Queue()
def bn_query(q,strin):
    dic=bngram.wordspliting(strin,'sd')
    dic.run()
    q.put((dic.dicword,dic.companword,dic.ascword,dic.gramword))

for st in sten:
    p=Process(target=bn_query, args=(q,st,))
    p.start()

while(p.is_alive()):
    p.join(1)

for x in range(len(sten)):
    for y in q.get():
        for z in y:
            a,b,c=z
            print a,b,c,

"""
text=unicode(sten, "utf-8")
a=bngram.wordspliting(sten,'sd')
print a.run()
print len(a.dicword)
print len(a.companword)
"""

