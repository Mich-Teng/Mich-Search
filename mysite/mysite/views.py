import sys  
 
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from mysite.forms import *
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.template import RequestContext
from account.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from bs4 import BeautifulSoup
import urllib2
import urllib
import chardet
import string
import re
import spynner
from ItemList.models import *
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage

#-*- coding: UTF-8 -*-




class Item():
	item_src=''
	pic_src = ''
	item_price=0.0
	item_name=''
	source=''
	item_layout = 0

	def __init__(self,item_src,pic_src,item_price,item_name,source):
		self.item_src=item_src
		self.pic_src=pic_src
		self.item_price=string.atof(item_price)
		self.item_name=item_name
		self.source=source
	
def SearchAll(request,url):
	item_list = {}
	item_list = SearchTaobao(request,url)
	item_list2 = SearchDangDang(request,url)
	item_list3 = SearchAmazon(request,url)
	item_list4 = SearchJingDong(request,url)
	item_list.extend(item_list2)
	item_list.extend(item_list3)
	item_list.extend(item_list4)

	return item_list

def SortResult(item_list):
	item_list.sort(key=lambda x:x.item_price)
	return item_list


def StoreResult(query,item_list):
	try:
		ItemList.objects.get(key_word = query)
	except:
		a = ItemList(key_word = query)
		a.save()
		for item in item_list:
			p = Item_db(item_src=item.item_src,pic_src = item.pic_src,item_name = item.item_name,item_price = item.item_price,source = item.source)
			p.save()
			a.item_list.add(p)
		a.save()


def Search(request,url):
	item_list={}
	func = {'taobao':SearchTaobao,'dangdang':SearchDangDang,'amazon':SearchAmazon,'jingdong':SearchJingDong,'all':SearchAll}
	url = url.encode('utf8')
	query = url[url.find('q=')+2:url.find('&src')]
	scope = url[url.find('src=')+4:url.find('&page')]
	
	try:
		ItemList.objects.get(key_word = query).item_list
		item_list = getData(scope,query)
	except:
		query = query.decode('utf8')	
		item_list= func.get(scope)(request,query)
		item_list = SortResult(item_list)
		StoreResult(query,item_list)
		
	return item_list
	
	# save item_list in the database


def getData(src,url):
	data =  ItemList.objects.get(key_word = url).item_list
	if src == "all":
		ret = data.all()
	else:
		ret = data.filter(source = src)
	return ret


def SearchView(request):
	i=0
	user = request.user
	authenticated=request.user.is_authenticated
	if request.method == 'POST':
		if request.POST.has_key('user_name_log') and request.POST.has_key('password_log'):
			return	BaseOperation(request,'search_result.html')
		else:
			search_content = request.POST['q']
			query = "/search ?q="+search_content+"&src=all&page=1"
			item_list = Search(request,query)
			
			return HttpResponseRedirect(query)
	else:
		#get the data from database

		item_list=[]
		url = request.GET['q']
		full_url = request.get_full_path()
		ret = getData(request.GET['src'],url)
		for p in ret:
			tmp = Item(item_src=p.item_src,pic_src=p.pic_src,item_name=p.item_name,source=p.source,item_price = p.item_price)
			tmp.item_layout = i%4
			item_list.append(tmp)
			i=i+1

		if i%4 == 0:
			line = True
		else:
			line = False


		url_src_prefix =  full_url[:full_url.find('&src=')]
		url_page_prefix = full_url[:full_url.find('&page=')]
		after_range_num = 5
		befor_range_num = 4
		debug = url
		try:
			page = int(request.GET['page'])
			if page < 1:
				page = 1
		except ValueError:
			page = 1
		paginator = Paginator(item_list,24)
		try:                 
			item_array = paginator.page(page)
		except(EmptyPage,InvalidPage,PageNotAnInteger):
			item_array = paginator.page(paginator.num_pages)
		if page >= after_range_num:
			page_range = paginator.page_range[page-after_range_num:page+befor_range_num]
		else:
			page_range = paginator.page_range[0:int(page)+befor_range_num]
		dictionary = {'item_list':item_array,'page_range':page_range,'item_array':item_array,'url_src_prefix':url_src_prefix,'url_page_prefix':url_page_prefix,'authenticated':authenticated,'user':request.user,'line':line}
		return render_to_response('search_result.html',dictionary)


