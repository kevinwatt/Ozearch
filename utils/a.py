#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
import bngram
import porterstemming

p=porterstemming.PorterStemmer()
p.stem('computer',0,len('computer')-1)
#test=bngram.wordspliting('whatever','any')
#test.context=unicode('演講的目的',"utf-8")
#test.context=unicode('請賣給我一開機就可以用的電腦!',"utf-8")
#test.context=unicode('阿爾卑斯山的少女, balala.. balala lala lala bababa. 英文法',"utf-8")
test.context=unicode('Linux作業系統二元樹(btree), 法務部門和服務部門 花蓮縣政府ab"cd eq./sasa',"utf-8")
#test.context=unicode('CNN.com delivers the latest breaking news and information on the latest top stories',"utf-8")
#test.context=unicode('abc',"utf-8")
#test.context=unicode('現在另外一個佔有主導地位的科技公司也開始受到質疑。一種前所未有的共同陣線於焉形成：曾經是反壟斷被告的微軟和AT&T，竟與消費者保護組織聯手，將矛頭對準Google主導........abc..a.s.d.',"utf-8")

test.text=test.word_split()
print test.text

def margecount(matchcx):
    lx=matchcx[0][0]
    ly=matchcx[len(matchcx)-1][1]
    return (lx,ly)

test.xsplit=test.markdicword()

print test.xsplit
for x in test.xsplit:
	lexp=[]
	for (w,p) in test.text[x[0]:(x[1]+x[0])]:
		lexp.append(p)
	start,end=margecount(lexp)
	#print test.context[start:end],start,end

d,b = test.letwordtodef()

for x in d:
	print x[0]
for x in b:
	print x[0]

