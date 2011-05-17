#!/usr/bin/env python
import time,sys
import re
import codecs
import bngram
from bsddb import db, dbutils
import ranking, contentprocess
import operator
import cPickle
from dba import Purecontent,DicQuery
from string import split
from lang import langconvert, punctuationmarks
import urllib
import zlib

class QueryObj(object):

    def __init__(self):
        self.uni=''
	self.pct=''
	self.page=0
	self.pagesize=10
	self.worddic={}
	self.wordlist=[]
	self.dq=DicQuery()

    def udngram(self):
	tail=[]
	getre=bngram.wordspliting(self.uni,"query")
	getre.start()
	getre.join()
	tail.append(getre)
	self.worddic, self.wordlist = self.dq.tailobject(tail)

    def dbinit(self):
	dbtype = db.DB_HASH
	dbopenflags = db.DB_THREAD
	envflags = db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK
	dbenv = db.DBEnv()
	dbenv.set_mp_mmapsize(50*1024*1024)
	dbenv.set_cachesize(0,100*1024*1024,0)
	homeDir='database/world'
	dbenv.open(homeDir, envflags | db.DB_CREATE)
	self.tempdb=db.DB(dbenv)
	self.tempdb.open('tempwdb.db', mode=0660, dbtype=db.DB_HASH, flags=dbopenflags|db.DB_CREATE)

        wdbenv = db.DBEnv()
        envflags= db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK
        wdbenv.set_mp_mmapsize(100*1024*1024)
        wdbenv.set_cachesize(0,200*1024*1024,0)
        homeDir='database/wpage/'
        wdbenv.open(homeDir, envflags|db.DB_CREATE)
        self.wpagedb=db.DB(wdbenv)
        self.wpagedb.open('wpagedb.db', None, db.DB_HASH, db.DB_DIRTY_READ)

	self.purei=Purecontent('r')
	self.serialdb=db.DB()
	self.serialdb.open('database/pureserial.db', None, db.DB_BTREE, db.DB_DIRTY_READ)
	self.urldb=db.DB()
	self.urldb.open('dic/anurl.db', None, db.DB_HASH, db.DB_DIRTY_READ)

    def dbclose(self):
	self.dq.dicclose()
	self.purei.close()
	self.urldb.close()
	self.tempdb.close()
	self.wpagedb.close()

    def wordmarkup(self,scorelist,startat):
        tempscorelist=[]
	at=scorelist[0][0]-startat
	for x in scorelist:
		start,end=x
		start=at+start-scorelist[0][0]
		end=at+end-scorelist[0][0]
		tempscorelist.append((start,end))
	return tempscorelist

    def uniques(self,wlist):
        u=[]
        for l in wlist:
                if l not in u and len(l)>0:
                        u.append(l)

        return u

    def dpickdump(self,picklist):
    	dpickstring=""
	for x in picklist:
	    if len(str(x[0]))<9:
	    	dpickstring=dpickstring+str(len(str(x[0])))+str(x[0])
	return dpickstring

    def dpickload(self,pick,wordsize):
        i=0
	b=[]
	while i<len(pick):
	    start=int(pick[1+i:1+i+int(pick[i])])
	    end=start+wordsize
	    b.append((start,end))
	    i=i+1+int(pick[i])
	return b

    def Stringload(self,UrlString):
        URLList={}
        for x in xrange(0,(len(UrlString)//6)):
	    URLList[UrlString[x*6:(1+x)*6]]=''
        return len(URLList),URLList

    def findpunctuation(self, pct, startat):
	until=0
	if startat > 20:
		until=20
	elif startat > 1:
		until=startat
	else:
		pass
	if until:
            for punctuationx in xrange(1,until):
	        if punctuationmarks(ord(pct[startat-punctuationx])):
	            startat=startat-punctuationx+1
	            break
	return startat

    def query(self):
	ST=time.time()
	conlinklist={}
	concountlist={}
	self.wordlist=self.uniques(self.wordlist)
	totalword=len(self.wordlist)
	for dbname in self.wordlist:
	    print self.worddic[dbname],
	    if self.tempdb.has_key(dbname):
	        concountlist[dbname],conlinklist[dbname]=self.Stringload(zlib.decompress(self.tempdb[dbname]))
	print "total word:", totalword
	# find the smallest size of conlinklist.
	mixSL=(0,0)
	for listcount in concountlist.keys():
	    if concountlist[listcount]>mixSL[1] or mixSL==(0,0):
	    	mixSL=(listcount,concountlist[listcount])
	# marge all of the key list.
	basiclist=conlinklist[mixSL[0]]
	for mx in conlinklist.keys():
	   templist={}
	   if mx != mixSL[0]:
	   	for iclb in conlinklist[mx].keys():
		     if basiclist.has_key(iclb):
		     	templist[iclb]=''
		basiclist=templist
	# The match key of every conlinklist is basiclist
	querydic={}
	
	tbs=len(basiclist)
	print 'est size',tbs,time.time()-ST
	brack=int(tbs//10000)
	if brack>0:
	    partsize=tbs//brack
	    lastpartsize=tbs%brack
	    # self.page*self.pagesize
	    matst=(self.page%brack)*partsize
	    if matst==0:
	        rlist=basiclist.keys()[matst:partsize+lastpartsize]
	    else:
	    	rlist=basiclist.keys()[matst+lastpartsize:matst+partsize]

	    
	    pagestartat=int(self.page//brack)*self.pagesize
	    #if (pagestartat+self.pagesize)>totalsize:
	    #	pageendat=totalsize
	    #else:
	    pageendat=pagestartat+self.pagesize
	else:
		rlist=basiclist.keys()

	RTS=0.0
	PT=time.time()
	tplist=''
	tpindex={}
	for wi in self.wordlist:
	    tplist=zlib.decompress(self.wpagedb.get(wi))
	    idx=0
	    if tplist:
	        while idx<len(tplist):
		    querykey=tplist[idx:idx+6] # querykey
		    tw=ord(tplist[idx+6]) # wordcount
		    nextidx=idx+7+3*(tw+1)
		    wposition=tplist[idx+7:nextidx]
		    idx=nextidx
		    tpindex[wi+querykey]=wposition
		    #print len(wi+querykey),tw,len(wposition)
	print time.time()-ST	
	for x in rlist:
	    #ptl,title=self.purei.querycontent(x)
	    if not querydic.has_key(x[0:4]):
	    	querydic[x[0:4]]={}
	    posilist=[]
	    ase=0
	    PT=time.time()
	    for pw in self.wordlist:
	    	# total size will be 6 bytes querykey + 1 bytes wordcount + wordcount * 3 bytes position.
		position=tpindex[pw+x]
		totalpositionsize=len(position)//3
		prseek=0
		for pr in xrange(totalpositionsize):
		    pse=position[prseek:prseek+3]
		    start=(ord(pse[0])<<8)+ord(pse[1])
		    end=start+ord(pse[2])
		    posilist.append((start,end))
		    prseek+=3
	    RTS=RTS+(time.time()-PT)
	    posilist.sort()
	    #if x[4:6]==chr(0)+chr(0):
	    #	print posilist
	    querydic[x[0:4]][x[4:6]]=posilist
	    #print posilist
	print RTS
	print len(querydic),time.time()-ST
	scorelist={}
	for senlist in querydic.keys():
	    #print contentprocess.asciitoint(senlist),':'
	    for ralist in querydic[senlist].keys():
	        #print chr(32)*4,contentprocess.asciitolin(ralist),'->',
		rx=querydic[senlist][ralist][0]
		x1,y1=rx[0],rx[1]
		#print rx[0],rx[1],
		i,c=1,0 # i and c value are working for the wordlink
		score=0
		x2,y2=0,0
		a=[]
		for rx in querydic[senlist][ralist][1:]:
		    x2,y2=rx[0],rx[1]
		    if y1==x2 or (y1-1)==x2:
		    	x1,y1=(x1,y2)
			i,c=1,1
		    elif i==1 and c==0:
		    	i=0
			a.append((x1,y1))
			score=score+(y1-x1-2)
			x1,y1=(x2,y2)
			#pse=rx[2]
		    else:
			a.append((x1,y1))
			score=score+(y1-x1-2)
			x1,y1=(x2,y2)
			pse=''
		    c=0
		if i==1:
		    a.append((x1,y1))
		    score=score+(y1-x1-2)
		if a[-1][1]!=y2 and y2!=0:
		    a.append((x2,y2))
		if a:
		    querydic[senlist][ralist]=a
		scorelist[senlist+ralist]=score
	# choucing the bast part of dest
	print "Scorelist:",time.time()-ST
	bastlist=[]
	subjectdic={}
	for senlist in querydic.keys():
	    bscore=0
	    addscore=0
	    tl=''
	    for ralist in querydic[senlist].keys():
		if ralist == chr(0)+chr(0):
		    subjectdic[senlist]=querydic[senlist][ralist]
	        elif scorelist.has_key(senlist+chr(0)+chr(0)):
		    score=scorelist[senlist+chr(0)+chr(0)]+scorelist[senlist+ralist]
		    if score>bscore or bscore==0:
			bscore=score+10
		        tl=ralist
		else:
		    score=scorelist[senlist+ralist]
		    if score>bscore or bscore==0:
		        bscore=score
		        tl=ralist
	    if len(tl):
	        bastlist.append((senlist+tl,bscore))
	ralist=[]
	print "bastlist:",time.time()-ST
	scoredlist=sorted(bastlist, key=operator.itemgetter(1),reverse=True)
        totalsize=len(scoredlist)
	
	if brack==0:
            pagestartat=self.page*self.pagesize
            if (pagestartat+self.pagesize)>totalsize:
                pageendat=totalsize
            else:
                pageendat=pagestartat+self.pagesize
	else:
		totalsize=tbs

	for ikey,score in scoredlist[pagestartat:pageendat]:
	    ptl,title=self.purei.querycontent(ikey) 
	    qstart=querydic[ikey[0:4]][ikey[4:6]][0][0]
	    startat=self.findpunctuation(ptl,qstart)
	    backoff=startat-qstart
	    bdest=0
	    if len(ptl)-startat<10:
	    	bdest=(startat+10-len(ptl))
	    startat=(startat-bdest)
	    #backoff=(backoff-bdest)
	    #print qstart,len(ptl),startat,backoff
	    positionlist=[]
	    for position in querydic[ikey[0:4]][ikey[4:6]]:
		if position[0]-startat>100:
		    break
		else:
		    positionlist.append((position[0]-startat,position[1]-startat))
		    #print position[0]-startat,position[1]-startat
	    url=urllib.quote(self.urldb[self.serialdb[ikey[0:4]]])
	    if subjectdic.has_key(ikey[0:4]):
	    	titleposition=subjectdic[ikey[0:4]]
	    else:
		titleposition=''
	    ralist.append((ptl[startat:startat+100],score,'',url,title,positionlist,titleposition))
	print time.time()-ST
	return (totalsize,ralist)

    def contentquery(self): 
        ST=time.time()
	urllist=[]
        totalword=len(self.wordlist)
	for x in self.wordlist:
		print self.worddic[x]
        print "total word:", totalword
	for dbname in self.wordlist:
	    if self.tempdb.has_key(dbname):
	       urllist=urllist+self.Stringload(zlib.decompress(self.tempdb[dbname]))
        if totalword>1:
	    ranklist=ranking.ranking(urllist)
	    urlcomp=ranklist.dicuniques(totalword)
        else:
	    urlcomp=urllist
	totalsize=len(urlcomp)
	ralist=[]
	pagestartat=self.page*self.pagesize
	if (pagestartat+self.pagesize)>totalsize:
		pageendat=totalsize
	else:
		pageendat=pagestartat+self.pagesize
	
	print time.time()-ST

        if totalword!=1:
	    rangestsart=0
	    rangeend=totalsize
	    if totalsize>500 or pagestartat>=500:
	    	rangestsart=(pagestartat//500)*500
		rangeend=rangestsart+500
		pagestartat=pagestartat-rangestsart
		pageendat=pagestartat+self.pagesize
	    #for i in xrange(0,totalsize):
	    count=0
	    searchtime=0.0
	    linktime=0.0
	    for i in xrange(rangestsart,rangeend):
		bastscore=0
	        mirs=0
	        spliturl=urlcomp[i]
		if totalword>=3:
			sword=3
		else:
			sword=totalword

		if len(spliturl)==2 and spliturl[0]==totalword:
		    at=time.time()
		    self.pct,title=self.purei.queryPurecontent(spliturl[1])
		    bt=time.time()-at
		    matchstart=0
		    scorelist=[]

		    searchtime=searchtime+bt
		    for match in re.finditer(self.uni.decode("utf-8"),self.pct):
			matchstart=match.start()
		    if matchstart:
			bastscore=60
			if (matchstart+150)> len(self.pct):
				mirs=len(self.pct)-matchstart
			scorelist.append((match.start(),match.end()))
			startat=self.findpunctuation(matchstart)
			scorelist=self.wordmarkup(scorelist,startat-mirs)
			abstract=startat-mirs
			destcontent=self.pct[abstract:abstract+150]
			url=urllib.quote(self.urldb[self.serialdb[spliturl[1]]])
			ralist.append((destcontent,bastscore,str(spliturl[0]),url,title,scorelist))

		if len(spliturl)==2 and spliturl[0]>=sword and bastscore==0:
		    at=time.time()
		    # self.pct,title=self.purei.queryPurecontent(spliturl[1])
		    r=[]
		    for dbname in self.wordlist:
			if self.tempdb.has_key(dbname):
				    picklelist=[]
				    for match in re.finditer(self.worddic[dbname],self.pct):
					picklelist.append((match.start(),match.end()))
				    r=r+picklelist
		    r=sorted(r, key=operator.itemgetter(0))
		    r=ranklist.wordlinker(r)
		    bastscore, scorelist = ranklist.counttheimportantpart(r)
		    #print scorelist
		    if len(scorelist)>0:
		        startat=scorelist[0][0]
		        startat=self.findpunctuation(startat)
		        if (startat+150)> len(self.pct):
		            mirs=len(self.pct)-startat
		        scorelist=self.wordmarkup(scorelist,startat-mirs)
		        abstract=startat-mirs
		        destcontent=self.pct[abstract:abstract+150]
		        url=urllib.quote(self.urldb[self.serialdb[spliturl[1]]])
		        ralist.append((destcontent,bastscore,str(spliturl[0]),url,title,scorelist))
		    bt=time.time()-at
		    linktime=linktime+bt

	print 'totalword2:',
	print time.time()-ST

        if totalword==1:
	    for i in xrange(pagestartat,pageendat):
                bastscore=0
                mirs=0
                spliturl=urlcomp[i]
		self.pct,title=self.purei.queryPurecontent(spliturl)
		matchstart=0
		scorelist=[]
		picklelist=[]
		for match in re.finditer(self.uni,self.pct):
                    matchstart=match.start()
		    picklelist.append((match.start(),match.end()))
                if (matchstart+100) > len(self.pct):
                    mirs=len(self.pct)-matchstart
		scorelist=picklelist
		startat=scorelist[0][0]
		startat=self.findpunctuation(startat)
		scorelist=self.wordmarkup(scorelist,startat-mirs)
		abstract=startat-mirs
		destcontent=self.pct[abstract:abstract+150]
		url=urllib.quote(self.urldb[self.serialdb[spliturl[0:4]]])
		#print destcontent,str(1),url,title,scorelist
		ralist.append((destcontent,100,str(1),url,title,scorelist))
	    print 'totalword1:',
	    print time.time()-ST
	    return (totalsize,sorted(ralist, key=operator.itemgetter(1),reverse=True))
	print "search:",str(searchtime)
	print "Link:",str(linktime)
	return (totalsize,sorted(ralist, key=operator.itemgetter(1),reverse=True)[pagestartat:pageendat])
	#return (len(ralist),sorted(ralist, key=operator.itemgetter(1),reverse=True)[pagestartat:pageendat])

