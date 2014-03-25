from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.utils import *
from rango.bing_search import run_query

from datetime import datetime
import logging

def index(request):

	#get the context of the page
	context = RequestContext(request)
	#get top 5 caategories and pages by ordering them with views
	#get the 5 top most categories
	categories_top = Category.objects.order_by('-views')[:5]

	#make additional field for storing the url
	#create url by repalcing all whitespaces with _ in name attribiute
	for category in categories_top:
		category.url = encode_url(category.name)

	pages = Page.objects.order_by('-views')[:5]
	context_dict = {'categories_top' : categories_top,
				    'pages' : pages,
				    'categories' : get_category_list(10)}

	#COOKIE handler 
	#check if the session has last_visited cookie
	last_visited = request.session.get('last_visited')

	if last_visited:
		#get the visited value

		visits = request.session.get('visits', 0)
		#check if last time the user was less than 5 seconds
		last_time_visited = datetime.strptime(last_visited[:-7],
											  '%Y-%m-%d %H:%M:%S')

		if (datetime.now() - last_time_visited).seconds > 5:
			print visits, last_visited
			#increase the visits cookie value and last time 
			request.session['visits'] = visits + 1
			request.session['last_visited'] = str(datetime.now())

	#session doesn't have the value for the last visited and visits cookie
	else:
		request.session['visits'] = 1
		request.session['last_visited'] = str(datetime.now())



	return render_to_response('index.html', context_dict, context)


def about(request):

	#get the context of the page
	context = RequestContext(request)

	visits = request.session.get('visits', 0)
	context_dict = {'visits' : visits,
					'categories' : get_category_list()}

	return render_to_response('about.html', context_dict, context)


def category(request, category_name_url):

	#get the context of the page
	context = RequestContext(request)
	#replace all underscores with the spaces to handle url
	category_name = decode_url(category_name_url)

	#create dictionary that will keep the categories for passing it to the
	#render function as an argument

	context_dict = {'categories' : category_name}

	#now use try except to catch non existing sites with given category
	#if page exists add new key value pair to the context_dict
	try:

		#use the get() method to find category by name if it not exists it
		#will rise a DoesNotExist exception

		category = Category.objects.get(name = category_name)

		#now get all associated pages with that category

		pages = Page.objects.filter(category = category)

		#add results to the context_dict
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_url'] = category_name_url
		context_dict['categories'] = get_category_list()

	except Category.DoesNotExist:
		#if category not exists pass the function template will handle 
		#that message for us
		pass
	#check if method is POST
	if request.method == 'POST':
		query = request.POST['query'].strip()

		if query:
			#run bing function
			results_list = run_query(query)
			context_dict['results_list'] = results_list
	else:
		context_dict['result'] = 'No results where found'



	return render_to_response('category.html', context_dict, context)

def add_category(request):

	#get the context
	context = RequestContext(request)
	#create empty error dictionary
	errors = ''
	#check if POST
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		#check if form is valid
		if form.is_valid():
			#save the new category to the database
			form.save(commit=True)

			#go back to the main page
			return index(request)

		else:
			# form contains some error extract them
			
			errors = form.errors

	else:
		# request is GET simply display the form to the user
		form = CategoryForm()

	#create dictionary with site context
	context_dict = {'form' : form,
					'errors' : errors,
					'categories' : get_category_list()}

	return render_to_response('add_category.html',context_dict, context)


def add_page(request, category_name_url):

	#get the context
	context = RequestContext(request)

	category_name = decode_url(category_name_url)

	#check if method is POST
	if request.method == 'POST':
		form = PageForm(request.POST)

		#check if form is valid
		if form.is_valid():
			#save the page and get it.
			#we need to populate resto of the categories
			page = form.save(commit=False)

			#get the category
			#wrap all to the try except block to catch the exception if
			#category not exists
			try:
				cat = Category.objects.get(name=category_name)
				page.category = cat
			except Category.DoesNotExist:
				#catch the exeption if category not exists redirect to the
				#add_category page
				return render_to_response('add_category', {}, context)

			#now create the default views field 
			page.views = 0

			#now we can save new model instatnce
			page.save()

			#redirect to the category page
			return category(request, category_name)

		else:
			error = form.errors

	else:
		#method is not POST simply display PageForm
		form = PageForm()

	#create context dictionary to keep the site context
	context_dict =  {'category_name_url' : category_name_url,
					 'category_name' : category_name,
					 'form' : form,
					 'categories' : get_category_list()} 
	
	return render_to_response('add_page.html', context_dict, context)


