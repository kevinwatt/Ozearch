#!/usr/bin/env python
import time,sys
import urllib
import xmlrpclib

ST=time.time()
if len(sys.argv) == 1:
	pass
else:
   if sys.argv[1:]:
   	arglist=sys.argv[1:]
   	getargv=arglist[0]
	if arglist[0] in ('-q','--query') and len(arglist)>1:
		from query import QueryObj
		from lang import langconvert
		a=langconvert(arglist[1],None)
		uni = unicode(a,"utf-8")
		query=QueryObj()
		query.dbinit()
		query.uni=uni.encode("utf-8")
		query.udngram()
		rasize,ralist=query.query()
		i=0
		for x in ralist:
			print i,urllib.unquote(x[2]), urllib.unquote(x[3]), x[4]
			print x[1], urllib.unquote(x[0])
			print x[5], x[6],rasize
			i+=1
		query.dbclose()

	if arglist[0] in ('-sq','--socketquery') and len(arglist)>1:
		s = xmlrpclib.Server('http://127.0.0.1:4443/')
		a=arglist[1]
		uni = unicode(a,"utf-8")
		rasize,ralist=s.echo(uni,20,0)
		i=0
		for x in ralist:
			print i,urllib.unquote(x[2]), urllib.unquote(x[3]), x[4]
			print x[1], urllib.unquote(x[0])
			print x[5], x[6],rasize
			i+=1
print time.time()-ST

