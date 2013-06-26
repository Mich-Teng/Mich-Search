from django.db import models
from django.contrib.auth.models import User,UserManager
from ItemList.models import *


class Account(models.Model):
	user = models.ForeignKey(User, unique=True, related_name='profile')
	name = models.CharField(max_length=30,blank=True,null=True)
	city = models.CharField(max_length=60,blank=True,null=True)
	province = models.CharField(max_length=50,blank=True,null=True)
	country = models.CharField(max_length=50,blank=True,null=True)
	description = models.CharField(max_length=300,blank=True,null=True)
	favorite = models.CharField(max_length=1000,blank=True,null=True)
	count = models.IntegerField(default = 0)
	favor_items = models.ManyToManyField(ItemList)
	class Meta:
		ordering=['name']


	


#User.profile = property(lambda u: Account.objects.create(user=u))	


# Create your models here.
