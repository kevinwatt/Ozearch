#!/usr/bin/python
import urllib2,time,cPickle
import sys,re,string
from bsddb import db, dbutils
from htmlparser import AnchorParser,HinetParser
from threading import Thread, currentThread

_proxy=''
MAX_THREADS=6
class getwebpage(Thread):
    def __init__ (self,url):
        Thread.__init__(self)
	self.url=url
	self.urlcount={}
        self.urlanchor={}
	self.edlist=[]

    def run(self):
        self.edlist=self.getlink(self.url)

    def getlink(self,url):
    	self.url=url
        request = urllib2.Request(self.url)
        proxy_handler = urllib2.ProxyHandler({'http': _proxy})
        if len(_proxy)>1:
            opener = urllib2.build_opener(proxy_handler)
        else:
            opener = urllib2.build_opener()
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0')
        b = opener.open(request).read()
	c = AnchorParser() 
	c.feed(b)
	c.close 
	l = c.anchorlist
	urllist={}
	if self.url[0:7]=='http://':
		urllist['scheme']=0
		urllist['link']=self.url[7:].split('/')
	elif self.url[0:8]=='https://':
		urllist['scheme']=1
		urllist['link']=self.url[8:].split('/')
	urllist['host']=urllist['link'][0]
	urllist['deep']=len(urllist['link'])
	fullpathurl=self.schemetype(urllist['scheme'])+'/'.join(urllist['link'][:urllist['deep']-1])+'/'
	rooturl=self.schemetype(urllist['scheme'])+urllist['host']
	rfc1738sw=re.compile('{|}\|\\|^|~|[|]|`|"')
	for x in l:
	    linkurl=re.sub('\r|\t|\n','',x['link'])
	    atext=re.sub('\s+|<([^>]|\n)*>|\&nbsp\;|\&copy\;|\r|\t|\n',chr(32),unicode(x['title'], "cp950"))
	    if not re.search(rfc1738sw,linkurl):
	        if linkurl[0:7]=='http://' or linkurl[0:8]=='https://':
		    if linkurl in self.urlcount:
		        self.urlcount[linkurl]+=1
		    else:
		        self.urlcount[linkurl]=0
			self.urlanchor[linkurl]=atext
		elif linkurl[0]=='/':
		    if rooturl+linkurl in self.urlcount:
		        self.urlcount[rooturl+linkurl]+=1
		    else:
		        self.urlcount[rooturl+linkurl]=0
			self.urlanchor[rooturl+linkurl]=atext
		else:
		    if fullpathurl+linkurl in self.urlcount:
		        self.urlcount[fullpathurl+linkurl]+=1
		    else:
		        self.urlcount[fullpathurl+linkurl]=0
			self.urlanchor[fullpathurl+linkurl]=atext
		        self.getlink(fullpathurl+linkurl)
	return self.urlanchor

    def schemetype(self,st):
	scheme=['http://','https://']
	return scheme[st]

def count_active(edlinklist):
    num_active = 0
    for g in edlinklist:
        if g.isAlive():
            num_active += 1
    return num_active

def help():
        pass

class newscrawler(object):
    "Get web news from hinet"

    def __init__(self):
    	self.contlist={}
	self.start_db()
	self.regi=re.compile("^[0-9]|$[0-9]")
	self.hinetnews=1

    def getcont(self,newslink,newstitle):
        self.newslink = newslink
	self.newstitle = newstitle
	ymdt=(0,0,0,0)
	newstime=''
	NewsComp=''
	# Time
	if self.newslink not in self.rcurl.keys():
	    if self.hinetnews and self.newslink and len(self.newstitle)>7:
	        if self.newstitle[-3]==':':
	            if self.regi.match(self.newstitle[-2:]) and \
		    self.regi.match(self.newstitle[-5:-3]):
		        data=self.newslink.split('/')[4]
		        y=data[0:4]
		        m=data[4:6]
		        d=data[6:]
	 	        ntime=self.newstitle[-5:]
		        ymdt=(y,m,d,ntime)

	        if self.newstitle[-7]==')':
	    	    if self.newstitle.rfind(')')>self.newstitle.rfind('('):
		        NewsComp=self.newstitle[self.newstitle.rfind('(')+1:self.newstitle.rfind(')')]
		        self.newstitle=self.newstitle[0:self.newstitle.rfind('(')]
            self.contents = self.getnews()
	    if len(self.contents)>10 and self.newslink and self.newstitle:
	        self.contlist[newslink]=(self.newstitle,self.contents,ymdt,NewsComp)

    def start_db(self):
    	self.newsdb=db.DB()
	self.newsdb.open('/var/tmp/newsdb.db', None, db.DB_HASH, db.DB_CREATE)
	self.rcurl=db.DB()
	self.rcurl.open('/var/tmp/rcurl.db', None, db.DB_HASH, db.DB_CREATE)

    def insertdb(self):
    	# cont table is title and content.
	for x in self.contlist.keys():
    	   dbutils.DeadlockWrap(self.newsdb.put, x , cPickle.dumps(self.contlist[x],protocol=1), max_retries=12)
	   dbutils.DeadlockWrap(self.rcurl.put, x , str(time.time()) , max_retries=12)
    def close_db(self):
    	self.newsdb.sync()
	self.newsdb.close()
	self.rcurl.sync()
	self.rcurl.close()

    def urlcontent(self):
        request = urllib2.Request(self.newslink)
        proxy_handler = urllib2.ProxyHandler({'http': _proxy})
        if len(_proxy)>1:
            opener = urllib2.build_opener(proxy_handler)
        else:
            opener = urllib2.build_opener()
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0')
        b = opener.open(request).read()
	return b

    def getnews(self):
        b=unicode(self.urlcontent(), "cp950",'ignore')
        list=[]
        hp=HinetParser()
	hp.feed(b)
	hp.close()
	context=''
	for x in hp.anagram:
	    context=context+re.sub("   +|\n|\t|\r",'',x)+"\n"
	hp.anagram=[]
	#print context
	return context

if sys.argv[1:]:
    cmdin=sys.argv[1:]
    if cmdin[0] in ('-f','--urllist'):
        pass
    elif cmdin[0] in ('-h','--help'):
	pass
    elif cmdin[0][0:4]=="http":
        edlinklist=[]
        edlinkthread = getwebpage(cmdin[0])
        edlinkthread.start()
else:
	edlinkthread = getwebpage('http://times.hinet.net/realtime/')
	edlinkthread.start()
	edlinkthread.join()
	nc=newscrawler()
        for x in edlinkthread.urlanchor:
	    nc.getcont(x,edlinkthread.urlanchor[x])
	nc.insertdb()
	nc.close_db()

