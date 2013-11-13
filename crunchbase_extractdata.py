#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
from bs4 import BeautifulSoup
import pickle
import re

url_base = 'http://www.crunchbase.com';

def usage():
  print "This is the usage function"
  print 'Usage: '+sys.argv[0]+' -h -d <datafile> -t <tag> -i <id> -v <value> -g <getid> -o <outputfile>'


def extractcrunchbase(datafile,tagname,idname,valuename,getidname):
	inputfile = open(datafile, "rb") 
	dico  = pickle.load(inputfile)
	inputfile.close()

	dico_out = {}	

	for elt in dico:
		soup = BeautifulSoup(dico[elt])
		if valuename <> "":
			search = re.compile(valuename)
		else:
			search = valuename
		htmlelts = soup.find_all(tagname, {idname : search})
		
		tab = []
		for htmlelt in htmlelts:
			if htmlelt <> None:
				if getidname <> None:
					astr = htmlelt[getidname]
				else: 
					astr = ''.join(htmlelt.get_text())
					astr = re.sub("[ |\n|\t|\r]{1,}", " ", astr)
					astr = re.sub("^[ ]", "", astr)
			tab.append([astr])
		dico_out.update({elt : tab})
	return dico_out

def main(argv):
	global _verbose
	_verbose = 0 
	datafile = None
	tagname = None
	idname = None
	valuename = None
	getidname = None
	outputfilename = None	
	try:
        	opts, args = getopt.getopt(argv[1:], "hd:t:i:v:g:o:", ["help","datafile","tag","id", "value", "getid","outputfile"])
	except getopt.GetoptError:          
        	usage()                         
        	sys.exit(2)                     
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()                     
            		sys.exit()                  
		elif opt in ("-d", "--datafile"):
            		datafile = arg
		elif opt in ("-t", "--tag"):
            		tagname = arg
		elif opt in ("-i", "--id"):
			idname = arg
		elif opt in ("-v", "--value"):
            		valuename = arg
		elif opt in ("-g", "--getid"):
			getidname = arg
		elif opt in ("-o", "--outputfile"):
			outputfilename = arg
	if datafile == None or tagname == None or idname == None or valuename == None or outputfilename == None:
		usage()
		sys.exit()

	print 'data file : {}'.format(datafile)
	print 'tag name : {}'.format(tagname)
	print 'id name : {}'.format(idname)
	print 'value name : {}'.format(valuename)
	print 'get id name: {}'.format(getidname)
	print 'output file {}'.format(outputfilename)
	
	dico = extractcrunchbase(datafile, tagname, idname, valuename, getidname)

	outputfile = open(outputfilename, "wb") 
	pickle.dump(dico,outputfile)
	outputfile.close()

main(sys.argv)
