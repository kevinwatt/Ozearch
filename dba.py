import cPickle
#import bsddb.db as db
from bsddb import db, dbutils
import time,hashlib
import zlib
import porterstemming
import contentprocess as contentline

class preparecontent(object):

    def __init__(self):
        self.bufferlist={}
        self.isclosed=0
        self.dbstart()

    def dbstart(self):
        self.ctempdb=db.DB()
        self.ctempdb.open('/tmp/tempdb.db', None, db.DB_HASH, db.DB_CREATE)

    def insertbufferlist(self,urlkey,content):
        self.bufferlist[urlkey]=content

    def gettempurl(self):
        return self.ctempdb.keys()

    def gettempsize(self):
        return self.ctempdb.stat()["ndata"]

    def gettempdic(self):
        tdic={}
        for x in self.ctempdb.keys():
            tl=cPickle.loads(self.ctempdb[x])
            tdic[x]=tl
        return tdic

    def sync(self):
        for x in self.bufferlist.keys():
            cl=cPickle.dumps(self.bufferlist[x],protocol=1)
            dbutils.DeadlockWrap(self.ctempdb.put, x , cl, max_retries=12)
            self.cleardic()
        self.ctempdb.sync()

    def delete(self):
        for x in self.ctempdb.keys():
            self.ctempdb.delete(x)
        self.cleardic()
        self.ctempdb.sync()

    def cleardic(self):
        self.bufferlist={}

    def close(self):
        # self.sync()
        self.isclosed=1
        self.ctempdb.close()

class DicQuery(object):

    def __init__(self):
        self.pstemmer=porterstemming.PorterStemmer()
        dicdir="dic/"
        self.utf8doc=dicdir+"utf-8doc.db"
        #self.spae=dicdir+"spae.db"
        self.utf8anu=dicdir+"utf-8anu.db"
        self.docdb=db.DB()
        #self.spaedb=db.DB()
        self.anudb=db.DB()
        self.docdb.open(self.utf8doc, None, db.DB_HASH, db.DB_DIRTY_READ)
        #self.spaedb.open(self.spae, None, db.DB_HASH, db.DB_DIRTY_READ)
        self.anudb.open(self.utf8anu, None, db.DB_HASH, db.DB_DIRTY_READ)

    def dicclose(self):
        self.docdb.close()
        #self.spaedb.close()
        self.anudb.close()

    def tailobject(self,tail):
        worddic={}
        wordlist=[]
        for i in tail:
            for qword in i.dicword:
                word=qword[0]
                if self.docdb.has_key(word.encode("utf-8")):
                    dbname=self.docdb[word.encode("utf-8")]
                    worddic[dbname]=word
                    wordlist.append(dbname)
            for qword in i.companword:
                word=qword[0]
                aw=0
                for x in word:
                    if 58>=ord(x)>=127:
                        print ord(x)
                        break
                    else:
                        aw=1
                if aw==1:
                    word=self.pstemmer.stem(word.lower(),0,len(word)-1)

                if self.anudb.has_key(word.encode("utf-8")):
                    dbname=self.anudb[word.encode("utf-8")]
                    worddic[dbname]=word
                    wordlist.append(dbname)
        return (worddic,wordlist)

