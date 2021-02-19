from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse

from common.models import Users
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q

# 浏览会员
def index(request):

	if request.method == "GET":
		users = Users.objects
		keywords = request.GET.get('keywords', '')
		sex = request.GET.get('sex')
		print("sex:", sex)
		if keywords :
			keywords = keywords.split(" ") # split後若有空格，則會變成list類型，可多個一併查詢
			
			users = users.filter(Q(username__in=keywords)|Q(name__in=keywords))
		if sex == "0" or sex =="1" :
			users = users.filter(Q(sex__in=sex))
			# 以上在objects.filter()雖然是QuerySet, 但它是Manager ,
		users = users.all()	
		print("users: ", users)
		p = Paginator(users,5)
		page = request.GET.get('page')
		page_list = p.get_page(page)
		print("page_list: ", page_list)
		return render(request,"myadmin/users/index.html", {'page_list':page_list, "keywords":keywords, "sex":sex})

# 打開添加會員表單
def add(request):

	return render(request,"myadmin/users/add.html")

# 執行添加會員表單
import hashlib
def insert(request):
	try:
		ob = Users()
		ob.username = request.POST.get('username')
		ob.name = request.POST.get('name')
		# 获取密码并md5
		m = hashlib.md5()
		m.update(bytes(request.POST.get('password'),encoding='utf8'))
		ob.password = m.hexdigest()
		ob.sex = request.POST['sex']
		ob.address = request.POST['address']
		ob.code = request.POST['code']
		ob.phone = request.POST['phone']
		ob.email = request.POST['email']
		ob.state = 1
		ob.addtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		ob.save()
		context = {'info':'添加成功！'}
	except Exception as err:
		print(err)
		context = {'info':'添加失败！'}

	return render(request,"myadmin/info.html",context)


# 執行會員信息刪除
def delete(request,uid):
	try:
		ob = Users.objects.get(id=uid).delete()
		context = {'info':'刪除成功!'}
	except Exception as err:
		print(err)
		context = {'info':'刪除失敗!'}
	return render(request,"myadmin/info.html",context)
		
# 打開編輯會員表單
def edit(request,uid):
	try:
		ob = Users.objects.get(id=uid)
		context = {'user':ob}
		return render(request,'myadmin/users/edit.html',context)
	except Exception as err:
		print(err)
		context = {'info':'刪除失敗!'}
		return render(request,"myadmin/info.html",context)

# 執行會員編輯表單
def update(request,uid):
	try:
		ob = Users.objects.get(id=uid)
		ob.name = request.POST['name']
		ob.sex = request.POST['sex']
		ob.address = request.POST['address']
		ob.code = request.POST['code']
		ob.phone = request.POST['phone']
		ob.email = request.POST['email']
		ob.state = request.POST['state']
		ob.save()
		context = {'info':'修改成功！'}
	except Exception as err:
		print(err)
		context = {'info':'修改失败！'}
	return render(request,"myadmin/info.html",context)


from django.contrib import messages
def resetPwd(request,uid):
	if request.method == "GET":
		ob = Users.objects.get(id=uid)
		context = {'user':ob}
		return render(request,"myadmin/users/reset_pwd.html",context)
	else:
		try:
			pwd = request.POST['password']
			repwd = request.POST['repassword']
			if pwd != repwd:
				messages.info(request,"密碼輸入不一致!")
				print("密碼輸入不一致!")
				# return redirect("/myadmin/users/reset_pwd/"+uid) 
				return redirect(reverse('myadmin_users_reset_pwd',kwargs={'uid':uid}))
			md5 = hashlib.md5()
			md5.update(bytes(pwd,encoding='utf8'))
			new_pwd = md5.hexdigest()
			ob = Users.objects.filter(id=uid).update(password=new_pwd)
			context = {'info':'密碼重置成功！'}
		except Exception as err:
			print(err)
			context = {'info':'密碼重置失败！'}
		return render(request,"myadmin/info.html",context)

def search_id(request):
	pass
