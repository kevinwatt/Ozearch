from sgmllib import SGMLParser  
  
class AnchorParser(SGMLParser):  
    def __init__(self):  
        SGMLParser.__init__(self)  
        self.anchor =  {'link':'', 'title':''}  
        self.anchorlist = [] 
        self.inA=False

    def start_a(self, attributes):  
        """For each anchor tag, pay attention to the href and title attributes."""  
        href, title = '', ''
        for name, value in attributes:  
            if name.lower() == 'href': href = value  
            if name.lower() == 'title': title = value  
        self.anchor['link'] = href 
        self.anchor['title'] = title 
	self.inA=True

    def handle_data(self, text):
	if self.inA and len(self.anchor['title'])<len(text):
	    #print text
	    self.anchor['title'] = text

    def end_a(self):
    	
        self.anchorlist.append(self.anchor) # store the anchor in a list 
        self.anchor = {'link':'', 'title':''}	# reset the dictionary,  
	self.inA=False

class HinetParser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.seen = 0
        self.text = ""
        self.anagram = []

    def start_span(self, attrs):
        attrs = dict(attrs)
	if attrs.has_key('id') and attrs['id'] == 'newscontent':
            self.seen = 1
    
    def end_span(self):
        if self.seen == 1:
            self.seen = 0

    def handle_data(self,data):
	self.text = data
	if self.seen and len(self.anagram)<len(data):
	    self.anagram.append(data)
	    self.text=''
