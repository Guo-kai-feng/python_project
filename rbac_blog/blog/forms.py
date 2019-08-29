#!/usr/bin/env python
# -*- coding:utf-8 -*-
from blog import models
from django import forms


class AlterBlogForm(forms.ModelForm):
    class Meta:
        model = models.Blog
        fields = '__all__'
        exclude = []
        error_messages = {
            'name': {'required': '不能为空'},
            'user': {'required': '不能为空'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from multiselectfield.forms.fields import MultiSelectFormField
        for field_name, field in self.fields.items():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})


class AlterArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        exclude = ['create_at', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from multiselectfield.forms.fields import MultiSelectFormField
        for field_name, field in self.fields.items():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})
