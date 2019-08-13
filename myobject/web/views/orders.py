from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse
import hashlib
from common.models import Users,Types,Goods,Orders,Detail
from django.db.models import Q
from datetime import datetime

# 公共信息加载
def loadinfo(request):
    '''公共信息加载'''
    context = {}
    lists = Types.objects.filter(pid=0)
    context['typelist'] = lists
    return context

def add(request):
	'''下订单第一步：订单表单'''
	context = loadinfo(request)
	# 获取要结算商品的id号
	ids = request.GET.get('ids','')
	if ids == '':
		context = {'info':"请选择要结算的商品！"}
		return render(request,'web/info.html',context)
	gidlist = ids.split(',')
	# 从购物车获取要结算所有商品，并放入到orderslist中，并且累计总金额
	shoplist = request.session['shoplist']
	orderslist = {}
	total = 0.0
	for gid in gidlist:
		orderslist[gid] = shoplist[gid]
		total += orderslist[gid]['price'] * orderslist[gid]['m']
	# 将这些信息放入到session中
	request.session['total'] = total
	request.session['orderslist'] = orderslist
	return render(request,"web/ordersadd.html",context)



	return render(request,"web/ordersadd.html")

def confirm(request):
	'''最後確認訂單以及商品明細'''
	context = loadinfo(request)
	return render(request,"web/ordersconfirm.html",context)

def insert(request):
    '''建立訂單'''
    context = loadinfo(request)
    try:
        # 执行订单信息添加操作
        od = Orders()
        od.uid = request.session['vipuser']['id']
        print('this is vipuser')
        print(request.session['vipuser'])
        print('this is the end')
        # {'id': 20, 'username': 'ssss', 'name': 'ssss', 'password': '8f60c8102d29fcd525162d02eed4566b', 'address': '5522 Sherbrooke ', 'phone': '7783188190', 'email': 'svmax0922@gmail.', 'state': 0}
        od.linkman = request.POST.get('linkman')
        print('od.linkman')
        od.address = request.POST.get('address')
        print('od.address')
        od.code = request.POST.get('code')
        print('od.phone')
        od.phone = request.POST.get('phone')
        print('od.phone')
        od.addtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        od.total = request.session['total']
        od.state = 0
        od.save()
        print('od.save()')

        # 执行订单详情添加
        orderslist = request.session['orderslist']
        print('shoplist')
        shoplist = request.session['shoplist']
        print('shoplist')
        # print(orderslist)
        # {'9': {'id': 9, 'typeid': 9, 'goods': '华为800手机', 'company': '华为品牌', 'price': 2680.0, 'picname': '1523417017.3019178.jpg', 'store': 30, 'num': 0, 'clicknum': 5, 'state': 1, 'm': 1}}
        # print(orderslist.values())
        # dict_values([{'id': 9, 'typeid': 9, 'goods': '华为800手机', 'company': '华为品牌', 'price': 2680.0, 'picname': '1523417017.3019178.jpg', 'store': 30, 'num': 0, 'clicknum': 5, 'state': 1, 'm': 1}])
        for shop in orderslist.values():
            
            del shoplist[str(shop['id'])]
            print("thhis is loop")
            ov = Detail()
            ov.orderid = od.id
            print("thhis is loop")
            ov.goodsid = shop['id']
            print("thhis is loop")
            #ov.name = shop['goods']
            print('this is shit')
            ov.price = shop['price']
            print('this is shit')
            ov.num = shop['m']
            print('this is shit')
            #print(ov.name)
            ov.save()
            print("this is loopend")
        del request.session['orderslist']  
        del request.session['total']
        request.session['shoplist'] = shoplist
        context = {"info":"订单添加成功！订单号："+str(od.id)}
        return render(request,"web/info.html",context)
    except Exception as err:
        print("errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        print(err)
        context = {"info":"订单添加失败，请稍后再试！"}
        return render(request,"web/info.html",context)