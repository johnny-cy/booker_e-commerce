from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
import hashlib
from common.models import Users, Types, Goods
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import connections
# cache
# from django.views.decorators.cache import cache_page
from django.core.cache.backends import locmem
from django.core.cache import cache


# 前台首页
# ===========================================================

def custom_sql(sql):
    with connections['mydb'].cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall() 
        return data

# @cache_page(60*60*72)
def index(request):
    # ---熱門點擊率區塊---
    # 讀取類別表
    type_obj = Types.objects
    typelist = type_obj.filter(pid=0)  # 只讀取基類pid=0 # pylint: disable=maybe-no-member
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
    # typelist_3 = Types.objects.exclude(pid=0)
    # [print(i.name) for i in typelist_3]
    typelist_3 = type_obj.filter(pid=0).values('id','name')

    # cache goodslist start---
    # get cache if exists
    cache_data = cache.get("cache_data_of_index")
    if cache_data:
        goodslist = cache_data
    else:
        goodslist = Goods.objects.raw("SELECT a.* FROM goods a WHERE 5>=(SELECT COUNT(*) FROM goods b WHERE a.typeid=b.typeid AND a.addtime>=b.addtime);") # pylint: disable=maybe-no-member
        goodslist = Goods.objects.filter(id__in=[ i.id for i in goodslist ]).values('id', 'typeid', 'goods', 'price', 'picname') # re query ids from raw to remake it as a queryset
        count_dict = {}
        for g in goodslist:
            pid = type_obj.get(id=g['typeid']).pid
            ppid = type_obj.get(id=pid).pid
            # print("ppid: ", ppid)
            if f"id_{ppid}" in count_dict.keys():
                # append
                if count_dict[f"id_{ppid}"] < 4:
                    count_dict[f"id_{ppid}"] += 1
                    g.update({"ppid": ppid})
                else:
                    g.update({"ppid": 0})
            else:
                count_dict.update({f"id_{ppid}": 0})
                g.update({"ppid": ppid})
        # 再次將goodslist 存入cache供後續使用
        cache.set("cache_data_of_index", goodslist, 60*60*24*7) # set cache for next use
    # cache goodslist end---

    context = {'typelist': typelist,
               'goods_by_click': goods_by_click,
               'goodslist': goodslist,
               'typelist_3': typelist_3,
               }
    return render(request, "web/index.html", context)


def lists(request, pIndex=1):
    t_obj = Types.objects
    tlv1 = Types.objects.filter(pid=0).values('id','path') # 第一層類別id, path  # [{'id': 162, 'path': '0'}, ...]
    tlv2 = Types.objects.filter(path__iregex='^0,[0-9]+,$').values('id','path') # 第二層類別id, path # [{'id': 162, 'path': '0,1,,'}, ...]
    tlv3 = Types.objects.filter(path__iregex='^0,[0-9]+,[0-9]+,$').values('id', 'path') # 第三層類別id, path # [{'id': 162, 'path': '0,1,2,'}, ...]

    tlv1_ids   = [ i['id'] for i in tlv1] # tlv1_ids length:  19
    tlv2_ids   = [ i['id'] for i in tlv2] # tlv2_ids length:  141
    tlv3_ids   = [ i['id'] for i in tlv3] # tlv3_ids length:  233
    tlv1_paths = [ i['path'] for i in tlv1]
    tlv2_paths = [ i['path'] for i in tlv2]
    tlv3_paths = [ i['path'] for i in tlv3]
    # 找出tid底下的goods
    context = {}
    # 獲取前端問號變數回傳的值
    tid = int(request.GET.get('tid', 0))
    orderby = request.GET.get('orderby', None)
    # 查詢根類別項目, 分類瀏覽使用
    typelist = Types.objects.filter(pid=0) # 顯示第一層類別
    # 做一個比對的字典，在類別表當中，每一個大類底下對映著那些子類，而當大類的tid傳入的時候，就把它底下的子類群列表，再拿商品表當中filter(typeid__in=子類群) 篩選出來後輸出到前端
    
    # 製作大類id列表
    typelist_tmp_parent = []
    [typelist_tmp_parent.append(i.id) for i in typelist]
    # print(typelist_tmp_parent) # [25]
    typelist_tmp_child = []
    
    # typelist_2 = Types.objects.exclude(pid=0) # 所有商品
    typelist_2 = Types.objects.filter(path=f"0,{tid},") # 顯示第二層類別
    if not typelist_2:
        typelist_2 = Types.objects.filter(pid=tid)
    [typelist_tmp_child.append(i.id) for i in typelist_2]
    # print(typelist_tmp_child) # [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44]

    context['typelist_2']= typelist_2 # type: Queryset # 第二層路徑符合的都顯示其類別
    
    
    try:
        if tid in tlv1_ids:
            print("hit tlv1, return tlv2")
            context['q_tid'] = f'tid={tid}&'
            filtered_ids = t_obj.filter(path__iregex=f"^0,{tid},").values_list('id')
            context['goodslist'] = Goods.objects.filter(typeid__in=filtered_ids)
            # get breadcrum info
            context['t_name'] = Types.objects.get(id=tid).name
        elif tid in tlv2_ids:
            print("hit tlv2, return tlv3")
            context['q_tid'] = f'tid={tid}&'
            filtered_ids = t_obj.filter(path__iregex=f"^0,[0-9]+,{tid},$").values_list('id')
            context['goodslist'] = Goods.objects.filter(typeid__in=filtered_ids)
            # get breadcrum info previous
            t_name_pid = Types.objects.get(id=tid).pid
            context['t_name_pid'] = t_name_pid
            context['t_name_prev'] = Types.objects.get(id=t_name_pid).name
            context['t_name'] = Types.objects.get(id=tid).name
        elif tid in tlv3_ids:
            print("hit tlv3, return lv3")
            context['q_tid'] = f'tid={tid}&'
            context['goodslist'] = Goods.objects.filter(typeid=tid)
            # get breadcrum info previous and pprevious
            t_name_pid = Types.objects.get(id=tid).pid
            t_name_ppid = Types.objects.get(id=t_name_pid).pid
            context['t_name_ppid'] = t_name_ppid
            context['t_name_pid'] = t_name_pid
            context['t_name_pprev'] = Types.objects.get(id=t_name_ppid).name
            context['t_name_prev'] = Types.objects.get(id=t_name_pid).name
            context['t_name'] = Types.objects.get(id=tid).name
        else:
            print("tid neither in tlv1 nor tlv2!")
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
    print(context.keys())
    return render(request, "web/list.html", context)


# 商品詳情內頁
def detail(request, gid):
    # typelist = Types.objects.filter(pid=0) # pylint: disable=maybe-no-member
    # context = {'typelist': typelist}
    goods = Goods.objects.get(id=gid) # pylint: disable=maybe-no-member
    goods.clicknum += 1  # 商品點擊數量增加
    goods.save()
    context = {'goods': goods }
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
                print("user.toDoct() as following:")
                print(user.toDict())
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


    