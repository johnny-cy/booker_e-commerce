from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect,reverse
from common.models import Goods,Types,Orders,Detail
from datetime import datetime

# 公共信息加载
def loadinfo(request):
    '''公共信息加载'''
    context = {}
    lists = Types.objects.filter(pid=0)
    context['typelist'] = lists
    return context

def viporders(request):
	context = loadinfo(request)
	odlist = Orders.objects.filter(uid=request.session['vipuser']['id'])
	for od in odlist:
		dlist = Detail.objects.filter(orderid=od.id)
		for og in dlist:
			og.picname = Goods.objects.only('picname').get(id=og.goodsid).picname
		od.detaillist = dlist

	context['orderslist'] = odlist

	return render(request,"web/viporders.html",context)

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