class DataInsert(object):

    def __init__(self):
        self.wordlist=[]
        self.md5url=''
        self.url=''
        self.companwordcount=0
        self.dicdir="dic/"
        self.pstemmer=porterstemming.PorterStemmer()

    def urldbinit(self):
        self.urldb=db.DB()
        self.anurldb=db.DB()
        self.urlreltime=db.DB()
        self.urldb.open(self.dicdir+'anurl.db', None, db.DB_HASH, db.DB_CREATE)
        self.anurldb.open(self.dicdir+'url.db', None, db.DB_HASH, db.DB_CREATE)
        self.urlreltime.open(self.dicdir+'urlreltime.db', None, db.DB_HASH, db.DB_CREATE)


    def urldbclose(self):
        self.urldb.close()
        self.anurldb.close()
        self.urlreltime.close()

    def md5hex(self,str):
        return hashlib.md5(str).hexdigest()

    def httpsplit(self,url):
        diclist = url.split('/')
        i=0
        enuri="http:/"
        for deuri in diclist:
                if i:
                        enuri=enuri+'/'+deuri
                i+=1

        return enuri

    def inserturldb(self):
        self.uri=self.url
        if not self.anurldb.has_key(self.uri):
                self.urldb['%s'%self.md5url]='%s'%self.uri
                self.anurldb['%s'%self.uri]='%s'%self.md5url
                self.urlreltime['%s'%self.md5url]='%s'%time.time()
        else:
                self.urlreltime['%s'%self.md5url]='%s'%time.time()

    def outdicdbinit(self):
        #self.spaedb=db.DB()
        #self.spaedb.set_cachesize(0,10*1024*1024,0)
        self.anuwdb=db.DB()
        self.anuwdb.set_cachesize(0,10*1024*1024,0)
        #self.spaedb.open(self.dicdir+'spae.db', None, db.DB_HASH, db.DB_CREATE)
        self.anuwdb.open(self.dicdir+'utf-8anu.db', None, db.DB_HASH, db.DB_CREATE)
    
    def outdicdbclose(self):
        #self.spaedb.sync()
        self.anuwdb.sync()
        #self.spaedb.close()
        self.anuwdb.close()

    def anuworddb(self):
        for x in self.wordlist:
            comencode=x[0].encode("utf-8")
            if x[1]==2:
                comencode=self.pstemmer.stem(comencode.lower(),0,len(comencode)-1)
                # print comencode
                # comencode=comencodestemed
            if x[1]>2:
                self.companwordcount+=1
            if not self.anuwdb.has_key(comencode):
                self.anuwdb['%s'%comencode]='%s'%(self.md5hex(comencode))
        # self.anuwdb.sync()


class OriginalPage(object):
    def __init__(self):
        self.url=''
        self.content=''
        self.exist=0
        self.synccount=0
        self.initdb()

    def initdb(self):
        self.dbfile="database/original.db"
        self.dbhtmlserial="database/oriserial.db"
        self.odb=db.DB()
        self.odb.set_cachesize(0,100*1024*1024,0)
        self.odb.open(self.dbfile, None, db.DB_HASH, db.DB_CREATE)
        self.serialdb=db.DB()
        self.serialdb.set_cachesize(0,100*1024*1024,0)
        self.serialdb.open(self.dbhtmlserial, None, db.DB_HASH, db.DB_CREATE)
        self.serialdb[chr(0)*4]='0' # initial serial db.
        self.serialcursor=self.serialdb.cursor()

    def insertoriginalct(self):
        if not self.odb.has_key(self.url):
            try:
                serialnumber=contentline.asciitoint(self.serialcursor.last()[0])+1
                asciiserial=contentline.inttoascii(serialnumber)
                dbutils.DeadlockWrap(self.serialdb.put, asciiserial, self.url,max_retries=12)
            except db.DBPageNotFoundError: 
                print "WARNING: DBPageNotFoundError while loading database"
                self.serialdb.sync()
                self.close()
                print 'Close db',
                time.sleep(3)
                self.initdb()
                print '-> initial db'
                self.serialdb.sync()
                serialnumber=contentline.asciitoint(serialcursor.last()[0])+1
                asciiserial=contentline.inttoascii(serialnumber)
                dbutils.DeadlockWrap(self.serialdb.put, asciiserial, self.url,max_retries=12)
            compresscontent=zlib.compress(self.content,9)
            dbutils.DeadlockWrap(self.odb.put, self.url, compresscontent,max_retries=12)
            #self.odb['%s'%self.url]='%s'%(compresscontent)
        self.synccount+=1
        if self.synccount//20000==0:
            self.sync()
        return

    def checkexist(self):
        if not self.odb.has_key(self.url):
            self.exist=True
        else:
            self.exist=False
        return self.exist

    def queryoriginalct(self):
        try:
            if self.odb.has_key(self.url):
                if len(self.odb.get(self.url))>0:
                    return zlib.decompress(self.odb.get(self.url),15)
        except db.DBRunRecoveryError:
            print "WARNING: db.DBRunRecoveryError while loading database"
            self.odb.sync()
            self.close()
            print 'Close db',
            time.sleep(3)
            self.initdb()
            print '-> initial db'
            self.odb.sync()

    def sync(self):
        self.odb.sync()
        self.serialdb.sync()

    def close(self):
        self.odb.sync()
        self.odb.close()
        self.serialdb.sync()
        self.serialdb.close()
        return

