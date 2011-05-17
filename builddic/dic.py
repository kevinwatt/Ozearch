import string
a=open('dict.dat').read()
for x in string.split(a,"\t"):
    xl=string.split(unicode(x,"utf-8"))
    if len(xl[0])>=2:
        print xl[0],