def register(request):

	#get the request context
	context = RequestContext(request)

	#set value to store the registartion status. Initialy False it will change
	#to True after succesfully resitration proces
	registered = False

	#check if it's POST
	if request.method == 'POST':
		#get the user information that are provided in concrete fileds
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		#check if the form is valid
		if user_form.is_valid() and profile_form.is_valid():
			#save user to the database
			user = user_form.save()

			#hash the user password by use of set_password method 
			user.set_password(user.password)
			user.save()

			#deal with user profile (website and pictures)
			#get the profile but not save it until it will succesfully be made
			profile = profile_form.save(commit=False)
			profile.user = user

			#check if picture is provided
			picture = request.FILES.get('picture', False)
			if picture:
				#if picture is pass it to the user profile
				profile.picture = picture
			else:
				profile.picture = None

			#now we can save the profile
			profile.save()

			#update the registration info 
			registered  = True

		else:
			print user_form.errors, profile_form.errors

	#it's not the POST method so simply render the registartion page
	#using the two model instatnces
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	#create context dictionary to hold site content 
	context_dict = {'user_form' : user_form,
					'profile_form' : profile_form,
					'registered' : registered,
					'categories' : get_category_list()}
	
	return render_to_response('registration.html', context_dict, context)


def user_login(request):

	#get the context of the user request
	context = RequestContext(request)

	#check if it is post method
	if request.method == 'POST':

		#get the username and password
		username = request.POST['username']
		password = request.POST['password']

		#chcek if username and passoword are valid by use of Django 
		#authentication method
		user = authenticate(username=username, password=password)
		if user:
			#check if user account is active
			if user.is_active:
				#user is verified and active so we can log him in
				login(request, user)

				#add cookie to the session with username
				request.session['user'] = username		
				return HttpResponseRedirect('/rango/')
			else:
				#inactive account
				return HttpResponse('Your account has been deactivated')
		else:
			#invalid user details 
			print 'Invalid login detalis: {0}, {1}'.format(username, password)
			return HttpResponse('Invalid login details')

	else:
		return render_to_response('login.html',
								  {'categories' : get_category_list()},
								  context)

@login_required
def restricted(request):

	return HttpResponse('Since you are logged in, you can see this text!')


@login_required
def user_logout(request):
	#because of the decorator we know that user is already logged in
	#so we can simplu log his out
	logout(request)

	return HttpResponseRedirect('/rango/')

@login_required
def auto_add_page(request):
    context = RequestContext(request)
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render_to_response('page_list.html', context_dict, context)


@login_required
def like_category(request):

	#get the context of site
	context = RequestContext(request)
	#create category id and as default set to None
	cat_id = None

	#check if method is GET
	#if so get the category id
	if request.method == 'GET':
		cat_id = request.GET['category_id']

	likes = 0
	print cat_id
	#if category id isn't none get the concrect category
	#and increment the likes by one
	if cat_id:
		category = Category.objects.get(id=int(cat_id))
		if category:
			likes = category.likes + 1
			category.likes = likes
			category.save()

	return HttpResponse(likes);

def search(request):

	context = RequestContext(request)
	results_list = []

	#check if method is POST
	if request.method == "POST":
		query = request.POST['query'].strip()

		if query:
			#run bing function
			results_list = run_query(query)

	return render_to_response('search.html', 
		{'results_list' : results_list,
		 'categories' : get_category_list()}, 
		context)

def profile(request):

	#get the context page
	context = RequestContext(request)

	#get the user 
	username = request.session.get('user')
	print username
	user = User.objects.get(username=username)

	context_dict = {'user' : user,
					'categories' : get_category_list}

	return render_to_response('profile.html', context_dict, context)


def track_url(request):

	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			print page_id


			page = Page.objects.get(id=page_id)
			page.views+=1
			page.save()

			url = page.url
			
			return redirect(url)
	return redirect('/rango/')		

def suggest_category(reqeuset):

	#get the context of the site
	contex = RequestContext(request)

	categories = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.method.GET['suggestion']

	categories = get_category_list(8, starts_with)

	return render_to_response('category_list.html',
							  {'categories' : categories},
							  context)


def get_category_list(max_reslut=0, starts_with=''):

	categories = []
	#get the cateogries list according to the parameter starts_with
	#enables getting all cateogries that starts with this particular string
	#if it's not porvided get all caategories
	if starts_with:
		categories = Category.objects.filter(name_istartswith=starts_with)
	else:
		categories = Category.objects.all()

	#now filter the number of records 
	if max_reslut > 0:
		if len(categories) > max_reslut:
			categories = categories[:max_reslut]

	#iterate over all categories and encode the url
	for cat in categories:
		cat.url = encode_url(cat.name)
	

	return categories

