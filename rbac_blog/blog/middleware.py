from rbac import models
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class UserAuth(MiddlewareMixin):

    def process_request(self, request):
        white_list = [reverse('login'), ]
        if request.path in white_list:
            return
        user_id = request.session.get('user_id')

        if user_id:
            user_obj = models.UserInfo.objects.get(id=request.session.get('user_id'))
            # 将当前登录用户对象作为一个属性，封装给了request
            request.user_obj = user_obj
            return

        else:
            return redirect('login')