class Purecontent(object):

    def __init__(self,dbmode):
        self.url_md5=''
        self.content=''
        self.title=''
        self.purecotentinline=[]
        self.exist=0
        #self.dbmode="r"
        self.openpdb(dbmode)

    def openpdb(self,dbmode):
        dbenv = db.DBEnv()
        envflags= db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK
        dbenv.set_mp_mmapsize(10*1024*1024)
        dbenv.set_cachesize(0,50*1024*1024,0)
        homeDir='database/'
        dbenv.open(homeDir, envflags|db.DB_CREATE)
        self.pdb=db.DB(dbenv)
        self.pdb.open('purecontent.db', None, db.DB_HASH, db.DB_CREATE)
        self.tdb=db.DB()
        titledb="database/title.db"
        #self.dbfile="database/purecontent.db"
        inlinedb="database/purecontentinline.db"
        countline="database/purecontentcount.db"
        dbconserial="database/pureserial.db"
        dbpureserial="database/serialpure.db"
        self.serialdb=db.DB()
        self.puresedb=db.DB()
        self.pureinline=db.DB()
        self.purecontentcount=db.DB()

        if dbmode=="c":
            self.tdb.open(titledb, None, db.DB_HASH, db.DB_CREATE)
            self.puresedb.open(dbpureserial, None, db.DB_HASH, db.DB_CREATE)
            self.pureinline.open(inlinedb, None, db.DB_HASH, db.DB_CREATE)
            self.purecontentcount.open(countline, None, db.DB_HASH, db.DB_CREATE)
            self.serialdb.open(dbconserial, None, db.DB_HASH, db.DB_CREATE)
            self.serialcursor=self.serialdb.cursor()
        else:
            self.tdb.open(titledb, None, db.DB_HASH, db.DB_DIRTY_READ)
            self.puresedb.open(dbpureserial, None, db.DB_HASH, db.DB_DIRTY_READ)
            self.pureinline.open(inlinedb, None, db.DB_HASH, db.DB_DIRTY_READ)
            self.purecontentcount.open(countline, None, db.DB_HASH, db.DB_DIRTY_READ)
            self.serialdb.open(dbconserial, None, db.DB_HASH, db.DB_DIRTY_READ)

    def insertPurecontent(self):
        if not self.pdb.has_key(self.url_md5) and len(self.content) > 1:
            self.serialdb[chr(0)*4]='0' # initial serial db.
            serialnumber=contentline.asciitoint(self.serialcursor.last()[0])+1
            asciiserial=contentline.inttoascii(serialnumber)
            self.serialdb[asciiserial]=self.url_md5 #  serialdb insert
            self.puresedb['%s'%self.url_md5]=asciiserial # insert serial to url_md5
            compresscontent=zlib.compress(self.content,9)
            self.pdb['%s'%asciiserial]='%s'%(compresscontent)
            if not self.tdb.has_key(asciiserial) and len(self.title) > 1:
                self.tdb['%s'%asciiserial]='%s'%(self.title)
            
            # insert purecontentcount and pureinline
            totallinesize=len(self.purecotentinline)
            self.purecontentcount['%s'%asciiserial]='%s'%str(totallinesize)
            # 2 bytes serial line
            self.pureinline['%s'%asciiserial+contentline.lintoascii(0)]=self.title
            for x in xrange(totallinesize):
                serialkey=asciiserial+contentline.lintoascii(x+1)
                self.pureinline['%s'%serialkey]=self.purecotentinline[x]

    def queryencodcontent(self, md5url):
        purecon,puretitle='',''
        if self.pdb.has_key(md5url):
                purecon=self.pdb.get(md5url)
        if self.tdb.has_key(md5url):
                puretitle=self.tdb.get(md5url)
        return (purecon,puretitle)

    def serialpure(self, md5url):
        return self.serialdb.get(md5url)

    def querycontentinline(self, pureconserial):
        return self.pureinline.get(pureconserial)

    def querycontentcount(self, asciiserial):
        return self.purecontentcount.get(asciiserial)

    def queryserial(self, md5url):
        return self.puresedb.get(md5url)

    def querycontent(self, key):
        pil,puretitle='',''
        if self.pureinline.has_key(key):
            pil=self.pureinline.get(key)
        if self.tdb.has_key(key[0:4]):
            puretitle=self.tdb.get(key[0:4])
        return (pil.decode("utf-8"),puretitle)

    def queryPurecontent(self, md5url):
        if self.pdb.has_key(md5url[0:4]):
            purecon=zlib.decompress(self.pdb.get(md5url[0:4]),15)
            #purecon=self.pdb.get(md5url[0:4])
        else:
            purecon=''
        if self.tdb.has_key(md5url[0:4]):
            puretitle=self.tdb.get(md5url[0:4])
        else:
            puretitle=''
        return (purecon,puretitle)

    def checkexist(self):
        if not self.puresedb.has_key(self.url_md5):
            self.exist=True
        else:
            self.exist=False
        return self.exist

    def close(self):
        self.pdb.close()
        self.tdb.close()
        self.serialdb.close()
        self.puresedb.close()
        self.pureinline.close()
        self.purecontentcount.close()

