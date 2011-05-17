#!/usr/bin/env python
from twisted.web import xmlrpc
from twisted.internet import defer
from dba import preparecontent
from query import QueryObj
from lang import langconvert
# This module is standard in Python 2.2, otherwise get it from
#   http://www.pythonware.com/products/xmlrpc/
import xmlrpclib
from threading import Thread, currentThread
import indexer

class Echoer(xmlrpc.XMLRPC):
    def __init__(self,query):
	self.query=query
	self.newc=preparecontent()
	self.allowNone=1

    def xmlrpc_reload(self):
	query=QueryObj()
	query.dbinit()
	self.query=query
	print 'Database has been Reload'
	return defer.succeed("reloaded")

    def xmlrpc_echo(self, *args):
        """Return all query args."""
	self.query.uni=args[0].encode("utf-8")
	self.query.udngram()
	if len(args)>1:
		self.query.pagesize=args[1]
	if len(args)>2:
		self.query.page=args[2]
	resultsize, ralist = self.query.query()
	return (resultsize,ralist)
    
    def xmlrpc_insertdata(self, *args):
        """ Insert temp data from xmlrpc ."""
	if self.newc.isclosed==1:
	    self.newc=preparecontent()
	if len(args)>2:
	    url=args[0]
	    title=args[1]
	    content=args[2]
	    self.newc.insertbufferlist(url,(title,content))
        return defer.succeed(1)

    def xmlrpc_syncdata(self):
    	if self.newc.isclosed==1:
	    self.newc=preparecontent()
	self.newc.sync()
	self.newc.close()
	self.newc=preparecontent()
	return defer.succeed(1)

    def xmlrpc_Contentprocess(self):
        if self.newc.isclosed==1:
	    pass
	elif self.newc.isclosed==0 and self.newc.gettempsize()>0:
	    self.newc.close()
	    cp=patchwork()
	    cp.start()
	return defer.succeed(1)

class patchwork(Thread):
    def __init__ (self):
        Thread.__init__(self)
	self.lindexer=indexer.Contentprocess()
	self.newc=preparecontent()

    def run(self):
        self.lindexer.contentadd(self.newc.gettempdic())
	#self.lindexer.contentdel(self.newc.gettempdic())
	md5urllist=self.lindexer.closeandreturn() # close pure content process
	indexer.linesplitinster(md5urllist)
	self.newc.delete()
	self.newc.close()

def main():
    from twisted.internet import reactor
    from twisted.web import server
    query=QueryObj()
    query.dbinit()
    r = Echoer(query)
    reactor.listenTCP(4443, server.Site(r))
    reactor.run()

if __name__ == '__main__':
    main()