def SearchJingDong(request,url):
	url = url.encode('utf8')
	url = urllib2.quote(url)
	query_url =  "http://search.jd.com/Search?keyword="+url+"&enc=utf-8"
	browser = spynner.Browser()
	try:  
		browser.load(url=query_url, load_timeout=120, tries=1)  
	except spynner.SpynnerTimeout:   
		print 'Timeout.' 
	
#	html_content = urllib.urlopen(query_url).read()
	html_content = browser.html
	soup = BeautifulSoup(html_content, "html.parser")
	items=[]
	for i in range(0,36):
		try:
			item_src = soup.find_all(attrs={"class":'p-img'})[i].find('a')['href']
			pic_src = soup.find_all(attrs={"class":'p-img'})[i].find('img')['data-lazyload']
			item_name = unicode(soup.find_all(attrs={"class":'p-name'})[i].find('a').contents[0])
			l_price =  soup.find_all(attrs={"class":'p-price'})
			item_price = unicode(soup.find_all(attrs={"class":'p-price'})[i].find('strong').contents[0])
			item_price = re.findall(r'\d+.[0-9]*',item_price)[0]
			source = "jingdong"
			#each div is a item-box, store it into form and show it out
			tmp=Item(item_src,pic_src,item_price,item_name,source)
			items.append(tmp)
		except:
			break
	return items


def SearchDangDang(request,url):
	#url = request.GET['q']
	url = url.encode('gbk')
#	url = url.decode('utf8').encode('gb2312')
	query_url = "http://search.dangdang.com/?key="+url
	html_content = urllib.urlopen(query_url).read().decode('gbk')
	soup = BeautifulSoup(html_content, "html.parser")
	content = soup.find_all(attrs={"class": "inner"})
	items=[]
	del content[0]
	for div in content:
		try:
			item_src = div.find(attrs={"class": "pic"})['href']
			pic_src =div.find(attrs={"class": "pic"}).find('img')['src']
			item_price =unicode(div.find(attrs={"class": "price_n"}).contents[0])[1:]
			item_price = item_price[:item_price.find(" ")]
			item_name = div.find(attrs={"class": "name"}).find('a')['title']
			source = "dangdang"
			#each div is a item-box, store it into form and show it out
			tmp=Item(item_src,pic_src,item_price,item_name,source)
			items.append(tmp)
		except:
			break

	return items


def SearchAmazon(request,url):
	url = url.encode('utf8')
	query_url ="http://www.amazon.cn/s/field-keywords="+url
	html_content = urllib2.urlopen(query_url).read()
	soup = BeautifulSoup(html_content, "html.parser")
	
	items=[]
	for i in range(0,16):
		try:
			q_str = "result_"+str(i)
			content = soup.find_all(attrs={"id": q_str})
			item_src = content[0].find('a')['href']
			pic_src = content[0].find('img')['src']
			item_name = unicode(content[0].find_all(attrs={"class":"productTitle"})[0].find('a').contents[0])
			item_price = unicode(content[0].find_all(attrs={"class":"newPrice"})[0].find('span').contents[0])
			item_price = re.findall(r'\d+.[0-9]*',item_price)[0]
			item_price = item_price.replace(',','')
			source = "amazon"
			#each div is a item-box, store it into form and show it out
			tmp=Item(item_src,pic_src,item_price,item_name,source)
			items.append(tmp)
		except:
			break

	return items

def SearchTaobao(request,url):
	url = url.encode('gb2312')
	url = urllib2.quote(url)
	query_url = "http://s.taobao.com/search?q="+ url
	html_content = urllib2.urlopen(query_url).read().decode('gb2312','ignore')
	soup = BeautifulSoup(html_content, "html.parser")
	content = soup.find_all(attrs={"class": "item-box"})
	items=[]
	for div in content:
		try:
			item_src = div.find(attrs={"class": "pic-box"}).find('a')['href']
			pic_src = div.find(attrs={"class": "pic-box"}).find('img')['src']
			item_price = unicode(div.find(attrs={"class": "col price"}).contents[0])[1:]
			item_price = re.findall(r'\d+.[0-9]*',item_price)[0]
			item_name = div.find(attrs={"class": "summary"}).find("a")['title'].encode('utf8')
			source = "taobao"
			#each div is a item-box, store it into form and show it out
			tmp=Item(item_src,pic_src,item_price,item_name,source)
			items.append(tmp)
		except:
			break

	return items


