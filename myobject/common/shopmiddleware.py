# 自定义中间件类
from django.shortcuts import redirect,reverse

import re

class ShopMiddleware(object):
	def __init__(self,get_response):
		self.get_response = get_response
		# One-time configuration and initialization(一次性配置和初始化).

	def __call__(self,request):
		
		# 定义网站后台不用登录也可访问的路由url
		urllist = ['/myadmin/login','/myadmin/dologin','/myadmin/logout','/myadmin/verify']
		# 获取当前请求路径
		path = request.path
		# 判断当前请求是否是访问网站后台,并且path不在urllist中
		if re.match("/myadmin",path) and path not in urllist:
			# 判断当前用户是否没有登录
			if 'adminuser' not in request.session:
				return redirect(reverse('myadmin_login'))
		
		response = self.get_response(request)
		# Code to be executed for each request/response after
		# the view is called.
		
		return response
		

class FeedbackMiddleware(object):
	def __init__(self,get_response):
		self.get_response = get_response

	def __call__(self,request):
		
		# 定义网站前台登入時才可以訪問的路由url
		urllist = ['/booker/vip/feedback/', '/booker/vip/orders/']
		# 获取当前请求路径
		path = request.path
		# 判断当前path是否在urllist中
		if path in urllist:
			# 判断当前用户是否有登录，若沒則跳轉登入頁面 
			if 'vipuser' not in request.session:
				print("vipuser not in session..redirect to login")
				return redirect(reverse('login')) # 順便回傳當前的request.path，登入之後方便直接回來
		
		response = self.get_response(request)
		
		return response
		