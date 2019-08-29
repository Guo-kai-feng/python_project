from django.db import models

class Menu(models.Model):
    title = models.CharField(max_length=12)
    weight = models.IntegerField(default=0)
    icon = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('title','weight')
        verbose_name_plural = '一级菜单'


class Permission(models.Model):
    url = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    menus = models.ForeignKey('Menu',null=True,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True)
    url_name = models.CharField(max_length=32,unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '权限表'

class Role(models.Model):
    name = models.CharField(max_length=12)
    permissions = models.ManyToManyField(to='Permission')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '角色表'

class UserInfo(models.Model):
    roles = models.ManyToManyField(Role)
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户表'







