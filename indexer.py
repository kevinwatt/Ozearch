#!/usr/bin/env python
from __future__ import division
# division is makes the "/" operator on integers give the same result as for floats.

import sys,re,os,time,hashlib,xmlrpclib
import config, contentprocess
import bngram, porterstemming
from logger import infologger
from zipfile import ZipFile
from string import split,join
from html2txt import html2txt
from util import openhtml
from lang import cutwordrange,langconvert,stopmarks,punctuationmarks
from dba import DataInsert,TextInsert,OriginalPage,Purecontent
from math import ceil
stderr = sys.stderr

class Contentprocess(object):

    def __init__(self):
        self.uni=''
        self.title=''
        self.content=''
        self.md5urllist={}
        self.purei=Purecontent('c')
        self.urlinsert=DataInsert()
        self.urlinsert.urldbinit()

    def closeandreturn(self):
        self.purei.close()
        self.urlinsert.urldbclose()
        return self.md5urllist

    def contentadd(self,largeinsert):
        for x in largeinsert.keys():
            self.uni=x
            cdata=largeinsert[x]
            self.title=cdata[0]
            self.content=cdata[1]
            self.contentinsert()

    def contentinsert(self):
        md5url=hashlib.md5(self.uni).hexdigest()
        self.purei.url_md5=md5url
        self.md5urllist[md5url]=self.uni
        # url db
        self.urlinsert.url=self.uni
        self.urlinsert.md5url=md5url
        self.urlinsert.inserturldb()
        stmk=stopmarks()

        if self.purei.checkexist():
            self.purei.title=self.title.encode("utf-8")
            context=''
            word=self.content
            n=0
            for xw in word:
                if ord(xw)>=32 or ord(xw) in [9,10,13]:
                    context=context+xw
                n+=1
                if n>40000000: # may over 65535 line of a document.
                    break
            context=context+chr(32)
            contline=[]
            contline.append('')
            word='' # release word value
            i=0 # line of contline list
            x=0 # word number
            msl=260
            while x<len(context):
                ordx=ord(context[x])
                contline[i]=contline[i]+context[x]
                sentencecount=len(clearspace((contline[i])))
                if sentencecount>msl and stmk.atypestopmarks(ordx) or \
                sentencecount>msl and context[x:x+2] =='. ' or \
                sentencecount>msl+20 and stmk.btypestopmarks(ordx) or \
                sentencecount>msl+20 and ordx==10 and ord(context[x+1:x+2])<65:
                    nextword=context[x+1:x+2]
                    if nextword:
                        if punctuationmarks(ord(nextword)):
                            # at some case, chinese word will use two marks.
                            x+=1
                            contline[i]=contline[i]+context[x]
                    contline.append('')
                    i=len(contline)-1
                    if msl<=16640 and i%2:
                        msl=msl+msl # Dobule it, Until this value bigger then 16640.
                x+=1
                if sentencecount<msl:
                    contline[i]=contline[i]+context[x:x+msl]
                    x=x+msl

            contcleanline=[]
            i=0 # i for contline
            for x in contline:
                 cont=clearspace(x)
                 if len(cont) > 1:
                     if cont[0]==chr(32) and cont[-1]==chr(32):
                         cont=cont[1:-1]
                     elif cont[-1]==chr(32):
                         cont=cont[:-1]
                     elif cont[0]==chr(32):
                         cont=cont[1:]
                 if len(cont)<65025 and cont!=chr(32):
                     contcleanline.append(cont.encode("utf-8"))
                     i=i+1
            self.purei.purecotentinline=contcleanline
            self.purei.content=clearspace(context).encode("utf-8")
            self.purei.insertPurecontent()
            stderr.write('.')


