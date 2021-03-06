# 自定义中间件类
from django.shortcuts import render,redirect,reverse
import re

# class MyadminPagesMiddleware(object):
# 	def __init__(self,get_response):
# 		self.get_response = get_response
# 		# One-time configuration and initialization(一次性配置和初始化).

# 	def __call__(self,request):
		
# 		# 定义网站后台不用登录也可访问的路由url
# 		# urllist = ['/myadmin/login','/myadmin/dologin','/myadmin/logout','/myadmin/verify']
# 		# 获取当前请求路径
# 		path = request.path
# 		print(path)
# 		# 判断当前请求是否是访问网站后台,并且path不在urllist中
# 		# if re.match("^/booker/myadmin/",path):
# 		# 	# 判断当前用户是否没有登录
# 		# 	if 'adminuser' not in request.session:
# 		# 		return redirect(reverse('myadmin_login'))
# 		# 	else:
# 		# 		print(request.session['adminuser'])
		
# 		response = self.get_response(request)
# 		# Code to be executed for each request/response after
# 		# the view is called.
		
# 		return response
		

class VIPPagesMiddleware(object):
	def __init__(self,get_response):
		self.get_response = get_response

	def __call__(self,request):
		print('vippagesmiddleware')
		# 定义网站前台登入時才可以訪問的路由url
		urllist = ['/booker/vip/feedback/', '/booker/vip/orders/']
		urllist_pass_myadmin = ['login','dologin','logout','verify']
		# 获取当前请求路径
		path = request.path
		print(path)
		# 判断当前path是否在urllist中
		if re.match('^/booker/vip/', path):
			if 'vipuser' not in request.session:
				print("vipuser not in session..redirect to login")
				return redirect(reverse('login')) # 順便回傳當前的request.path，登入之後方便直接回來
		elif re.match('^/booker/myadmin/', path) and not any(i in path for i in urllist_pass_myadmin):
			if 'adminuser' not in request.session:
				print("adminuser not found")
				return render(request,'myadmin/login.html')

		# 	if 'adminuser' not in request.session:
		# 		return render(request,'myadmin/login.html')
				# return redirect(reverse('myadmin_login'))
		# if path in urllist:
		# 	# 判断当前用户是否有登录，若沒則跳轉登入頁面 
		# 	if 'vipuser' not in request.session:
		# 		print("vipuser not in session..redirect to login")
		# 		return redirect(reverse('login')) # 順便回傳當前的request.path，登入之後方便直接回來
		
		response = self.get_response(request)
		
		return response
		