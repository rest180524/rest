from django.db import models
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from django.core.files.storage import default_storage as storage  

from django.contrib.auth.models import User

import math

# ћодели отображают информацию о данных, с которыми вы работаете.
# ќни содержат пол¤ и поведение ваших данных.
# ќбычно одна модель представл¤ет одну таблицу в базе данных.
#  ажда¤ модель это класс унаследованный от django.db.models.Model.
# јтрибут модели представл¤ет поле в базе данных.
# Django предоставл¤ет автоматически созданное API дл¤ доступа к данным

# choices (список выбора). »тератор (например, список или кортеж) 2-х элементных кортежей,
# определ¤ющих варианты значений дл¤ пол¤.
# ѕри определении, виджет формы использует select вместо стандартного текстового пол¤
# и ограничит значение пол¤ указанными значени¤ми.

# „итабельное им¤ пол¤ (метка, label).  аждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
# первым аргументом принимает необ¤зательное читабельное название.
# ≈сли оно не указано, Django самосто¤тельно создаст его, использу¤ название пол¤, замен¤¤ подчеркивание на пробел.
# null - ≈сли True, Django сохранит пустое значение как NULL в базе данных. ѕо умолчанию - False.
# blank - ≈сли True, поле не об¤зательно и может быть пустым. ѕо умолчанию - False.
# Ёто не то же что и null. null относитс¤ к базе данных, blank - к проверке данных.
# ≈сли поле содержит blank=True, форма позволит передать пустое значение.
# ѕри blank=False - поле об¤зательно.

# Тип комнаты
class Kind(models.Model):
    title = models.CharField(_('kind_title'), max_length=128, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'kind'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['title']),
        ]
        # Сортировка по умолчанию
        ordering = ['title']
    def __str__(self):
        # Вывод названияв тег SELECT 
        return "{}".format(self.title)

# Комнаты
class Room(models.Model):
    kind = models.ForeignKey(Kind, related_name='room_kind', on_delete=models.CASCADE)
    title = models.CharField(_('room_title'), max_length=16)
    floor = models.IntegerField(_('floor'))
    details = models.TextField(_('room_details'))
    photo = models.ImageField(_('room_photo'), upload_to='images/', blank=True, null=True)    
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'room'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['kind', 'title']),
        ]
        # Сортировка по умолчанию
        ordering = ['kind', 'title']
    def __str__(self):
        # Вывод названияв тег SELECT 
        return "{}: {}".format(self.kind, self.title)

class ViewRoom(models.Model):
    kind_id = models.IntegerField(_('kind_id'))
    kind = models.CharField(_('kind_title'), max_length=128)
    title = models.CharField(_('room_title'), max_length=128)
    floor = models.IntegerField(_('floor'))
    details = models.TextField(_('room_details'))
    photo = models.ImageField(_('room_photo'), upload_to='images/', blank=True, null=True)    
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    avg_rating = models.DecimalField(_('avg_rating'), max_digits=6, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'view_room'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['kind', 'title']),
        ]
        # Сортировка по умолчанию
        ordering = ['kind', 'title']
        # Таблицу не надо не добавлять не удалять
        managed = False
    def __str__(self):
        # Вывод названияв тег SELECT 
        return "{}: {}".format(self.region, self.title)

                        
# Заявки пользователей
class Claim(models.Model):
    datec = models.DateTimeField(_('datec_claim'), auto_now_add=True)
    user = models.ForeignKey(User, related_name='claim_user', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='claim_room', on_delete=models.CASCADE)
    start = models.DateTimeField(_('start'))
    finish = models.DateTimeField(_('finish'))
    details = models.TextField(_('claim_details'))
    result = models.TextField(_('claim_result'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'claim'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['datec', 'user']),
        ]
        # Сортировка по умолчанию
        ordering = ['datec']

# Отзывы 
class Reviews(models.Model):
    dater = models.DateTimeField(_('dater_reviews'), auto_now_add=True)
    room = models.ForeignKey(Room, related_name='reviews_room', on_delete=models.CASCADE)
    rating = models.IntegerField(_('rating'), blank=True, null=True)
    details = models.TextField(_('details_reviews'))
    user = models.ForeignKey(User, related_name='reviews_user', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'reviews'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['dater']),
        ]
        # Сортировка по умолчанию
        ordering = ['dater']

# Ќовости 
class News(models.Model):
    daten = models.DateTimeField(_('daten'))
    title = models.CharField(_('title_news'), max_length=256)
    details = models.TextField(_('details_news'))
    photo = models.ImageField(_('photo_news'), upload_to='images/', blank=True, null=True)    
    class Meta:
        # ѕараметры модели
        # ѕереопределение имени таблицы
        db_table = 'news'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['daten']),
        ]
        # —ортировка по умолчанию
        ordering = ['daten']
    #def save(self):
    #    super().save()
    #    img = Image.open(self.photo.path) # Open image
    #    # resize image
    #    if img.width > 512 or img.height > 700:
    #        proportion_w_h = img.width/img.height  # ќтношение ширины к высоте 
    #        output_size = (512, int(512/proportion_w_h))
    #        img.thumbnail(output_size) # »зменение размера
    #        img.save(self.photo.path) # —охранение
