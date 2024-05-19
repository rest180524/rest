from django.contrib import admin

# Register your models here.
from .models import Kind, Room, Claim, Reviews, News

# Добавление модели на главную страницу интерфейса администратора
admin.site.register(Kind)
admin.site.register(Room)
admin.site.register(Claim)
admin.site.register(Reviews)
admin.site.register(News)
