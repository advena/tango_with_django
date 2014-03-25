import json 
import urllib, urllib2

def run_query(search_terms):

	#specify the base 
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	source = 'Web'

	#create results per page and offset to specify how many results should be 
	#presented per page and form wichone to start
	results_per_page = 10
	offset = 0

	#wrap the qoutes around our query terms - it's required by Bing API
	query = "'{0}'".format(search_terms)
	query = urllib.quote(query)

	#construct latter part of our request URL.
	#sets the format to JSON and other properities
	search_url = '{0}{1}?$skip={2}&$top={3}&$format=json&Query={4}'.format(
		root_url,
		source,
		offset,
		results_per_page,
		query)

	#setup the authnetication with bing servers 
	username = ''
	bing_api_key = 'Feod5VSxBAYsLyn//wudB9rkCuldAvCL/hRRKFAop10'

	#create a 'password manager' which handles authnetication for us.
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, search_url, username, bing_api_key)

	#create our results list 
	results = []

	try:
		#prepare for connecting to Bing's servers.
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)
			
		#connect to the server and read the response generated
		response = urllib2.urlopen(search_url).read()

		#convert the string response to a Python dictionary object
		json_response = json.loads(response)

		#loop through each page returned, populating out results list
		for result in json_response['d']['results']:
			results.append({
				'title' : result['Title'],
				'link' : result['Url'],
				'summary' : result['Description']})

	#catch URLError exception - something went wrong with the connection
	except urllib2.URLError, e:
		print 'Error when querying the Bing API: ', e

	return results


# if __name__ == '__main__':
# 	query = raw_input('Please provide a query: ')
# 	results = run_query(query)
# 	print results
# 	for result in results:
# 		print 'title', result['title']
# 		print 'url: ', result['link']