from django.contrib import admin
from django.urls import path
from web.views import index,cart,orders,vip
from django.conf.urls import url,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	url(r'^$', index.index, name='index'), 
	url(r'^list/$', index.lists, name='lists'),
	url(r'^list/(?P<pIndex>[0-9]+)$', index.lists, name="lists"),# 商品列表
	url(r'^detail/(?P<gid>[0-9]+)$', index.detail, name='detail'),

	url(r'^login/$', index.login, name='login'),
	url(r'^dologin/$', index.dologin, name='dologin'),
	url(r'^logout/$', index.logout, name='logout'),
	url(r'^login/register/$', index.register, name='register'),
	url(r'^myinfo/$', index.myinfo, name='myinfo'),

	# 購物車用
	url(r'^cart$', cart.index,name='cart_index'), # 瀏覽購物車
	url(r'^cart/add/(?P<gid>[0-9]+)$', cart.add,name='cart_add'), # 添加商品入購物車
	url(r'^cart/del/(?P<gid>[0-9]+)$', cart.delete,name='cart_del'), # 刪除商品從購物車
	url(r'^cart/clear$', cart.clear,name='cart_clear'), # 清空購物車
	url(r'^cart/change$', cart.change,name='cart_change'), # 修改購物車內容
	
	# 訂單專用
    url(r'^orders/add$', orders.add,name='orders_add'), #订单的表单页
    url(r'^orders/confirm$', orders.confirm,name='orders_confirm'), #订单确认页
    url(r'^orders/insert$', orders.insert,name='orders_insert'), #执行订单添加操作

	# 會員中心
	# url(r'^vip/orders$', vip.viporders,name='vip_orders'), #会员中心我的订单
    # url(r'^vip/odstate$', vip.odstate,name='vip_odstate'), #修改订单状态（确认收货）
    # url(r'^vip/profile$', vip.profile,name='vip_profile'), #
    # url(r'^vip/profile/update/(?P<uid>[0-9]+)$', vip.update_profile,name='vip_profile_update'), #
    #url(r'^vip/info$', vip.info,name='vip_info'), #会员中心的个人信息
    #url(r'^vip/update$', vip.update,name='vip_update'), #执行修改会员信息
    #url(r'^vip/resetps$', vip.resetps,name='vip_resetps'), #重置密码表单
    #url(r'^vip/doresetps$', vip.doresetps,name='vip_doresetps'), #执行重置密码

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
