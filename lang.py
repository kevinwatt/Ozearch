class stopmarks(object):
    def __init__(self):
	a=[65108,65110,65111,65281,65294,65311,65307,65377,65381,65439,65518]
        a=a+[12442,12444,12288,12290]
        a=a+[9474,9472]
        self.a=a+[63,59,33,124]
        
	b=[65104,65109,65292,65306,65380] # , : ,
        self.b=b+[44,46]

    def atypestopmarks(self,ordx):
	if ordx in self.a:
                return 1 # True
        else:
                return 0 # False

    def btypestopmarks(self,ordx):
	if ordx in self.b:
		return 1 # True
	else:
		return 0 # False

def punctuationmarks(ordx):
        if 65280 <= ordx <= 65295 or 65339 <= ordx <= 65344 \
        or 65371 <= ordx <= 65519 or 65306 <= ordx <= 65312 \
        or 65072 <= ordx <= 65135 or 12286 <= ordx <= 12351 \
        or 12800 <= ordx <= 13055 or 91<=ordx<=96 \
	or 58<=ordx<=64 or 32<=ordx<=48 or 123<= ordx <=0x127: # CJK punctuation marks
                return 1 # True
        else:
                return 0 # False

def cutwordrange():	
	cutword=range(1,48)+range(58,65)+range(91,97)+range(123,128)
	cutword=cutword+range(12286,12352)+range(65280,65296)+range(65339,65345)
	cutword=cutword+range(65371,65520)+range(65306,65313)+range(65072,65136)
	cutword=cutword+range(12286,12352)+range(12800,13056)
	return cutword

def langconvert(text,charset):
        # Ha, You are looking this function!!
        # If you know any batter way to do. change this stupid stuff, Plz....
        # * Chinese (PRC): gb2312 gbk gb18030 big5hkscs hz
	# * Chinese (ROC): big5 cp950
	# * Japanese: cp932 shift-jis shift-jisx0213 shift-jis-2004 euc-jp euc-jisx0213 
	#   euc-jis-2004 iso-2022-jp iso-2022-jp-1 iso-2022-jp-2 iso-2022-jp-3 iso-2022-jp-ext iso-2022-jp-2004
	# * Korean: cp949 euc-kr johab iso-2022-kr
	# * Unicode: utf-7 utf-8 utf-16 utf-16-be utf-16-le
    uni=""
    if charset:
    	if charset.upper()=="BIG5":
	    uni = unicode(text,"cp950",'ignore')
	else:
	    try:
	        uni = unicode(text,charset.lower(),'ignore')
	    except:
	        uni = guesscharset(text)
	return uni.encode("utf-8")
    else:
    	uni = guesscharset(text)
	return uni.encode("utf-8")

def guesscharset(text):
    uni=''
    try:
            uni = unicode(text, "cp950")
    except:
            try:
                uni = unicode(text, "big5_tw")
            except:
                try:
                        uni = unicode(text, "utf-8")
                except:
                        try:
                                uni = unicode(text, "gb2132")
                        except:
                                try:
                                        uni = unicode(text, "ascii")
                                except:
                                        try:
                                                uni = unicode(text)
                                        except:
                                                pass
    return uni