def BaseOperationWithForm(request,path,form):
	dic = {'index':1,'about':2,'contact':3}
	index = dic[path[:path.find('.')]]
	if request.method == 'POST':
		user = auth.authenticate(username=request.POST['user_name_log'], password=request.POST['password_log'])
		if user:
			auth.login(request, user)
			authenticated=True
			info =""
		else:
			info = "Invalid Account!"
			authenticated=False
		return render_to_response(path,{'index':index,'authenticated':authenticated,'user':request.user,'info':info,'form':form})	
	else:
		authenticated=request.user.is_authenticated	
		return render_to_response(path,{'authenticated':authenticated,'user':request.user,'form':form,'index':index})


def BaseOperation(request,path):
	dic = {'index':1,'about':2,'contact':3}
	index = dic[path[:path.find('.')]]
	if request.method == 'POST':
		user = auth.authenticate(username=request.POST['user_name_log'], password=request.POST['password_log'])
		if user:
			auth.login(request, user)
			authenticated=True
			info =""
		else:
			info = "Invalid Account!"
			authenticated=False
		return render_to_response(path,{'authenticated':authenticated,'user':request.user,'info':info,'index':index})	
	else:
		authenticated=request.user.is_authenticated	
		return render_to_response(path,{'authenticated':authenticated,'user':request.user,'index':index})

def index(request):
	if request.method == 'POST' and request.POST.has_key('search'):
		content = request.POST['search_form']
		query = "/search ?q="+content+"&src=all&page=1"
		item_list = Search(request,query)
		return HttpResponseRedirect(query)
		
	else:
		return BaseOperation(request,'index.html')


def about(request):
	return BaseOperation(request,'about.html')

def detail(request):
	#get the user info
	user = request.user
	authenticated = user.is_authenticated
	try :
		profile=user.get_profile()
		initial={'name':profile.name,'city':profile.city,'province':profile.province,'country':profile.country,'description':profile.description}
		tmp = parseFavorite(profile.favorite)
		if tmp != None:
			for i in range(profile.count):
				str_name = "Favorite"+str(i+1)
				initial[str_name]=tmp[i]
	except:
		profile= Account(user=user)
		profile.save()
		profile=user.get_profile()
		initial={}

		
	form = DetailForm(initial=initial,c={'count':profile.count+1})	

	if request.method == 'POST':
		if request.POST.has_key('user_name_log') and request.POST.has_key('password_log'):
			return	BaseOperationWithForm(request,'details.html',form)	
		else:
			try:
				num = 0
				index=1
				favorite=[]
				while True:
					tmp =  request.POST['Favorite'+str(index)]
					if tmp.strip():
						favorite.append(tmp)
						num = num +1
					index=index+1

			except:
				i=0
				profile.favorite=""
				for i in range(num):
					profile.favorite+=(favorite[i]+";")
				profile.count=num

			form = DetailForm(request.POST,c={'count':profile.count+1})
			if form.is_valid():		
				cd = form.cleaned_data
				profile.name=cd['name']
				profile.city=cd['city']
				profile.province=cd['province']
				profile.country=cd['country']
				profile.description=cd['description']
				profile.save()
				return HttpResponseRedirect('/index/')
	return render_to_response('details.html',{'index':5,'form':form,'uname':user.username,'email':user.email,'authenticated':authenticated,'user':user,'count':profile.count+1})

