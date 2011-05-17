from string import split
import operator

class ranking(object):

    def __init__(self,urllist):
        self.urllist = urllist
        self.url=''

    def dicuniques(self,totalword):
        u={}
        r=[]
        for l in self.urllist:
		# u[l]=((l in u) and u[l]+1) or 1
		if l not in u:
                        u[l]=1
                else:
        		u[l]+=1
	for x in u.keys():
		if u[x]==totalword:
		#if u[x]!=1:
			r.append((u[x],x))
	r=sorted(r, key=operator.itemgetter(0), reverse=True)
	return r

    def urluniques(self):
    	u=[]
	r=[]
	print len(self.urllist)
	for l in self.urllist:
		if l not in u:
			u.append(l)
		else:
			self.url=l
			self.countscore()
			if self.url not in r:
				r.append(self.url)
	r=sorted(r, key=operator.itemgetter(0), reverse=True)
	return r

    def wordlinker(self,rlist):
        i=0
        c=0
        a=[]
	if len(rlist)>0:
            x1,y1=rlist[0]
            for newitem in rlist[1:]:
                x2,y2=newitem
                if x2 == y1 or x2 == (y1-1):
                        x1,y1=(x1,y2)
                        i=1
                        c=1
                elif i==1 and c==0:
                        i=0
                        a.append((x1,y1))
                        x1,y1=(x2,y2)
                elif i==0 and c==0:
                        a.append((x1,y1))
                        x1,y1=(x2,y2)
                c=0
            if i==1:
                a.append((x1,y1))
        return a


    def counttheimportantpart(self,partlist):
        partsize=len(partlist)
        r=[]
        score=0
        bastscore=0
        bastscoremark=[]
        for i in range(partsize):
                        x=partlist[i]
                        r.append(x)
                        for w in range(1+i,partsize):
                                y=partlist[w]
                                if y[0]-x[0] < 100: # the score of next 100 words.
                                   score+=x[1]-x[0]+y[1]-y[0]
                                   r.append(partlist[w])
                                else:
                                   break
                        if bastscore<score:
                                bastscore=score
                                bastscoremark=r
                        r=[]
                        score=0
        if bastscore==0:
                bastscore=1
                tempscore=0
                for lonerone in partlist:
                        if(lonerone[1]-lonerone[0])>tempscore:
                                tempscore=lonerone[1]-lonerone[0]
                                lonerestone=lonerone
                		bastscoremark.append(lonerestone)
        return bastscore,bastscoremark

    def countscore(self):
        spliturl=split(self.url,",")
	self.url=(self.urllist.count(spliturl[0]),spliturl[0])

