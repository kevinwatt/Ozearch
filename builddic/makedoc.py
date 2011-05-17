#!/usr/bin/python2.4
import bsddb,md5
dicdir='dic/'
db = bsddb.btopen('dic/utf-8doc.db', 'r')
newdb = bsddb.btopen('dic/c_doc.db', 'c')
def uniques(list):
        u=[]
        for l in list:
                if l not in u:
                        u.append(l)
		else:
			print l
        return u

value=[]
hash = md5.new()
for i in db.keys():
	value.append(db[i])
	try:
		#print i.decode("utf-8")
		hash.update(i)
		md5url=hash.hexdigest()
		newdb['%s'%i]='%s'%md5url
	except:
		pass
newdb.close()
print "Total key:"+str(len(db.keys()))
