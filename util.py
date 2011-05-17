import urllib2

def openhtml(urllist):
	request = urllib2.Request(urllist)
	opener = urllib2.build_opener()
	request.add_header('User-Agent','Mozilla/5.001 (windows; U; NT4.0; en-us) Gecko/25250101')
	htmlpage=opener.open(request).read()
	return htmlpage


