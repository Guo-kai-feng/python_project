from django.contrib import admin
from blog import models
#root 12345678g

admin.site.register(models.Blog)
admin.site.register(models.Article)
