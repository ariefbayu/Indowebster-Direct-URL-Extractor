#!/usr/bin/env python
 
"""
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2010/11/30 $"
"""

import sys
import urllib2
from urlparse import urlparse
import urllib
import os
import re
import time
import gzip
import zipfile
import cStringIO
import string


opener = urllib2.build_opener(urllib2.HTTPHandler())
opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)')]  

def fetch_firstlevel_download_url(url):
	(html, headers) = openUrl( url )
	#print html
	chs = re.compile('href="([^"]+)" class="tn_button1"').findall(html)
	
	if len( chs ) == 0:
		sys.exit(0, "Sorry, can't find first level download url")
	
	return chs[0]
	#print chs

def fetch_real_download_url ( first_url ):
	url_get_real_download = "http://www.indowebster.com/" + first_url
	(html, headers) = openUrl( url_get_real_download )
	
	#print headers;
	
	dl_kuncis = re.compile('<input type="hidden" value="([^"]+)" name="kuncis">').findall(html)
	dl_id = re.compile('<input type="hidden" value="([^"]+)" name="id" />').findall(html)
	dl_name = re.compile('<input type="hidden" value="([^"]+)" name="name" />').findall(html)
	
	#print dl_kuncis
	#print dl_id
	#print dl_name
	
	real_download_url = "http://www.indowebster.com/download.php"
	post_data = {
			"kuncis": dl_kuncis[0],
			"id": dl_id[0],
			"name": dl_name[0],
			"button.x":"10",
			"button.y":"10"
	}
	
	cookie = ''
	for data in headers:
		if data[0] == 'set-cookie':
			cookie = data[1]
	data = urllib.urlencode(post_data)
	req = urllib2.Request(real_download_url, data)
	req.add_header('Referer', url_get_real_download)
	req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)')
	req.add_header('Cookie', cookie)
	
	response = urllib2.urlopen(req)

	return (string.replace(response.headers.getheader('refresh'), '0; url=', ''), dl_name[0])

	
def gunzip(fileobj):
	g = gzip.GzipFile(fileobj=fileobj)
	gFile = g.read()
	g.close()
	return gFile

def openUrl(url):
	request = urllib2.Request(url)
	request.add_header('Accept-encoding', 'gzip')
	retry = 1
	maxRetry = 4
	page = opener.open(request)
	while retry < maxRetry:
		try:
			page = opener.open(request)
		except urllib2.URLError, e:
			retry += 1
		else:
			retry = maxRetry
	html = page.read()
	if page.headers.getheader('content-encoding') == 'gzip':
		html = gunzip(cStringIO.StringIO(html))
	return(html, page.headers.items())

def defaultMessage():
	print "Usage: idws.py fileurl"
	print "Extract indowebster direct url from file url."
	print "Line #1: Direct URL"
	print "Line #2: Filename"

if __name__ == "__main__":
	idws_url = ''
	
	try:
		idws_url = sys.argv[1]
	except:
		defaultMessage()
		sys.exit(1)
	
	try:
		i = urlparse( idws_url )
		if i.scheme == '':
			raise RuntimeError( '[url] must be a valid URL (with trailing http://)' )
	except:
		raise RuntimeError( '[url] must be a valid URL (with trailing http://)' )
	
	#"url is '" + idws_url + "'"
	
	
	try:
		first_url = fetch_firstlevel_download_url( idws_url )
		
		real_dl_url = fetch_real_download_url ( first_url )
		
		print real_dl_url[0]
		print real_dl_url[1]
		
	except urllib2.HTTPError, e:
		print "error: %s" % e.code
	except urllib2.URLError, e:
		print "error: %s" % e.reason
	except:
		print "error: %s" % str(sys.exc_info()[1])