def OriginalHTMLprocess(listsplit):
    OriginalHTMLdb=OriginalPage()
    ilog=infologger()
    purei=Purecontent('c')
    pat = re.compile('<([^>]|\n)*>')
    space = re.compile('\&nbsp\;|\&copy\;|\r|\t')
    stmk=stopmarks()
    md5urllist={}
    for i in listsplit:
        md5url=md5hex(i)
        md5urllist[md5url]=[i]
        word=''
        st=time.time()
        purei.url_md5=md5url
        if purei.checkexist():
            OriginalHTMLdb.url=i
            parser = html2txt()
            try:
                parser.feed(OriginalHTMLdb.queryoriginalct())
                charset=parser.charset # charset detector
                parser.close()
            except:
                charset=''
            Originaltext=langconvert(OriginalHTMLdb.queryoriginalct(),charset)
            Originaltext=Originaltext.decode("utf-8")
            ilog.sentence_split_info(time.time()-st)
            try: # If this page is normal html format
                parser=''
                parser = html2txt()
                parser.feed(Originaltext)
                word=word+parser.text
                if len(word)==0:
                    word=word+space.sub(chr(32),pat.sub(chr(32),Originaltext))
                contenttitle=clearspace(parser.title)
                parser.close()
                #print contenttitle,i,charset
                purei.title=contenttitle.encode("utf-8")
            except:
                try:
                    parser = html2txt()
                    parser.feed(Originaltext)
                    contenttitle=clearspace(parser.title)
                    parser.close()
                except:
                    contenttitle=''
                purei.title=contenttitle.encode("utf-8")
                word=word+space.sub(chr(32),pat.sub(chr(32),Originaltext))
            
            context=''
            ilog.sentence_split_info(time.time()-st)
            n=0
            for xw in word:
                if ord(xw)>=32 or ord(xw) in [9,10,13]:
                    context=context+xw
                n+=1
                if n>40000000: # may over 65535 line of a document.
                    break
            ilog.sentence_split_info(purei.title+str(len(context))+i+charset)
            context=context+chr(32)
            contline=[]
            contline.append('')
            i=0 # line of contline list
            #for x in xrange(len(context)):
            x=0 # word number
            msl=260
            while x<len(context):
                ordx=ord(context[x])
                contline[i]=contline[i]+context[x]
                sentencecount=len(clearspace((contline[i])))
                #sentencecount=len(contline[i])
                if sentencecount>msl and stmk.atypestopmarks(ordx) or \
                sentencecount>msl and context[x:x+2] =='. ' or \
                sentencecount>msl+20 and stmk.btypestopmarks(ordx) or \
                sentencecount>msl+20 and ordx==10 and ord(context[x+1:x+2])<65:
                    nextword=context[x+1:x+2]
                    if nextword:
                        if punctuationmarks(ord(nextword)):
                            # at some case, chinese word will use two marks.
                            x+=1
                            contline[i]=contline[i]+context[x]
                    contline.append('')
                    i+=1
                    if msl<=16640 and i%2:
                        msl=msl+msl # Dobule it, Until this value bigger then 4000.
                x+=1
                if sentencecount<msl:
                    contline[i]=contline[i]+context[x:x+msl]
                    x=x+msl

            contcleanline=[]
            i=0
            ilog.sentence_split_info(time.time()-st)
            for x in contline:
                cont=clearspace(x)
                if len(cont) > 1:
                    if cont[0]==chr(32) and cont[-1]==chr(32):
                        cont=cont[1:-1]
                    elif cont[-1]==chr(32):
                        cont=cont[:-1]
                    elif cont[0]==chr(32):
                        cont=cont[1:]
                if len(cont)<65025 and cont!=chr(32):
                    contcleanline.append(cont.encode("utf-8"))
                    i=i+1
            ilog.sentence_split_info(time.time()-st)
            purei.purecotentinline=contcleanline
            purei.content=clearspace(context).encode("utf-8")
            purei.insertPurecontent()
            stderr.write('.')
    OriginalHTMLdb.close()
    purei.close()
    return md5urllist

def clearspace(text):
    text=re.sub(unichr(0x3000),chr(32),text)
    return re.sub('\s+',chr(32),text)


def reloadxmlrpcd():
    try:
        xmlrpclib.Server('http://127.0.0.1:4443/').reload()
        return 1
    except:
        return 0


