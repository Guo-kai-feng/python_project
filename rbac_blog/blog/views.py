from django.shortcuts import render, HttpResponse, redirect
from blog import models


def home(request):
    return render(request, 'base.html')


# 博客展示
def blog_show(request):
    blog_obj = models.Blog.objects.all()
    return render(request, 'blog_list.html', {'blog_obj': blog_obj})


# 博客删除
def del_blog(request, pk=None):
    if pk:
        models.Blog.objects.filter(id=pk).delete()
    return redirect('blog:blog_list')


# 博客新增 和 修改
from blog.forms import AlterBlogForm


def alter_blog(request, pk=None):
    obj = models.Blog.objects.filter(id=pk).first()
    title = '新增博客' if not pk else '编辑博客'
    obj_all = AlterBlogForm(instance=obj)
    if request.method == 'POST':
        obj_all = AlterBlogForm(data=request.POST, instance=obj)
        if obj_all.is_valid():
            obj_all.save()
            return redirect('blog:blog_list')
    return render(request, 'alter_blog.html', {'obj_all': obj_all, 'title': title})


# 文章展示
def article_show(request):
    article_obj = models.Article.objects.all()
    return render(request, 'article_list.html', {'article_obj': article_obj})


# 文章删除
def del_article(request, pk=None):
    if pk:
        models.Article.objects.filter(id=pk).delete()
    return redirect('blog:article_list')


# 文章新增 和 修改
from blog.forms import AlterArticleForm


def alter_article(request, pk=None):
    obj = models.Article.objects.filter(id=pk).first()
    title = '新增文章' if not pk else '编辑文章'
    obj_all = AlterArticleForm(instance=obj)
    if request.method == 'POST':
        obj_all = AlterArticleForm(data=request.POST, instance=obj)
        if obj_all.is_valid():
            obj_all.save()
            return redirect('blog:article_list')
    return render(request, 'alter_blog.html', {'obj_all': obj_all, 'title': title})
