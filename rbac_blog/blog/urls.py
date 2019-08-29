#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.conf.urls import url
from blog import views

urlpatterns = [

    url(r'^home/', views.home, name='home'),

    url(r'^blog_list/', views.blog_show, name='blog_list'),
    url(r'^del_blog/(\d+)/', views.del_blog, name='del_blog'),
    url(r'^add_blog/', views.alter_blog, name='add_blog'),
    url(r'^edit_blog/(\d+)/', views.alter_blog, name='edit_blog'),

    url(r'^article/', views.article_show, name='article_list'),
    url(r'^del_article/(\d+)/', views.del_article, name='del_article'),
    url(r'^add_article/', views.alter_article, name='add_article'),
    url(r'^edit_article/(\d+)/', views.alter_article, name='edit_article'),

]
