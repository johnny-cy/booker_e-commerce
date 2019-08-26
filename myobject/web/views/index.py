from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
import hashlib
from common.models import Users, Types, Goods
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import connections



# 前台首页
# ===========================================================

def custom_sql(sql):
    with connections['mydb'].cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall() 
        return data

def index(request):
    # ---熱門點擊率區塊---
    # 讀取類別表
    typelist = Types.objects.filter(pid=0)  # 只讀取基類pid=0 # pylint: disable=maybe-no-member
    # 獲取商品點擊數前五名的商品
    goods_obj = Goods.objects
    goods_by_click = goods_obj.all().order_by('clicknum')[:5] # pylint: disable=maybe-no-member

    # ---中間商品區塊---
    # 讀取類別表
    # typelist_2 = Types.objects.exclude(pid=0)  # 只讀取子類pid not 0
    # 從商品表中獲取現有商品的typeid
    # goodslist_tmp = goods_obj.only('typeid').all() # pylint: disable=maybe-no-member
    # temp = []
    # for goods in goodslist_tmp:
    #     if r.sadd('tmp_list', goods.typeid):
    #         temp.append(goods.typeid)
    

    # temp = []
    # for goods in goodslist_tmp:
    #     if goods.typeid not in temp:
    #         temp.append(goods.typeid)
    # print('the temp list is like '+str(temp)) # correct [2,4,10,7]
    # temp = custom_sql("SELECT DISTINCT typeid FROM goods;")
    # print(temp)
    # typelist_3 = Types.objects.filter(id__in=temp) # pylint: disable=maybe-no-member
    typelist_3 = Types.objects.exclude(pid=0)
    # [print(i.name) for i in typelist_3]
    goodslist = Goods.objects.raw("SELECT a.* FROM goods a WHERE 5>=(SELECT COUNT(*) FROM goods b WHERE a.typeid=b.typeid AND a.addtime>=b.addtime);") # pylint: disable=maybe-no-member

    context = {'typelist': typelist,
               'goods_by_click': goods_by_click,
               'goodslist': goodslist,
               'typelist_3': typelist_3,
               }
    return render(request, "web/index.html", context)


def lists(request, pIndex=1):
    context = {}
    # 獲取前端問號變數回傳的值
    tid = int(request.GET.get('tid', 0))
    orderby = request.GET.get('orderby', None)
    # 查詢根類別項目, 分類瀏覽使用
    typelist = Types.objects.filter(pid=0) 
    # 做一個比對的字典，在類別表當中，每一個大類底下對映著那些子類，而當大類的tid傳入的時候，就把它底下的子類群列表，再拿商品表當中filter(typeid__in=子類群) 篩選出來後輸出到前端
    # 製作大類id列表
    typelist_tmp_parent = []
    [typelist_tmp_parent.append(i.id) for i in typelist]
    print(typelist_tmp_parent) # [25]
    typelist_tmp_child = []
    
    typelist_2 = Types.objects.exclude(pid=0) # 所有商品
    [typelist_tmp_child.append(i.id) for i in typelist_2]
    print(typelist_tmp_child) # [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44]

    context['typelist_2']= typelist_2
    
    try:

        if tid in typelist_tmp_child:
            context['q_tid'] = 'tid='+str(tid)+'&'  # q_tid作為子類別商品查詢使用
            context['goodslist'] = Goods.objects.filter(typeid=tid) # 單一id
            context['t_name'] = Types.objects.only('name').filter(id=tid)[0].name
        elif tid in typelist_tmp_parent:
            context['q_tid'] = 'tid='+str(tid)+'&'  # q_tid作為子類別商品查詢使用
            # 父類id求其子類，必須使用0,父id
            tmp = "0,"+str(tid)+","
            tmp2 = Types.objects.filter(path=tmp) 
            context['goodslist'] = Goods.objects.filter(typeid__in=[i.id for i in tmp2]) # 多個id
        else:
            context['goodslist'] = Goods.objects.all()
        if orderby:
            context['goodslist'] = context['goodslist'].order_by(orderby)
            if '-' in orderby:
                context['q_orderby'] = 'orderby=' + \
                    orderby[1:]+'&'  # q_orderby作為依排序查詢使用 此處迴傳的有兩種可能(點擊率、價格)
            else:
                context['q_orderby'] = 'orderby=-' + \
                    orderby+'&'  # 正負號表升降冪排序，每次判斷切換
        # paginator
        paginator = Paginator(context['goodslist'],20)
        page = request.GET.get('page')
        page_list = paginator.get_page(page)
        context['goodslist'] = page_list

    except Exception as err:
        print(err)
        return HttpResponse("error...")

    return render(request, "web/list.html", context)


# 商品詳情內頁
def detail(request, gid):
    typelist = Types.objects.filter(pid=0) # pylint: disable=maybe-no-member
    context = {'typelist': typelist}
    goods = Goods.objects.get(id=gid) # pylint: disable=maybe-no-member
    goods.clicknum += 1  # 商品點擊數量增加
    goods.save()
    context['goods'] = goods
    return render(request, "web/detail.html", context)

# 前台使用者登入
# ===========================================================

def login(request):
    print("This is login")
    
    return render(request, "web/login.html")
def login_with_next(request,path):
    print("This is login with path")
    context = {"path": path}
    print(path)
    return render(request, "web/login.html", context)

def dologin(request):
    # 校验验证码
    print("DOLOGIN")
    verifycode = request.session['verifycode']
    code = request.POST['code'].upper()
    nextpage = request.POST['nextpage']
    print("this is nextpage ",nextpage)
    if verifycode != code:
        context = {'info': '验证码错误！'}
        print("验证码错误！")
        return render(request, "web/login.html", context)
    username = request.POST['username']
    password = request.POST['password']
    try:
        user = Users.objects.get(username=username) # pylint: disable=maybe-no-member
        if user.state == 0 or user.state == 1:
            im = hashlib.md5()
            im.update(bytes(password, encoding='utf-8'))
            if user.password == im.hexdigest():
                request.session['vipuser'] = user.toDict()
                # return render(request, nextpage)
                return redirect(reverse("index"))
            else:
                context = {'info': '登录密码错误！'}
        else:
            context = {'info': '此用户为非法用户！'}
    except Exception as err:
        print(err)
    return render(request, "web/login.html")


def logout(request):
    del request.session['vipuser']
    return redirect(reverse('login'))


def register(request):
    if request.method == "GET":
        return render(request, "web/register.html")
    else:
        username = request.POST['username']
        password = request.POST['password']
        repassword = request.POST['repassword']
        if password != repassword:
            context = {'info': '密碼不一致!'}
            return render(request, "web/register.html", context)
        im = hashlib.md5()
        im.update(bytes(password, encoding='utf-8'))
        password = im.hexdigest()

        Users.objects.create( # pylint: disable=maybe-no-member
            username=username, password=password, sex=0, state=0)
        request.session['vipuser'] = {'username': username}
        return redirect(reverse('index'))


def myinfo(request):
    if request.method == "GET":
        username = request.GET['username']
        ob = Users.objects.get(username=username) # pylint: disable=maybe-no-member
        context = {'ob': ob}
        return render(request, "web/myinfo.html", context)
    elif request.method == "POST":
        password = request.POST['password']
        m = hashlib.md5()
        m.update(bytes(password, encoding='utf-8'))

        ob = Users.objects.get(username=request.POST['username']) # pylint: disable=maybe-no-member
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
        return render(request, "web/info.html", context)
