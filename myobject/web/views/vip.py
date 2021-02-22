from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect,reverse
from common.models import Goods,Types,Orders,Detail,Users
from datetime import datetime
import hashlib
from django.core.paginator import Paginator
from django.db.models import Q
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import html

MAIL_SERVER_ADDR_ = "smtp.gmail.com"
MAIL_SERVER_SSL_PORT_ = 465
MAIL_SERVER_STARTTLS_PORT_ = 587
SENDER_ = "smtplibmail01"
SENDER_PASSWD_ = "thisissick123"
RECEIVER_ = ["smtplibmail01@gmail.com",]

# 公共郵件寄送加載
def send_smtp_ssl(msg):
	# create an instance with server addr and port.
	server = smtplib.SMTP_SSL(MAIL_SERVER_ADDR_, MAIL_SERVER_SSL_PORT_)
	# login with mail account/password.
	server.login(SENDER_, SENDER_PASSWD_)
	# sendmail with addr of sender, receiver and message to send out.
	server.sendmail(SENDER_, RECEIVER_, msg)
	# disconnect
	server.quit()
	print("send_smtp_SSL success!")

# 公共信息加载
def loadinfo(request):
    '''公共信息加载'''
    context = {}
    lists = Types.objects.filter(pid=0)
    context['typelist'] = lists
    return context

def viporders(request):
	context = loadinfo(request)
	# 用登錄者id去查找訂單
	odlist = Orders.objects
	odlist = odlist.filter(uid=request.session['vipuser']['id'])
	# print result = <QuerySet [<Orders: Orders object (20180005)>, <Orders: Orders object (20180006)>]>
	# 獲取前台回傳的state
	state = request.GET.get('state',0)
	if state != 0:
		# 將odlist再過濾第二次
		odlist = odlist.filter(state=state)
	# 遍歷訂單
	for od in odlist:
		# 用訂單id去查找詳情, 並存入detaillist
		detaillist = Detail.objects.filter(orderid=od.id)
		# detaillist = Detail.objects.all()
		print("detillist ...")
		print(detaillist)
		# 遍歷詳情，並放入商品模塊中的picname到詳情內
		for g in detaillist:
			print("g:", g, g.goodsid)
			
			g.picname = Goods.objects.get(id=g.goodsid).picname
			print("this is g.pickname = "+g.picname)
		# 將新的詳情加入odlist當中，屬性名稱同為detaillist

		od.detaillist = detaillist
	paginator = Paginator(odlist,5)
	page = request.GET.get('page')
	page_list = paginator.get_page(page)

	context['orderslist'] = page_list
	return render(request,'web/viporders.html',context)

def odstate(request):
	try:
		oid = request.GET.get('oid','0')
		a = Orders.objects.get(id=oid)
		a.state = request.GET.get('state')
		a.save()
		return redirect(reverse('vip_orders'))
	except Exception as err:
		print(err)
		return HttpResponse("訂單處理失敗!")

def profile(request):
	user = Users.objects.filter(username=request.session['vipuser']['username'])
	context = {'user':user}
	return render(request,"web/vipprofile.html", context)

from django.contrib import messages
def update_profile(request,uid):
	'''加载编辑信息页面'''
	try:
		print('start')
		user = Users.objects.get(id=uid)
		user.name = request.POST['name']
		user.phone = request.POST['phone']
		user.email = request.POST['email']
		user.address = request.POST['address']
		user.sex = request.POST['sex']
		if request.POST['password'] :
			pwd = request.POST['password']
			repwd = request.POST['repassword']
			if pwd != repwd:
				messages.info(request,"密碼輸入不一致!")
				return redirect(reverse('vip_profile'))
			m = hashlib.md5()
			m.update(bytes(request.POST['password'], encoding="utf8"))
			user.password = m.hexdigest()
		user.save()
		context = {"user":user}
		context["info"] = "個人信息修改成功! "
		return render(request,"web/vipprofileinfo.html",context)
	except Exception as err:
		context={"info":"没有找到要修改的信息！"}
		return render(request,"web/vipprofileinfo.html",context)

def feedback(request):
	if request.method == 'GET':
		
		return render(request, "web/feedback.html")
	elif request.method == 'POST':
		print("get in post")
		myajax_content = html.unescape(request.POST.get('content'))
		
		message = MIMEMultipart()
		message['From'] = Header(r"BOOKER網", "utf-8")
		message['To'] = Header(r"", "utf-8")
		message['Subject'] = Header(r"從網站內寄出的反饋意見，來自"+request.session['vipuser']['username'], "utf-8")
		message.attach(MIMEText(myajax_content, 'html','utf-8')) 
		print("before send_smtp_ssl....")
		send_smtp_ssl(message.as_string())
		context = {"info" : "謝謝您的反饋，我們將竭誠為您服務！"}
		print("before render...")
		return render(request,"web/info.html",context)
