#!/usr/bin/python2.5
import string,re,os,time,cPickle
import threading
import locale
import bsddb.db as db
from lang import punctuationmarks
import config,logger

class wordspliting(threading.Thread):
    def __init__(self,context,querykey):
        threading.Thread.__init__(self)
        self.querykey = querykey
        self.context = context.decode("utf-8")
        self.splitmode=1 # 1 or 2
        self.gramword = []
        self.companword = []
        self.dicword = []
        self.ascword = []
        self.wordtypedic = {}
        self.textx = None
        self.text = None
        self.debugmsg = None
        self.db = db.DB()
        dicdir=config.defaultpath+'/dic/'
        self.utf8doc=dicdir+"utf-8doc.db"
        self.db.open(self.utf8doc, None, db.DB_HASH, db.DB_DIRTY_READ)
        self.bign = None
        self.litn = None
        self.word = None
        markworddic=dicdir+"markword.pick"
        self.wordclass=cPickle.load(open(markworddic,'r'))
        self.logger = logger.infologger()
        self.xsplit=[]

    def run(self):
    	locale.setlocale(locale.LC_ALL, 'zh_TW.UTF-8')
        self.text = self.word_split()
        self.xsplit=self.markdicword()
        self.companword,self.dicword=self.letwordtodef()
        self.gramword=[]
        self.textx = None
        self.text = None
        self.word = None
        self.db.close()

    def bigram(self):
        self.gramword=[]
        ngi=1
        if len(self.textx) > 2: # It mast bigger than 2,
            for word in range(len(self.textx)-1):
                self.gramword.append(self.textx[ngi-1:ngi+1])
                ngi += 1
        else:
            self.gramword.append(self.textx)
        return self.gramword

    def joinlist(self,totaltext):
        joinword=""
        tail=self.bign+self.litn+1
        if totaltext<=tail:
            tail=totaltext
        for i in xrange(self.bign,tail):
            if i >= self.bign and i <= self.bign+self.litn:
                if self.wordtypedic.get(self.text[i][0])==2:
                    joinword = joinword+self.text[i][0]+' '
                else:
                    joinword = joinword+self.text[i][0]
        return joinword

    def wordclasscheck(self,word,calist):
        wordlist=[]
        for cl in calist:
            wordlist=wordlist+self.wordclass[cl]
        if word.encode("UTF-8") in wordlist:
            return 1
        else:
            return 0

    def uniques(self):
        u=[]
        for l in self.list:
                if l not in u and len(l)>0:
                    u.append(l)
        return u
    
    def word_split(self):
        word=[]
        asciiword=""
        countb=len(self.context)
        i=0
        aeword=0
        for x in self.context:
            ordx=ord(x)
            if ordx < 0xa0: # ASCII Base10 < 128, 127 is <DEL>
                if ordx > 47 or (ordx in [45,46,47,58] and aeword==1 and 47<ord(asciiword[-1:])<58):
                    if 91<=ordx<=96 or 58<=ordx<=64 or ordx > 122:
                        if aeword==1 and len(asciiword) > 0:
                            word.append((asciiword,(startat,i)))
                            self.wordtypedic[asciiword]=2
                        asciiword='' # clear ASCII word
                        aeword=0
                    else:
                        if aeword==0:
                            startat=i
                            aeword=1
                        asciiword=asciiword+x
                elif ordx > 31:
                    if aeword==1 and len(asciiword) > 0:
                        word.append((asciiword,(startat,i)))
                        self.wordtypedic[asciiword]=2
                        aeword=0
                        asciiword='' # clear ASCII word
                    word.append((x,(i,i+1)))
                    self.wordtypedic[x]=3

            elif 12352 <= ordx <= 40959: # CJK
                if aeword==1 and len(asciiword) > 0:
                    word.append((asciiword,(startat,i)))
                    self.wordtypedic[asciiword]=2
                    aeword=0
                    asciiword=''
                word.append((x,(i,i+1)))
                self.wordtypedic[x]=1
            else:
                if aeword==1 and len(asciiword) > 0:
                    word.append((asciiword,(startat,i)))
                    self.wordtypedic[asciiword]=2
                    aeword=0
                    asciiword=''
                word.append((x,(i,i+1)))
                self.wordtypedic[x]=3
            i+=1

        if aeword==1 and len(asciiword) > 0:
            word.append((asciiword,(startat,i)))
            self.wordtypedic[asciiword]=2	
        return word

    def markdicword(self):
        companword=(0,0)
        xsplit=[]
        self.bign=0
        self.litn=1
        loopi=0
        maxwordindic=6
        cword=len(self.text)
        if cword<maxwordindic:
            maxwordindic=cword
        while cword > self.bign:
            while self.wordtypedic[self.text[self.bign][0]]>2 and cword-1 > self.bign:
                self.bign+=1
            b=self.joinlist(cword)
            self.litn+=1
            #print b,self.bign,self.litn,self.text[self.bign]
            if self.db.has_key(b.encode("utf-8")):
                companword=(self.bign,self.litn) 
            if self.wordtypedic.has_key(b[-1]):
                if self.wordtypedic[b[-1]]==3:
                    # type 3 is interpunction. litn should stop here.
                    self.litn=maxwordindic
            if cword-self.bign-1<maxwordindic:
                maxwordindic=cword-self.bign
            if self.litn>=maxwordindic:
                if companword!=(0,0):
                    # if use self.bign+=1 could find all lexicon.
                    self.bign=self.bign+companword[1]
                    xsplit.append(companword)
                else:
                    self.bign+=1
                self.litn=1
                companword=(0,0)
        return xsplit

    def margelexicon(self,matchcx):
        lx=matchcx[0][0]
        ly=matchcx[len(matchcx)-1][1]
        return (lx,ly)

    def letwordtodef(self):
        dicword=[]
        companword=[]
        lastoneisbword=0
        xsplitkey=0
        xsplitsize=len(self.xsplit)	
        self.debugmsg=("L:%s")%(self.context)
        self.logger.info(self.debugmsg)
        textcount=len(self.text)
        x=0
        if len(self.xsplit)<1:
            self.xsplit.append((-1,0)) # Just give a value, it never use.
        while x < textcount:
            if x == self.xsplit[xsplitkey][0]:
                """ B type word """
                sta,until=self.xsplit[xsplitkey]
                if xsplitkey<xsplitsize-1:
                    xsplitkey+=1
                lexp=[]
                for (w,p) in self.text[sta:(sta+until)]:
                    lexp.append(p)
                start,end=self.margelexicon(lexp)
                self.debugmsg='%s %s %s '%('b:',self.context[start:end],(start,end))
                self.logger.info(self.debugmsg)
                dicword.append((self.context[start:end],1,(start,end))) # dic word type 1
                x=x+until
                lastoneisbword=1
            elif lastoneisbword==0:
                """ A type word """
                lastoneisbword=0
                if self.wordtypedic[self.text[x][0]] in [1,2]: # wordtype is ASCII or CJK
                    alexp=[]
                    for (w,p) in self.text[x:x+2]:
                        if self.wordtypedic[w]!=3:
                            alexp.append(p)
                    start,end=self.margelexicon(alexp)
                    if end-start>1 and x+1<textcount and \
                    self.wordtypedic[self.text[x][0]]==2 and \
                    self.wordtypedic[self.text[x+1][0]]==1: # first word is ASCII.
                        if self.splitmode==1:
                            self.debugmsg='%s %s %s '%('a1:',self.context[alexp[0][0]:alexp[0][1]],(alexp[0][0],alexp[0][1]))
                            self.logger.info(self.debugmsg)
                            companword.append((self.context[alexp[0][0]:alexp[0][1]],2,(alexp[0][0],alexp[0][1]))) 
                            # ascii type 2
                        elif self.splitmode==2:
                            self.debugmsg='%s %s %s '%('a1:',self.context[alexp[0][0]:alexp[0][1]],(alexp[0][0],alexp[0][1]))
                            self.logger.info(self.debugmsg)
                            companword.append((self.context[alexp[0][0]:alexp[0][1]],2,(alexp[0][0],alexp[0][1])))
                            self.debugmsg='%s %s %s '%('a2:',self.context[start:end],(start,end))
                            self.logger.info(self.debugmsg)
                            companword.append((self.context[start:end],3,(start,end))) # ascii word with CJK type 3
                    elif end-start>1 and x+1<textcount and self.wordtypedic[self.text[x][0]]==1 and \
                    self.wordtypedic[self.text[x+1][0]]==2: # second word is ASCII.
                        if self.wordtypedic[self.text[x-1][0]]==2:
                            self.debugmsg='%s %s %s'%('iu-a:',self.text[x][0],(start,end))
                            self.logger.info(self.debugmsg)
                            companword.append((self.text[x][0],4,(start,end))) # CJK unigram is type 4
                        else:
                            pass # we do nothing here, let become first word.

                    elif end-start>1 and self.wordtypedic[self.text[x][0]]==1 and \
                    self.wordtypedic[self.text[x+1][0]]==1: # both are cjk word.
                        self.debugmsg='%s %s %s'%('a:',self.context[start:end],(start,end))
                        self.logger.info(self.debugmsg)
                        companword.append((self.context[start:end],5,(start,end))) # CJK bigram is type 5

                        if self.wordclasscheck(self.context[start],['Ta']) and len(companword)>1:
                            if companword[-2][0][1:2]==self.context[start]:
                                self.debugmsg='%s %s %s %s %s'%("find Ta(stopword)",self.context[start],\
                                "delete",companword[-2][0],companword[-1][0])
                                self.logger.info(self.debugmsg)
                                companword=companword[:-2]
                                companword.append((self.context[start],4,(start,start+1))) # unigram is type 4

                        if self.wordclasscheck(self.context[end-1],['UL']) and len(companword)>1:
                            self.debugmsg='%s %s %s'%(self.context[end-1],'del',companword[-1])
                            self.logger.info(self.debugmsg)
                            companword=companword[:-1]
                            companword.append((self.context[end-1],4,(end-1,end))) # unigram is type 4

                    elif self.wordtypedic[self.text[x][0]]==2: # ascii.
                        self.debugmsg='%s %s %s'%('a1:',self.text[x][0],self.text[x][1])
                        self.logger.info(self.debugmsg)
                        companword.append((self.text[x][0],2,self.text[x][1])) # ascii type 2
                    elif len(companword)>0:
                        if companword[-1][0][-1]!=self.context[start:end]: # unigram word.
                            self.debugmsg='%s %s %s'%('u-a:',self.context[start:end],(start,end))
                            self.logger.info(self.debugmsg)
                            companword.append((self.context[start:end],4,(start,end))) # unigram is type 4
                    elif len(self.context[start:end])==1:
                        companword.append((self.context[start:end],4,(start,end))) # unigram is type 4

                elif self.wordtypedic[self.text[x][0]]==3: # wordtype 3 is interpunction
                    pass
                x+=1
            elif lastoneisbword==1:
                """ C type word """
                lastoneisbword=0
                clexp=[]
                for (w,p) in self.text[x-1:x+1]:
                    if self.wordtypedic[w]!=3:
                        clexp.append(p)
                start,end=self.margelexicon(clexp)
                if end-start>1 and x+1<textcount and self.wordtypedic[self.text[x][0]]==2:
                    if self.splitmode==1:
                        self.debugmsg='%s %s %s'%('c1:',self.context[clexp[-1][0]:clexp[-1][1]],'let a process it.')
                        self.logger.info(self.debugmsg)
                    elif self.splitmode==2:
                        self.debugmsg='%s %s'%('c1:',self.context[clexp[-1][0]:clexp[-1][1]])
                        self.logger.info(self.debugmsg)
                        self.debugmsg='%s %s %s'%('c2:',self.context[start:end],(start,end))
                        self.logger.info(self.debugmsg)
                elif end-start>1:
                    if self.db.has_key(self.context[start:end].encode("utf-8")):
                        lastbwordstart,lastbwordend=self.margelexicon(lexp)
                        bsize=lastbwordend-lastbwordstart
                        if self.db.has_key(self.context[lastbwordstart:lastbwordend-1].encode("utf-8")) and \
                        bsize<(bsize-1+end-start):
                            self.debugmsg='%s %s %s %s %s %s'%('last b',\
                            self.context[lastbwordstart:lastbwordend-1],(lastbwordstart,lastbwordend-1),\
                            'c->b(db)',self.context[start:end],(start,end))
                            #lastoneisbword=1
                            self.logger.info(self.debugmsg)
                            dicword=dicword[:-1]
                            dicword.append((self.context[lastbwordstart:lastbwordend-1],1,(lastbwordstart,lastbwordend-1)))
                            dicword.append((self.context[start:end],1,(start,end)))
                        elif bsize<3 and self.wordclasscheck(self.context[lastbwordstart],['CCA'])==1:
                            self.debugmsg='%s %s %s %s %s'%('find CCA',self.context[lastbwordstart:lastbwordend-1],\
                            'c->b',self.context[start:end],(start,end))
                            self.logger.info(self.debugmsg)
                            companword.append((self.context[lastbwordstart:lastbwordend-1],4,(lastbwordstart,lastbwordend-1)))
                            dicword=dicword[:-1]
                            # companword.append((self.context[lastbwordstart:lastbwordend-1],4,(lastbwordstart,lastbwordend-1)))
                            dicword.append((self.context[start:end],1,(start,end)))
                        else:
                            self.debugmsg='%s %s %s'%('c->b:',self.context[start:end],(start,end))
                            self.logger.info(self.debugmsg)
                            dicword.append((self.context[start:end],1,(start,end)))
                        lastoneisbword=1
                        x+=1
                    elif self.wordclasscheck(self.context[start:end][-1],['UL'])==1:
                        self.debugmsg='%s %s %s'%('ctail:',self.context[start:end],(start,end))
                        self.logger.info(self.debugmsg)
                        companword.append((self.context[start:end][-1],4,(start+1,end)))
                    else:
                        self.debugmsg='%s %s %s'%('c:',self.context[start:end],(start,end))
                        self.logger.info(self.debugmsg)
                        companword.append((self.context[start:end],6,(start,end))) #  # C CJK bigram is type 6
        return companword,dicword

