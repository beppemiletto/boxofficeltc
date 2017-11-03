'''
Created on 03 nov 2017

@author: beppe
'''
from collections import defaultdict
import pickle
# from dicttoxml import dicttoxml
# from xml.dom.minidom import parseString
# import xml.etree.ElementTree as ET


if __name__ == '__main__':
	aDict = defaultdict(dict)
	aDict['p_uno']['s_uno']={'a':1,'b':2,'c':3}
	aDict['p_uno']['s_due']={'a':4,'b':5,'c':6}
	aDict['p_due']['s_uno']={'d':1,'e':2,'f':3}
	aDict['p_due']['s_due']={'d':4,'e':5,'f':6}
	aDict['p_due']['s_tre']={'d':7,'e':8,'f':9}
	aDict['p_due']['s_tre']={'d':7,'e':8,'f':9}
	
# 	xml = dicttoxml(aDict)
# 	xml_string=parseString(xml)
# 	f = open("my_xml_file.xml", "w", encoding="utf-8")
# 	f.write(xml_string.toprettyxml())
# 	f.close()

# 	f= open("my_xml_file.xml", "r", encoding="utf-8")
# 	doc = ET.parse('myopen("file.dat", "wb")_xml_file.xml')
# 	print(doc)

	pickle.dump(aDict,open("dumpdata.dat", "wb"))
	
	del aDict
	
	aDict=pickle.load(open("dumpdata.dat", "rb"))
	
	print(aDict)
	