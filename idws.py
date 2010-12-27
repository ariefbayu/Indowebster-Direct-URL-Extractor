#!/usr/bin/env python
 
"""
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2010/12/11 $"
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
import getopt


loop_count = 10 #how many try is allowed before timeout?

opener = urllib2.build_opener(urllib2.HTTPHandler())
opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)')]  

def fetch_firstlevel_download_url(url):
	(html, headers) = openUrl( url )

	chs = re.compile('href="([^"]+)" class="tn_button1"').findall(html)
	
	if len( chs ) == 0:
		sys.exit(0, "Sorry, can't find first level download url. Maybe indowebster redesign it's homepage.")
	
	return chs[0]

def fetch_real_download_url ( first_url ):
	url_get_real_download = "http://www.indowebster.com/" + first_url
	fetch_result = False
	
	fetch_result = openUrl( url_get_real_download )
	html = headers = False
	if fetch_result == False:
		return False
	
	(html, headers) = fetch_result
	

	dl_kuncis = re.compile('<input type="hidden" value="([^"]+)" name="kuncis">').findall(html)
	dl_id = re.compile('<input type="hidden" value="([^"]+)" name="id" />').findall(html)
	dl_name = re.compile('<input type="hidden" value="([^"]+)" name="name" />').findall(html)
	
	if len(dl_kuncis) == 0:
		return False
	
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

	(response, headers) = openUrl(real_download_url, data, 
								url_get_real_download, 
								'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)', 
								cookie)
	idws_direct_url = ''
	for data in headers:
		if data[0] == 'refresh':
			idws_direct_url = string.replace(data[1], '0; url=', '')

	if idws_direct_url.strip() == '':
		return False
	return (idws_direct_url, dl_name[0])

	
def gunzip(fileobj):
	g = gzip.GzipFile(fileobj=fileobj)
	gFile = g.read()
	g.close()
	return gFile

def openUrl(url, data=None, referer=None, UA=None, Cookie=None):
	if data == None:
		request = urllib2.Request(url)
	else:
		request = urllib2.Request(url, data)
	request.add_header('Accept-encoding', 'gzip')
	if referer <> None:
		request.add_header('Referer', referer)
	if UA <> None:
		request.add_header('User-Agent', UA)
	if Cookie <> None:
		request.add_header('Cookie', Cookie)

	retry = 1
	maxRetry = 4
	try:
		page = opener.open(request)
	except urllib2.HTTPError, e:
		return False
	
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
	print "Usage: " + sys.argv[0] + " -u fileurl [OPTION...]"
	print "Extract indowebster direct url from file url."
	print """
	   -u, --url FILEURL                indowebster's permalink URL
	   -w, --as-wget                    echo result as wget command (wget -c url -u filename) 
	   -e, --extra-param EXTRA_PARAM    Extra parameter for wget if -w is set
	"""

if __name__ == "__main__":
	idws_url = ''
	wget_extra_param = ''
	echo_as_wget = False
	try:

		opts, args = getopt.getopt(sys.argv[1:], "u:e:w", ["url=", "extra-param=", "as-wget"])

		for opt, arg in opts:
			if opt in ("-u", "--url"):
				idws_url = arg
			elif opt in ("-e", "--extra-param"):
				wget_extra_param = arg
			elif opt in ("-w", "--as-wget"):
				echo_as_wget = True

	except:
		defaultMessage()
		sys.exit( 1 )

	i = urlparse( idws_url )
	if i.scheme == '':
		print '[url] must be a valid URL (with trailing http://)'
		sys.exit( 1 )	

	counter = 0
	first_url = False
	while first_url == False and counter < loop_count:
		counter += 1

		first_url = fetch_firstlevel_download_url( idws_url )

		if first_url == False:
			continue

		counter2 = 0
		real_dl_url = False
		while real_dl_url == False and counter2 < loop_count:
			counter2 += 1

			real_dl_url = fetch_real_download_url ( first_url )
			if real_dl_url == False:
				#sleep, to prevent abusing idws's server resources
				#print "sleep #", counter2
				time.sleep(0.5)

	if real_dl_url == False:
		print "unable to fetch direct download from %s" % idws_url
	else:
		if echo_as_wget:
			print "wget " + wget_extra_param + " -c \"" + real_dl_url[0] + "\" -O \"" + real_dl_url[1] + "\" "
		else:
			print real_dl_url[0]
			print real_dl_url[1]


#	except urllib2.HTTPError, e:
#		print "error: %s" % e.code
#	except urllib2.URLError, e:
#		print "error: %s" % e.reason
#	except:
#		print "error: %s" % str(sys.exc_info()[1])
