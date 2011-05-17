#!/usr/bin/python
import cPickle
from bsddb import db, dbutils
import xmlrpclib

s = xmlrpclib.Server('http://127.0.0.1:4443/')
newsdb=db.DB()
newsdb.open('/var/tmp/newsdb.db', None, db.DB_HASH, db.DB_CREATE)
print len(newsdb.keys())
if len(newsdb.keys()) > 0:
    for x in newsdb.keys():
        news=cPickle.loads(newsdb[x])
        s.insertdata(x,news[0],news[1])
        newsdb.delete(x)
s.syncdata()
newsdb.sync()
newsdb.close()
s.Contentprocess()


