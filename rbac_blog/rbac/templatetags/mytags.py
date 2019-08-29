from collections import OrderedDict

from django.conf import settings
from django import template

register = template.Library()


@register.inclusion_tag('rbac/menu2.html')
def menu(request):
    menu_dict = request.session.get(settings.MENU_KEY)
    keys = sorted(menu_dict, key=lambda x: menu_dict[x]['weight'], reverse=True)
    order_dict = OrderedDict()
    for key in keys:
        order_dict[key] = menu_dict[key]
    for key, value in order_dict.items():
        for i in value['children']:
            if request.current_id == i.get('id'):
                value['class'] = 'show'
                i['class'] = 'active'
    return {'order_dict': order_dict}


# 这就是精确到按钮级别的过滤器
@register.filter
def url_filter(name, request):
    if name in request.session['url_name']:
        return True
    else:
        return False


@register.inclusion_tag('rbac/bread.html')
def breadCrumbs(request):
    bread_crumbs = request.bread_crumbs
    return {'bread_crumbs': bread_crumbs}


@register.simple_tag
def gen_role_url(request, rid):
    params = request.GET.copy()
    params._mutable = True
    params['rid'] = rid
    return params.urlencode()
