from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from common.models import Goods,Users,Types

'''公共信息加载函数'''
def loadinfo(request):
    lists = Types.objects.filter(pid=0)
    context = {'typelist':lists}
    return context

'''查看購物車信息'''
def index(request):
    context = loadinfo(request)
    if 'vipuser' not in request.session:
        return render(request,"web/login.html",context)
    elif 'shoplist' not in request.session:
    	request.session['shoplist']={}
    return render(request,"web/cart.html",context)

'''分頁瀏覽購物車中商品信息'''
def add(request,gid):
    goods = Goods.objects.get(id=gid)
    shop = goods.toDict()
    shop['m'] = int(request.POST.get("m",1))
    shoplist = request.session.get("shoplist",{})
    #判断购物车中是否已存在要购买的商品
    if gid in shoplist:
        shoplist[gid]['m'] += shop['m'] #累加购买量
    else:
        shoplist[gid] = shop
    #将购物车中的商品信息放回到session中
    request.session['shoplist'] = shoplist
    #跳转查看购物车
    return redirect(reverse('cart_index'))

'''從購物車刪除商品信息'''
def delete(request,gid):
    shoplist = request.session['shoplist']
    del shoplist[gid]
    request.session['shoplist'] = shoplist
    return redirect(reverse('cart_index'))

'''清空購物車信息'''
def clear(request):
    request.session['shoplist'] = {}
    return redirect(reverse('cart_index'))

'''更改購物車商品信息'''
def change(request):
    shoplist = request.session['shoplist']
    shopid = request.GET.get("gid",0)
    num = int(request.GET.get('num',1))
    if num < 1:
        num = 1
    shoplist[shopid]['m'] = num
    request.session['shoplist'] = shoplist
    return redirect(reverse('cart_index'))
