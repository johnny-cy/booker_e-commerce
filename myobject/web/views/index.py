from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse
import hashlib
from common.models import Users,Types,Goods
from django.db.models import Q




#前台首页
#===========================================================
def index(request):
	list = Types.objects.filter(pid=0)
	# 獲取商品點擊數前五名的商品
	goods_by_click = Goods.objects.all().order_by('clicknum')[:5]
	ty = Types.objects.only('id').filter(pid=1)
	# 獲取衣服底下的所有子類別商品，取4條數據
	cloth_by_addtime = Goods.objects.filter(typeid__in=ty).order_by('addtime')[:4]
	ty = Types.objects.only('id').filter(pid=2)
	# 獲取數碼底下的所有子類別商品，取4條數據
	digits_by_addtime = Goods.objects.filter(typeid__in=ty).order_by('addtime')[:4]

	context = {'typelist':list,
		'goods_by_click':goods_by_click,
		'cloth_by_addtime':cloth_by_addtime,
		'digits_by_addtime':digits_by_addtime,
		}
	return render(request,"web/index.html",context)

def lists(request,pIndex=1):
	
	# 獲取前端問號變數回傳的值
	tid = int(request.GET.get('tid',0))
	orderby = request.GET.get('orderby',None)

	# 查詢根類別項目, 分類瀏覽使用
	list = Types.objects.filter(pid=0)
	context = {'typelist':list}

	# 查詢所有商品
	goodslist = Goods.objects.all()
	context['goodslist'] = goodslist

	try:
		if tid > 0:
			a = Types.objects.filter(pid=tid)
			b = Goods.objects.filter(typeid__in=a)
			context['goodslist'] = b
			context['q_tid'] = 'tid='+str(tid)+'&'  # q_tid作為子類別商品查詢使用
		if orderby:
			a = context['goodslist'].order_by(orderby)
			context['goodslist'] = a
			if '-' in orderby:
				context['q_orderby'] = 'orderby='+orderby[1:]+'&' # q_orderby作為依排序查詢使用
			else:
				context['q_orderby'] = 'orderby=-'+orderby+'&' # 正負號表升降冪排序，每次判斷切換
	except Exception as err:
		print(err)
		return HttpResponse("error...")
	return render(request,"web/list.html",context)



# 商品詳情內頁
def detail(request,gid):
	list = Types.objects.filter(pid=0)
	context = {'typelist':list}
	goods = Goods.objects.get(id=gid)
	goods.clicknum +=1 # 商品點擊數量增加
	goods.save()
	context['goods'] = goods
	return render(request,"web/detail.html",context)

#前台使用者登入
#===========================================================
def login(request):
	return render(request,"web/login.html")

def dologin(request):
	# 校验验证码
	print("DOLOGIN")
	verifycode = request.session['verifycode']
	code = request.POST['code']
	if verifycode != code:
		context = {'info':'验证码错误！'}
		print("验证码错误！")
		return render(request,"web/login.html",context)
	username = request.POST['username']
	password = request.POST['password']
	try:
		user = Users.objects.get(username=username)
		if user.state == 0 or user.state == 1:
			im = hashlib.md5()
			im.update(bytes(password,encoding='utf-8'))
			if user.password == im.hexdigest():
				request.session['vipuser'] = user.toDict()
				#return render(request,"web/index.html",context)
				return redirect(reverse("index"))
			else:
				context = {'info':'登录密码错误！'}
		else:
			context = {'info':'此用户为非法用户！'}
	except Exception as err:
		print(err)
	return render(request,"web/login.html")
		

def logout(request):
	del request.session['vipuser']
	return redirect(reverse('login'))

def register(request):
	if request.method == "GET":
		return render(request,"web/register.html")
	else:
		username = request.POST['username']
		password = request.POST['password']
		repassword = request.POST['repassword']
		if password != repassword:
			context = {'info':'密碼不一致!'}
			return render(request,"web/register.html",context)
		im = hashlib.md5()
		im.update(bytes(password,encoding='utf-8'))
		password = im.hexdigest()
		Users.objects.create(username=username,password=password,sex=0,state=0)	
		request.session['vipuser'] = {'username':username}
		return redirect(reverse('index'))

def myinfo(request):
	if request.method == "GET":
		username = request.GET['username']
		ob = Users.objects.get(username=username)
		context = {'ob':ob}
		return render(request,"web/myinfo.html",context)
	elif request.method == "POST":
		password = request.POST['password']
		m = hashlib.md5()
		m.update(bytes(password,encoding='utf-8'))
		
		ob = Users.objects.get(username=request.POST['username'])
		if m.hexdigest() == ob.password:
			ob.name = request.POST['name']
			ob.sex = request.POST['sex']
			ob.address = request.POST['address']
			ob.phone = request.POST['phone']
			ob.email = request.POST['email']
			ob.save()
			context = {'info': '更新已完成!'}
		else:
			context = {'info': " 密碼輸入錯誤!"}
		return render(request,"web/info.html",context)