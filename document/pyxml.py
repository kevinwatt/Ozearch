#!/usr/bin/python
# -*- coding: utf-8 -*-
from xml.dom import minidom
import sys

sys.getdefaultencoding()

xmldoc = minidom.parse('詞首1.xml')
for x in xmldoc.getElementsByTagName('AFFIX'):
	print x.firstChild.data,

print len(xmldoc.getElementsByTagName('AFFIX'))