class TextInsert(object):

    def __init__(self):
        self.getdicdb=0
        self.dicword=[]
        self.insertbuffer={} # For wpage Buffer
        self.tempbuffer={} # For tempdb Buffer
        self.content='' # pure page content without html target.
        self.dicdir="dic/"
        self.dbfile="database/word_database.db"
        self.pstemmer=porterstemming.PorterStemmer()
        self.utf8doc=db.DB()
        self.utf8doc.open(self.dicdir+"utf-8doc.db", None, db.DB_HASH, db.DB_DIRTY_READ)
        self.utf8anu=db.DB()
        self.utf8anu.open(self.dicdir+"utf-8anu.db", None, db.DB_HASH, db.DB_DIRTY_READ)

        self.wdbenv = db.DBEnv()
        self.envflags= db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK

        self.wdbenv.set_mp_mmapsize(100*1024*1024)
        self.wdbenv.set_cachesize(0,200*1024*1024,0)
        self.homeDir='database/wpage/'
        self.wdbenv.open(self.homeDir, self.envflags|db.DB_CREATE)
        self.wpagedb=db.DB(self.wdbenv)
        self.wpagedb.open('wpagedb.db', None, db.DB_HASH, db.DB_CREATE)
        # DB Env
        self.dbtype = db.DB_HASH
        self.dbopenflags = db.DB_THREAD
        self.envflags = db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK
        self.dbenv = db.DBEnv()
        self.homeDir='database/world/'
        self.dbenv.set_mp_mmapsize(50*1024*1024)
        self.dbenv.set_cachesize(0,100*1024*1024,0)
        self.dbenv.open(self.homeDir, self.envflags|db.DB_CREATE)
        self.tempdb=db.DB(self.dbenv)
        self.tempdb.open('tempwdb.db', mode=0660, dbtype=self.dbtype, flags=self.dbopenflags|db.DB_CREATE)
        #self.dicdb=db.DB()

    def opendicdb(self):
        if self.getdicdb==1:
            self.dicdb=self.utf8doc
        elif self.getdicdb==2:
            self.dicdb=self.utf8anu
    
    def Stringloadcheck(self,UrlString):
        return 1

    def x3tracp(self,x3t):
        a=contentline.lintoascii(x3t[0])
        b=chr(x3t[1]-x3t[0])
        return a+b

    def anureload(self):
        self.utf8anu.close()
        self.utf8anu=db.DB()
        self.utf8anu.open(self.dicdir+"utf-8anu.db", None, db.DB_HASH, db.DB_DIRTY_READ)

    def tempwurl(self,querykey): # to create temp database befor into the world database
        """ querykey is pureserial+contentprocess.lintoascii(seri) """
        self.opendicdb()
        sercheck={}
        for sx in self.dicword:
            if sx[1]==2:
                x=self.pstemmer.stem(sx[0].lower(),0,len(sx[0])-1).encode("utf-8")
            else:
                x=sx[0].encode("utf-8")

            if sercheck.has_key(x):
                sercheck[x]+=1
            else:
                sercheck[x]=0

            if self.dicdb.has_key(x) and sercheck[x]==0:
                dicdbmd5=hashlib.md5(x).hexdigest()
                if self.tempbuffer.has_key(dicdbmd5):
                    self.tempbuffer[dicdbmd5]=self.tempbuffer[dicdbmd5]+querykey
                else:
                    if self.tempdb.has_key(dicdbmd5):
                        diclinklist=zlib.decompress(self.tempdb.get(dicdbmd5))
                        self.tempbuffer[dicdbmd5]=diclinklist+querykey
                        #dbutils.DeadlockWrap(self.tempdb.put, dicdbmd5, diclinklist+querykey,max_retries=12)
                    else:
                        self.tempbuffer[dicdbmd5]=querykey
                        #dbutils.DeadlockWrap(self.tempdb.put, dicdbmd5, querykey,max_retries=12)
            # total size will be 6 bytes querykey + 1 bytes wordcount + wordcount * 3 bytes position.
            if self.dicdb.has_key(x) and (sx[2][1]-sx[2][0])<255:
                dicdbmd5=hashlib.md5(x).hexdigest()
                if self.insertbuffer.has_key(dicdbmd5+querykey):
                   self.insertbuffer[dicdbmd5+querykey]=self.insertbuffer[dicdbmd5+querykey]+self.x3tracp(sx[2])
                else:
                   self.insertbuffer[dicdbmd5+querykey]=self.x3tracp(sx[2])

    def sync_wpage(self):
        winsertdata={}
        for dix in self.insertbuffer.keys():
            if (len(self.insertbuffer[dix])//3-1)>255: # I do think this word may useless, if there are so many.
                self.insertbuffer[dix]=self.insertbuffer[dix][0:255*3]
            chrsize=chr(len(self.insertbuffer[dix])//3-1) # start from 0.
            if winsertdata.has_key(dix[0:32]):
                winsertdata[dix[0:32]]=winsertdata[dix[0:32]]+dix[-6:]+chrsize+self.insertbuffer[dix]
            else:
                winsertdata[dix[0:32]]=dix[-6:]+chrsize+self.insertbuffer[dix]
        
        self.insertbuffer={} # reset this value

        for ik in winsertdata.keys():
            if self.wpagedb.has_key(ik):
                swprice=zlib.decompress(self.wpagedb.get(ik))
                compressedik=zlib.compress(swprice+winsertdata[ik])
                dbutils.DeadlockWrap(self.wpagedb.put, ik, compressedik, max_retries=12)
            else:
                compressedik=zlib.compress(winsertdata[ik])
                dbutils.DeadlockWrap(self.wpagedb.put, ik, compressedik, max_retries=12)
        winsertdata={} # release memory.
        for itd in self.tempbuffer.keys():
                dbutils.DeadlockWrap(self.tempdb.put, itd, zlib.compress(self.tempbuffer[itd]), max_retries=12)

        self.tempbuffer={}

    def closedicdb(self):
        # self.dicdb.close()
        self.tempdb.sync()
        self.wpagedb.sync()
        self.tempdb.close()
        self.wpagedb.close()

