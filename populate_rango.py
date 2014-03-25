import os 


def populate():


	python_cat = add_cat('Python')

	add_page(cat = python_cat,
		title = 'Official Python Tuturial',
		url = 'http://docs.python.org/2/tutorial')

	add_page(cat = python_cat,
		title = 'How to think like a Computer Scientists',
		url = 'http://www.greenteapress.com/thinkpython')

	add_page(cat = python_cat,
		title = 'Learn Python in 10 Minutes',
		url = 'http://www.korokithakis.net/tutorals/python')

	django_cat = add_cat('Django')

	add_page(cat = django_cat,
		title = 'Official Django Tuturial', 
		url = 'https://docs.djangoproject.com/en/1.5/tutorial01/')

	add_page(cat = django_cat,
		title = 'Django Rocks',
		url = 'http://www.djangorocks.com/')

	add_page(cat = django_cat,
		title = 'How to tango with Django',
		url = 'http://www.tangowithdjango.com/')

	frame_cat = add_cat('Other Frameworks')

	add_page(cat = frame_cat,
		title = 'Bottle',
		url = 'http://bottlepy.org/docs/dev')

	add_page(cat = frame_cat,
		title = 'Flask',
		url = 'http://flask.pocoo.org')

	#Print out what we have added to the user
	for cat in Category.objects.all():
		for page in Page.objects.filter(category = cat):
			print ' - {0} - {1} -'.format(str(cat), str(page))



def add_page(cat, title, url, views = 0):
	page = Page.objects.get_or_create(category = cat, title = title,
									url = url, views = views)[0]
	return page

def add_cat(cat):
	if cat == 'Python':
		category = Category.objects.get_or_create(name = cat, 
												  views = 128,
												  likes = 64)[0]
	elif cat == 'Django':
		category = Category.objects.get_or_create(name = cat, 
												  views = 64,
												  likes = 32)[0]
	elif cat == 'Other Frameworks':
		category = Category.objects.get_or_create(name = cat, 
												  views = 32,
												  likes = 16)[0]
	#default
	else:
		category = Category.objects.get_or_create(name = cat)[0]
	
	return category

#Start execution here!

if __name__ == '__main__':
	print 'Starting Rango population script...'
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 
		'tango_with_django.settings')
	from rango.models import Category, Page
	populate()