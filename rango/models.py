from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):

	name = models.CharField(max_length=128, unique=True)
	views = models.IntegerField(default=0)
	likes = models.IntegerField(default=0)

	
	def __unicode__(self):
		return self.name



class Page(models.Model):

	category = models.ForeignKey(Category)
	title = models.CharField(max_length=128)
	url = models.URLField()
	views = models.IntegerField(default=0)

	def __unicode__(self):
		return self.title

class UserProfile(models.Model):

	#link UserProfile to the User model instance
	user = models.OneToOneField(User)

	#here are additional attribiutes we want to include for user
	website = models.URLField(blank=True)
	picture = models.ImageField(upload_to='profile_imgaes', blank=True)

	def __unicode__(self):
		return self.user.username
		