def register(request):
	user = request.user
	authenticated=request.user.is_authenticated
	form = RegisterForm()
	if request.method == 'POST':
		if request.POST.has_key('user_name_log') and request.POST.has_key('password_log'):
			return BaseOperationWithForm(request,'register.html',form)
		else:
			form = RegisterForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
			#register the user info in the database here and jump to finish page
				try:
					User.objects.get(username=cd['user_name']) 
					user_error='user_name has already existed!'
					return render_to_response('register.html',{'user_error':user_error,'form':form})
				except:
					print 'a'
				try:
					User.objects.get(username=cd['email']) 
					user_error='email has already existed!'
					return render_to_response('register.html',{'email_error':user_error,'form':form})
				except:
					print 'a'
				user = User.objects.create_user(cd['user_name'],cd['email'], cd['password']) 
				user.save()
				user = auth.authenticate(username=cd['user_name'], password=cd['password'])
				if user:
					auth.login(request, user)
	
				return HttpResponseRedirect('/details/')
			#return render_to_response('details.html',{'debug':profile})					
	return render_to_response('register.html', {'form': form,'authenticated':authenticated,'user':request.user})


def contact(request):
	user = request.user
	authenticated=request.user.is_authenticated
	form = ContactForm()
	if request.method == 'POST':
		if request.POST.has_key('user_name_log') and request.POST.has_key('password_log'):
			return BaseOperationWithForm(request,'contact.html',form)
		else:
			form = ContactForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				send_mail(
					cd['subject'],
					cd['message'],
					cd.get('email','tengchao1992@gmail.com'),
					['MichZc.Teng@gmail.com'],
				)
				return render_to_response('thanks.html',
                              	Context(),
                              	context_instance=RequestContext(request))
			#return HttpResponseRedirect('thanks.html')
	else:
		
		return render_to_response('contact.html', {'form': form,'index':3,'authenticated':authenticated,'user':user})

def log_out(request):
	logout(request)
	return HttpResponseRedirect('/index/')


def create_form(request):
	profile = request.user.get_profile()
	f_list = parseFavorite(profile.favorite)
	form = DetailForm(None,c=profile.count)
	return form

def parseFavorite(favorite):
	try:
		tmp = favorite.split(';')
		return tmp
	except:
		print 'no favorite'


def favoriteView(request):
	user = request.user
	url_full = request.get_full_path()
	url_prefix = url_full[:url_full.find('favorite')+8]
	authenticated = user.is_authenticated
	profile=user.get_profile()
	count = profile.count
	tmp = parseFavorite(profile.favorite)
	favor_list=[]
	
	
	if tmp != None:
		for i in range(profile.count):
			favor_list.append(tmp[i])
	if url_full.find('?') != -1:
		url_src_prefix = url_full[:url_full.find('&src')]
		url_page_prefix = url_full[:url_full.find('&page')]

		item_list=[]
		favor_item = request.GET['q']
		ret = profile.favor_items.get(key_word = favor_item).item_list
		i=0
		src = request.GET['src']
		if src == "all":
			ret = ret.all()
		else:
			ret = ret.filter(source = src)
		for p in ret:
			tmp = Item(item_src=p.item_src,pic_src=p.pic_src,item_name=p.item_name,source=p.source,item_price = p.item_price)
			tmp.item_layout = i%4
			item_list.append(tmp)
			i=i+1


		after_range_num = 5
		befor_range_num = 4
		try:
			page = int(request.GET['page'])
			if page < 1:
				page = 1
		except ValueError:
			page = 1
		paginator = Paginator(item_list,24)
		try:                 
			item_array = paginator.page(page)
		except(EmptyPage,InvalidPage,PageNotAnInteger):
			item_array = paginator.page(paginator.num_pages)
		if page >= after_range_num:
			page_range = paginator.page_range[page-after_range_num:page+befor_range_num]
		else:
			page_range = paginator.page_range[0:int(page)+befor_range_num]
		return render_to_response('favorite.html',{'selected':1,'index':4,'url_page_prefix':url_page_prefix,'item_list':item_array,'count':count,'favor_list':favor_list,'authenticated':authenticated,'page_range':page_range,'url_src_prefix':url_src_prefix,'user':request.user})
	else:
		return  render_to_response('favorite.html',{'selected':0,'index':4,'count':count,'favor_list':favor_list,'authenticated':authenticated,'url_src_prefix':url_prefix,'user':request.user})

	
