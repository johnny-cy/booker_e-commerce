from django.db import models
from datetime import datetime
from DjangoUeditor.models import UEditorField
'''
class Article(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    content = UEditorField(width=600, height=300, toolbars="full", imagePath="imagessss/", filePath="files/",upload_settings={"imageMaxSize":1204000}, settings={}, verbose_name='内容', default="")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='发表时间')

    class Meta:
        db_table ='Article'
        verbose_name ='文章'
        verbose_name_plural = verbose_name
'''


#用户信息模型
class Users(models.Model):
	username = models.CharField(max_length=32)
	name = models.CharField(max_length=16)
	password = models.CharField(max_length=32)
	sex = models.IntegerField(default=1)
	address = models.CharField(max_length=255)
	code = models.CharField(max_length=6)
	phone = models.CharField(max_length=16)
	email = models.CharField(max_length=50)
	state = models.IntegerField(default=1)
	addtime = models.DateTimeField(default=datetime.now)

	def toDict(self):
		return {'id':self.id,'username':self.username,'name':self.name,'password':self.password,'address':self.address,'phone':self.phone,'email':self.email,'state':self.state}


	class Meta:
		db_table = "users"  # 更改表名

		
#商品类别信息模型
class Types(models.Model):
    name = models.CharField(max_length=32)
    pid = models.IntegerField(default=0)
    path = models.CharField(max_length=255)

    class Meta:
        db_table = "type"  # 更改表名

#商品信息模型
class Goods(models.Model):
    typeid = models.IntegerField()
    goods = models.CharField(max_length=32)
    company = models.CharField(max_length=50)
    content = models.CharField(max_length=255)
    price = models.FloatField()
    picname = models.CharField(max_length=255)
    store = models.IntegerField(default=0)
    num = models.IntegerField(default=0)
    clicknum = models.IntegerField(default=0)
    state = models.IntegerField(default=1)
    addtime = models.DateTimeField(default=datetime.now)

    def toDict(self):
        return {'id':self.id,'typeid':self.typeid,'goods':self.goods,'company':self.company,'price':self.price,'picname':self.picname,'store':self.store,'num':self.num,'clicknum':self.clicknum,'state':self.state}

    class Meta:
        db_table = "goods"  # 更改表名


