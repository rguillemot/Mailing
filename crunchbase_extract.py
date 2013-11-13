#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2
import threading
import time
import Queue
import sys
import getopt
from bs4 import BeautifulSoup
import pickle

url_base = 'http://www.crunchbase.com';

#Thread qui parcourt les pages à la suite de la recherche

class ThreadPagination(threading.Thread):
	def __init__(self, queue, out_queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.out_queue = out_queue 
          
	def run(self):
              while True:
		
                page = self.queue.get()

		if _verbose:
			print '{} get {}'.format(self.getName(),page)
            
                html = urllib2.urlopen(page)
		soup = BeautifulSoup(html)

		# Envoie la page suivante dans la permière file d'attente		
		paginationsdiv = soup.find("div", {"class" : "pagination"})
		if paginationsdiv <> None:
			paginations = paginationsdiv.contents
			pagination = paginations[len(paginations)-1]
			if pagination.name == "a":	
				page_next = url_base + pagination['href']
				self.queue.put(page_next)

		# Envoie toutes les liens des entreprises dans la deuxième file d'attente

		for div in soup.find_all("div",{ "class" : "search_result_name" }):
			self.out_queue.put(url_base + div.contents[1]['href']);
            
                self.queue.task_done()

# Thread qui récupère la fiche de chaque entreprise

class ThreadUrl(threading.Thread):
	def __init__(self, queue, dico_url):
		threading.Thread.__init__(self)
		self.queue = queue
		self.dico_url = dico_url
          
	def run(self):
              while True:
             
                company = self.queue.get()
		if _verbose:
			print '{} get {}'.format(self.getName(),company)
            
                url = urllib2.urlopen(company)
                self.dico_url.update({company : url.read()})
            
                #signals to queue job is done
                self.queue.task_done()

def usage():
  print "This is the usage function"
  print 'Usage: '+sys.argv[0]+' -h -q <queryfile> -o <outputfile> -t <nbthreads> -v'

def loadquery(queryfile):
	dicts_from_file = {} 
	with open(queryfile,'r') as inf:
    		for line in inf:
        		dicts_from_file.update(eval(line))
	return dicts_from_file  

def loadcrunchbase(queryfile,nbthreads):
	firstqueue = Queue.Queue()
	secondqueue = Queue.Queue()

	querydico = loadquery(queryfile)
	data = urllib.urlencode(querydico)
	
	url_query = url_base+'/search/advanced/companies';
	request = urllib2.Request(url_query,data)
	
	for i in range(nbthreads):
		t = ThreadPagination(firstqueue,secondqueue)
		t.setDaemon(True)
		t.start()

	dico_list = []
	for i in range(nbthreads):
		dico_list += [{}]
		t = ThreadUrl(secondqueue, dico_list[len(dico_list)-1])
		t.setDaemon(True)
		t.start()

	firstqueue.put(request)	

	firstqueue.join();
	secondqueue.join();

	dico = {}
	for elt in dico_list:
		dico.update(elt)

	return dico

def main(argv):
	start = time.time()
	nbthreads = None
	queryfile = None
	global _verbose
	_verbose = 0 
	
	try:
        	opts, args = getopt.getopt(argv[1:], "hq:o:t:v", ["help","queryfile","outputfile","nbthreads","verbose"])
	except getopt.GetoptError:          
        	usage()                         
        	sys.exit(2)                     
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()                     
            		sys.exit()                  
		elif opt in("-v","--verbose") :
            		_verbose = 1                
		elif opt in ("-q", "--query"):
            		queryfile = arg
		elif opt in ("-o", "--outputfile"):
			outputFile = arg
		elif opt in ("-t", "--nbthreads"):
			nbthreads = int(arg)
	if queryfile == None or outputFile == None or nbthreads == None:
		usage()
		sys.exit()

	print ('file: {}'.format(queryfile))
	print('nbthreads: {}'.format(nbthreads))
	
	dico = loadcrunchbase(queryfile,nbthreads)

	of = open(outputFile, "wb") 
	pickle.dump(dico,of)
	of.close()
	
	end = time.time()
	print "Nb Companies: {}".format(len(dico))
	print "Elapsed Time: %s" % (end - start)

main(sys.argv)
