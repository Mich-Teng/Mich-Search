import os,sys
sys.path.append('E:\\bs\\mysite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings' 


from account.models import *
from mysite.views import *


account_list = Account.objects.all()
for account in account_list:
	if account.count != 0:
		favor_list = parseFavorite(account.favorite)
		account.favor_items.clear()
		print len(favor_list)
		for i in range(len(favor_list)-1):
			favor_item = favor_list[i]
			if favor_item != None:
				item_list = Search(None,"/search ?q="+favor_item+"&src=all&page=1")
				print item_list
				try:
					q = ItemList.objects.get(key_word = favor_item)
				except:
					q = ItemList(key_word = favor_item)
					q.save()
				for item in item_list:
					p = Item_db(item_src=item.item_src,pic_src = item.pic_src,item_name = item.item_name,item_price = item.item_price,source = item.source)
					p.save()
					q.item_list.add(p)
				account.favor_items.add(q)
		account.save()
			
