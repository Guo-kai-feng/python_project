from rbac import models
from django.db.models import Q
from django import forms
from rbac.serve.permissions import init_permission
from django.shortcuts import render, HttpResponse, redirect


def role_list(request):
    all_roles = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'all_roles': all_roles})


class RoleForm(forms.ModelForm):
    class Meta:
        model = models.Role
        fields = '__all__'
        exclude = ['permissions', ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


def role_add_edit(request, rid=None):
    role_obj = models.Role.objects.filter(pk=rid).first()
    if request.method == 'GET':
        form_obj = RoleForm(instance=role_obj)

        return render(request, 'rbac/form.html', {'form_obj': form_obj})
    else:
        form_obj = RoleForm(request.POST, instance=role_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('rbac:role_list')
        else:
            return render(request, 'rbac/form.html', {'form_obj': form_obj})


def role_del(request, rid):
    models.Role.objects.filter(pk=rid).delete()
    return redirect('rbac:role_list')


def menu_list(request):
    mid = request.GET.get('mid')

    all_menus = models.Menu.objects.all()
    if mid:
        all_permissions = models.Permission.objects.filter(Q(menus_id=mid) | Q(parent__menus_id=mid)).values('id',
                                                                                                             'url',
                                                                                                             'title',
                                                                                                             'menus__title',
                                                                                                             'menus_id',
                                                                                                             'parent_id',
                                                                                                             'parent__title',
                                                                                                             'url_name')
    else:
        all_permissions = models.Permission.objects.all().values('id', 'url', 'title', 'menus_id', 'parent_id',
                                                                 'menus__title', 'parent__title', 'url_name')

    permission_dict = {}
    for i in all_permissions:
        if i.get('menus_id'):
            permission_dict[i['id']] = i
            i['children'] = []
    for k in all_permissions:
        pid = k.get('parent_id')
        if pid:
            permission_dict[pid]['children'].append(k)

    return render(request, 'rbac/menu_list.html',
                  {'all_menus': all_menus, 'permission_dict': permission_dict.values(), 'mid': mid})


from rbac.icon_data import icon_list
from django.utils.safestring import mark_safe


class MenuForm(forms.ModelForm):
    class Meta:
        model = models.Menu
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.RadioSelect(choices=[[i[0], mark_safe(i[1])] for i in icon_list]),
        }


def menu_add_edit(request, mid=None):
    menu_obj = models.Menu.objects.filter(pk=mid).first()
    if request.method == 'GET':
        form_obj = MenuForm(instance=menu_obj)
        return render(request, 'rbac/form.html', {'form_obj': form_obj})
    else:
        form_obj = MenuForm(request.POST, instance=menu_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('rbac:menu_list')
        else:
            return render(request, 'rbac/form.html', {'form_obj': form_obj})


# 删除菜单
def menu_del(request, mid):
    models.Menu.objects.filter(pk=mid).delete()
    return redirect('rbac:menu_list')


from django.forms import modelformset_factory, formset_factory
from rbac.forms import MultiPermissionForm
from rbac.serve.routes import get_all_url_dict


# 批量权限处理
def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """

    post_type = request.GET.get('type')  # 'add'

    # 更新和编辑用的
    FormSet = modelformset_factory(models.Permission, MultiPermissionForm, extra=0)

    # 增加用的
    AddFormSet = formset_factory(MultiPermissionForm, extra=0)

    # 查询出数据库中目前已经存在的所有的url路径(权限)
    permissions = models.Permission.objects.all()

    # 获取路由系统中所有URL
    router_dict = get_all_url_dict(ignore_namespace_list=['admin', ])

    # 数据库中的所有权限的别名
    permissions_name_set = set([i.url_name for i in permissions])

    # 路由系统中的所有权限的别名
    router_name_set = set(router_dict.keys())

    if request.method == 'POST' and post_type == 'add':
        add_formset = AddFormSet(request.POST)
        if add_formset.is_valid():
            permission_obj_list = [models.Permission(**i) for i in add_formset.cleaned_data]
            query_list = models.Permission.objects.bulk_create(permission_obj_list)
            for i in query_list:
                permissions_name_set.add(i.url_name)
    add_name_set = router_name_set - permissions_name_set
    add_formset = AddFormSet(initial=[row for name, row in router_dict.items() if name in add_name_set])

    del_name_set = permissions_name_set - router_name_set
    del_formset = FormSet(queryset=models.Permission.objects.filter(url_name__in=del_name_set))

    update_name_set = permissions_name_set & router_name_set
    update_formset = FormSet(queryset=models.Permission.objects.filter(url_name__in=update_name_set))

    if request.method == 'POST' and post_type == 'update':
        update_formset = FormSet(request.POST)
        if update_formset.is_valid():
            update_formset.save()
            update_formset = FormSet(queryset=models.Permission.objects.filter(url_name__in=update_name_set))

    return render(
        request,
        'rbac/multi_permissions.html',
        {
            'del_formset': del_formset,
            'update_formset': update_formset,
            'add_formset': add_formset,
        }
    )


def distribute_permissions(request):
    """
    分配权限
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')

    if request.method == 'POST' and request.POST.get('postType') == 'role':
        user = models.UserInfo.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        user.roles.set(request.POST.getlist('roles'))

    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        role = models.Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))

    # 所有用户
    user_list = models.UserInfo.objects.all()

    user_has_roles = models.UserInfo.objects.filter(id=uid).values('id', 'roles')
    user_has_roles_dict = {item['roles']: None for item in user_has_roles}

    """
    用户拥有的角色id
    user_has_roles_dict = { 角色id：None }
    """

    role_list = models.Role.objects.all()

    if rid:
        role_has_permissions = models.Role.objects.filter(id=rid).values('id', 'permissions')
    elif uid and not rid:
        user = models.UserInfo.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        role_has_permissions = user.roles.values('id', 'permissions')
    else:
        role_has_permissions = []

    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}

    """
    角色拥有的权限id
    role_has_permissions_dict = { 权限id：None }
    """

    all_menu_list = []

    queryset = models.Menu.objects.values('id', 'title')
    menu_dict = {}

    for item in queryset:
        item['children'] = []
        menu_dict[item['id']] = item
        all_menu_list.append(item)

    other = {'id': None, 'title': '其他', 'children': []}
    all_menu_list.append(other)
    menu_dict[None] = other

    root_permission = models.Permission.objects.filter(menus__isnull=False).values('id', 'title', 'menus_id')
    root_permission_dict = {}

    for per in root_permission:
        per['children'] = []
        nid = per['id']
        menu_id = per['menus_id']
        root_permission_dict[nid] = per
        menu_dict[menu_id]['children'].append(per)

    node_permission = models.Permission.objects.filter(menus__isnull=True).values('id', 'title', 'parent_id')

    for per in node_permission:
        pid = per['parent_id']  # 1
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        root_permission_dict[pid]['children'].append(per)

    return render(
        request,
        'rbac/distribute_permissions.html',
        {
            'user_list': user_list,
            'role_list': role_list,
            'user_has_roles_dict': user_has_roles_dict,
            'role_has_permissions_dict': role_has_permissions_dict,
            'all_menu_list': all_menu_list,
            'uid': uid,
            'rid': rid
        }
    )


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = models.UserInfo.objects.filter(username=username, password=password).first()
        if user_obj:
            request.session['user_id'] = user_obj.id
            init_permission(request, user_obj)
            return redirect('blog:home')
        else:
            return HttpResponse('登录失败')
    return render(request, 'login.html')
