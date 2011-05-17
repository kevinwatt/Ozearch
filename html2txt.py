from sgmllib import SGMLParser
import re
import htmllib
class AnchorParser(htmllib.HTMLParser):
    def __init__(self):
       # flag to determine if we are in an anchor tag
       self.in_anchor = 0

    def start_a(self, attrs):
       """Signal when we get to an <a> tag.
       """
       self.in_anchor = 1

    def end_a(self, attrs):
       """Signal when we are out of the anchor -- a </a> tag"""
       self.in_anchor = 0

    def handle_data(self, text):
       """This is called everytime we get to text data (ie. not tags) """
       if self.in_anchor:
          print "Got anchor text: %s" % text

class html2txt(SGMLParser):

    def reset(self):
        self.text = ''
	self.title = ''
	self.charset = ''
        self.inbody = True
	self.inside_title = False
        SGMLParser.reset(self)

    def start_meta(self, attrs):
    	#CHARSET_RE = re.compile(r'charset="?([^\s"]*)"?', re.I)
	CHARSET_RE = re.compile("((^|;)\s*charset=)([^;]*)")
	httpEquiv=None
	contentType=None
    	for i in range(0, len(attrs)):
		key, value = attrs[i]
		key = key.lower()
		if key == 'http-equiv':
			httpEquiv = value
		elif key == 'content':
			contentType = value
		#CHARSET_RE.search(contentType)
	if httpEquiv and contentType:
		match = CHARSET_RE.search(contentType)
		try:
		    if match.group(3):
			self.charset = match.group(3)
		except:
		    self.charset = ''

    def start_title(self, attrs):
        self.inside_title = True

    def end_title(self):
        self.inside_title = False

    def handle_data(self,text):
        if self.inbody:
            self.text += text
	if self.inside_title and text:
	    self.title = text

    def get_hyperlinks(self):
    	return self.hyperlinks

    def start_head(self,text):
        self.inbody = False

    def end_head(self):
        self.inbody = True