def linesplitinster(md5urllist):
    purei=Purecontent('r')
    total=len(md5urllist)
    wordi=TextInsert()
    wsynccount=0
    for md5url in md5urllist.keys():
        st=time.time()
        tail=[]
        totaldic=0
        totalcomp=0
        pureserial=purei.queryserial(md5url)
        if purei.querycontentcount(pureserial):
            purecount=int(purei.querycontentcount(pureserial))+1
        else:
            purecount=0
        for seri in xrange(purecount):
            querykey=pureserial+contentprocess.lintoascii(seri)
            while count_active(tail) >= config.splitercpu:
                time.sleep(0.5)
            getre=bngram.wordspliting(purei.querycontentinline(querykey),querykey)
            tail.append(getre)
            getre.start() # execute getre.run()
        dba=DataInsert()
        dba.outdicdbinit() # open the word database which are out of dic
        dba.companwordcount=0
        wa=0 # if we have to reload anuutf-8 dic
        for splitterlist in tail:
            splitterlist.join(config.splitertimeout)
            totalcomp=totalcomp+len(splitterlist.companword)
            totaldic=totaldic+len(splitterlist.dicword)
            dba.wordlist=splitterlist.companword
            if dba.wordlist:
                dba.anuworddb()
                wa=1
        dba.outdicdbclose()
        if wa:
            wordi.anureload()
        #print dba.companwordcount,totalcomp,totaldic
        # wordi=TextInsert()
        for splitterlist in tail:
            if splitterlist.dicword:
                wordi.getdicdb=1
                wordi.dicword=splitterlist.dicword
                wordi.tempwurl(splitterlist.querykey)
            if splitterlist.companword:
                wordi.getdicdb=2
                wordi.dicword=splitterlist.companword
                wordi.tempwurl(splitterlist.querykey)
        tail=[]
        #print time.time()-st
        wsynccount+=1
        if wsynccount>8192:
            stderr.write('dbsync')
            wordi.sync_wpage()
            wsynccount=0
            if reloadxmlrpcd():
                stderr.write('+')
        stderr.write('.')

    title,word='',''
    stderr.write('dbsync')
    wordi.sync_wpage()
    if reloadxmlrpcd():
        stderr.write('+')
    wordi.closedicdb()
    purei.close()

def urldbinsert(listsplit):
    urlinsert=DataInsert()
    urlinsert.urldbinit() # open the url database group
    for i in listsplit:
        md5url=hashlib.md5(i).hexdigest()
        urlinsert.url=i
        urlinsert.md5url=md5url
        urlinsert.inserturldb()
    urlinsert.urldbclose()

def count_active(tail):
    num_active = 0
    for g in tail:
        if g.isAlive():
            num_active += 1
    #print "%d alive" % num_active
    return num_active

def httpsplit(url):
    diclist = url.split('/')
    i=0
    enuri="http:/"
    for deuri in diclist:
        if i:
            enuri=enuri+'/'+deuri
        i+=1
    return enuri

def md5hex(str):
        return hashlib.md5(str).hexdigest()

def help():
        print ("Usage: %s [Option] [Location]") % os.path.basename(sys.argv[0])
        print "Option: "
        print ("\t%2s, %-25s %s" % ("-h","--help","show this usage message."))
        print ("\t%2s, %-25s %s" % ("-z","--zipfile","Zip package."))
        print ("\t%2s, %-25s %s" % ("-u","--url","Get html page from web site."))

def main():
    if len(sys.argv) <= 1:
        help()
        sys.exit(2) # common exit code for syntax error
    else:
        if sys.argv:
            if sys.argv[1:] in (['--help'], ['-h'], ['--usage'], ['-?']):
                help()
                sys.exit(0)
            if sys.argv[1] in ('--zipfile', '-z'):
                for zn in sys.argv:
                    if os.path.exists(zn):
                        filename=zn
                fp = ZipFile(filename,'r')
                namelist=fp.namelist()
                listsplit=[]
                OriginalHTMLdb=OriginalPage()
                print "\nOriginalHTML Insert:"
                for i in range(len(namelist)):
                    if split(namelist[i],'/')[-1] != "linkinfo":
                        nametourl=httpsplit(namelist[i])
                        OriginalHTMLdb.url=nametourl
                        if OriginalHTMLdb.checkexist():
                            OriginalHTMLdb.content=fp.read(namelist[i])
                            OriginalHTMLdb.insertoriginalct()
                            listsplit.append(nametourl)
                        stderr.write('.')

            if sys.argv[1] in ('--url','-u'):
                listsplit=[]
                OriginalHTMLdb=OriginalPage()
                OriginalHTMLdb.url=sys.argv[2]
                if OriginalHTMLdb.checkexist():
                    OriginalHTMLdb.content=openhtml(OriginalHTMLdb.url)
                    OriginalHTMLdb.insertoriginalct()
                    listsplit.append(OriginalHTMLdb.url)
    urldbinsert(listsplit)
    OriginalHTMLdb.sync()
    print "\nOriginalHTML Process:"
    md5urllist = OriginalHTMLprocess(listsplit)
    print "\nWordSplitting Process:"
    linesplitinster(md5urllist)
    OriginalHTMLdb.close()

if __name__ == '__main__':
        main()

