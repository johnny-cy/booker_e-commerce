from django.contrib import admin
from django.urls import path
from web.views import index
from django.conf.urls import url,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	#path('admin/', admin.site.urls),
	url(r'^$', index.index, name='index'),
	url(r'^list/$', index.lists, name='lists'),
	url(r'^list/(?P<pIndex>[0-9]+)$', index.lists, name="lists"),# 商品列表
	url(r'^detail/(?P<gid>[0-9]+)$', index.detail, name='detail'),
	url(r'^login/$', index.login, name='login'),
	url(r'^login/register/$', index.register, name='register'),
	url(r'^dologin/$', index.dologin, name='dologin'),
	url(r'^logout/$', index.logout, name='logout'),
	url(r'^myinfo/$', index.myinfo, name='myinfo'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
