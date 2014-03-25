def decode_url(url):

	''' Decodes given url that all underscores are replaced 
		with the whitespaces 

		>>> decode_url(some_sample_url)
		>>> 'some sample url'

	'''
	return url.replace('_', ' ')



def encode_url(url):

	''' Encodes given string that all whitespaces are replaced
		with underscores

		>>> encode_url('some sample url')
		>>> 'some_sample_url'

	'''
	return url.replace(' ', '_')


	