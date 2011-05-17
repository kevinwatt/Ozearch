#!/usr/bin/env python
import cPickle,string

markworddic="dic/markword.pick"
word="markword"
dumpdic=open(markworddic,'a')
mfile=open("markword",'r')
#print mfile.readlines()
dicindex={}
for charlist in mfile.readlines():
    if charlist and charlist[0]!="#":
        sechar=[]
    	tempdi=string.split(charlist[:-1],':')
	#print tempdi[0],string.split(tempdi[1],chr(32))
	for x in string.split(tempdi[1],chr(32)):
		if x:
		      sechar.append(x)
	dicindex[tempdi[0]]=sechar

print "Insert list:"
for x in dicindex.keys():
	print '{'+x+'}:',
	for tempdi in dicindex[x]:
		print tempdi,
	print "\n",

cPickle.dump(dicindex,dumpdic)

