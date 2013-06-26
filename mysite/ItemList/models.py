from django.db import models


class Item_db(models.Model):
	item_name = models.CharField(max_length=30)
	item_src = models.URLField()
	pic_src = models.URLField()
	item_price = models.IntegerField()
	source = models.CharField(max_length = 30)

class ItemList(models.Model):
	key_word = models.CharField(max_length = 30,unique=True)
	item_list = models.ManyToManyField(Item_db)

# Create your models here.
