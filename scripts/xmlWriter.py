from lxml import etree
import sys
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl

class XMLWriter:

	def __init__(self, fileName):
		self.out = open(fileName, 'w')
		self.g = XMLGenerator(self.out, 'utf-8')
		return

	def writeHeader(self, header):	
		#self.out.write("""<?xml version="1.0" encoding="UTF-8"?>""")
		#self.out.write("""<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd">""")
		self.out.write(header)
		return

	def startTag(self, name, attr={}, body=None, namespace=None):
		attr_vals = {}
		attr_keys = {}
		for key, val in attr.iteritems():
			key_tuple = (namespace, key)
			attr_vals[key_tuple] = val
			attr_keys[key_tuple] = key
		attr2 = AttributesNSImpl(attr_vals, attr_keys)
		self.g.startElementNS((namespace, name), name, attr2)
		if body:
			self.g.characters(body)
		return

	def endTag(self, name, namespace=None):
		self.g.endElementNS((namespace, name), name)
		return

	def tag(self, name, attr={}, body=None, namespace=None):
		self.startTag(name, attr, body, namespace)
		self.endTag(name, namespace)
		return

	def endDocument(self):
		self.g.endDocument()
		self.out.close()
		return
