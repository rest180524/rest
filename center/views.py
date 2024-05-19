from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.urls import reverse

from django.contrib.auth import login as auth_login

import datetime

import time

import csv
import xlwt
from io import BytesIO

# Подключение моделей
from django.contrib.auth.models import User, Group

from django.db import models
from django.db.models import Q

from .models import Kind, Room, ViewRoom, Claim, Reviews, News
# Подключение форм
from .forms import KindForm, RoomForm, ClaimForm, ClaimFormEdit, ReviewsForm, NewsForm, SignUpForm

from django.contrib.auth.models import AnonymousUser

# Create your views here.
# Групповые ограничения
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

# Стартовая страница 
def index(request):
    news1 = News.objects.all().order_by('-daten')[0:1]
    news24 = News.objects.all().order_by('-daten')[1:4]
    room14 = ViewRoom.objects.all().order_by('?')[0:4]
    reviews14 = Reviews.objects.all().order_by('?')[0:4]
    return render(request, "index.html", {"news1": news1, "news24": news24, "room14": room14, "reviews14": reviews14, })    

# Контакты
def contact(request):
    return render(request, "contact.html")

# Фотогалерея
def photogallery(request):
    return render(request, "photogallery.html")

# Прайс-лист
def price(request):
    return render(request, "price.html")

# Услуги
def services(request):
    return render(request, "services.html")

# Кабинет
@login_required
def cabinet(request):
    claim = Claim.objects.filter(user_id=request.user.id).order_by('-datec')   
    reviews = Reviews.objects.filter(user_id=request.user.id).order_by('-dater')    
    return render(request, "cabinet.html", {"claim": claim, "reviews": reviews, })

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def kind_index(request):
    try:
        kind = Kind.objects.all().order_by('title')
        return render(request, "kind/index.html", {"kind": kind,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def kind_create(request):
    try:
        if request.method == "POST":
            kind = Kind()
            kind.title = request.POST.get("title")
            kindform = KindForm(request.POST)
            if kindform.is_valid():
                kind.save()
                return HttpResponseRedirect(reverse('kind_index'))
            else:
                return render(request, "kind/create.html", {"form": kindform})
        else:        
            kindform = KindForm()
            return render(request, "kind/create.html", {"form": kindform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def kind_edit(request, id):
    try:
        kind = Kind.objects.get(id=id)
        if request.method == "POST":
            kind.title = request.POST.get("title")
            kindform = KindForm(request.POST)
            if kindform.is_valid():
                kind.save()
                return HttpResponseRedirect(reverse('kind_index'))
            else:
                return render(request, "kind/edit.html", {"form": kindform})
        else:
            # Загрузка начальных данных
            kindform = KindForm(initial={'title': kind.title, })
            return render(request, "kind/edit.html", {"form": kindform})
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def kind_delete(request, id):
    try:
        kind = Kind.objects.get(id=id)
        kind.delete()
        return HttpResponseRedirect(reverse('kind_index'))
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
#@login_required
def kind_read(request, id):
    try:
        kind = Kind.objects.get(id=id) 
        return render(request, "kind/read.html", {"kind": kind})
    except Kind.DoesNotExist:
        return HttpResponseNotFound("<h2>Kind not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def room_index(request):
    try:
        room = Room.objects.all().order_by('title')
        return render(request, "room/index.html", {"room": room,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
def room_list(request):
    try:
        room = ViewRoom.objects.all().order_by('title')
        #country = Country.objects.order_by('title').values_list('title', flat=True).distinct()
        #region = Region.objects.order_by('title').values_list('title', flat=True).distinct()
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Список Комнат
                room = ViewRoom.objects.all()
                # Поиск по категории
                kinds_search = request.POST.get("kinds_search")
                #print(kinds_search)
                if kinds_search != '':
                    kind_query = Kind.objects.filter(title__contains = kinds_search).only('id').all()
                    #print(kind_query)
                    room = room.filter(kind_id__in=kind_query)
                # Поиск по описанию комнаты
                details_search = request.POST.get("details_search")
                #print(details_search)
                if details_search != '':
                    room = room.filter(details__contains = details_search).all()
                # Сортировка
                room = room.order_by('title')
                return render(request, "room/list.html", {"room": room, "kinds_search" : kinds_search, "details_search" : details_search,})
            elif 'resetBtn' in request.POST:            
                room = ViewRoom.objects.all().order_by('title')
                return render(request, "room/list.html", {"room": room, })
            else:
                # Выделить id команты
                room_id = request.POST.dict().get("room_id")
                #print("room_id ", room_id)
                price = request.POST.dict().get("price")
                #print("price ", price)
                user = request.POST.dict().get("user")
                #print("user ", user)
                # Перейти к созданию заявки
                return HttpResponseRedirect(reverse('claim_create', args=(room_id,)))                
        else:
            #return render(request, "room/list.html", {"room": room, "country": country, "region": region, })
            return render(request, "room/list.html", {"room": room, })
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def room_create(request):
    try:
        if request.method == "POST":
            room = Room()
            room.kind = Kind.objects.filter(id=request.POST.get("kind")).first()
            room.title = request.POST.get("title")
            room.floor = request.POST.get("floor")
            room.details = request.POST.get("details")
            if 'photo' in request.FILES:                
                room.photo = request.FILES['photo']        
            room.price = request.POST.get("price")
            roomform = RoomForm(request.POST)
            if roomform.is_valid():
                room.save()
                return HttpResponseRedirect(reverse('room_index'))
            else:
                return render(request, "room/create.html", {"form": roomform})
        else:        
            roomform = RoomForm()
            return render(request, "room/create.html", {"form": roomform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def room_edit(request, id):
    try:
        room = Room.objects.get(id=id)
        if request.method == "POST":
            room.kind = Kind.objects.filter(id=request.POST.get("kind")).first()
            room.title = request.POST.get("title")
            room.floor = request.POST.get("floor")
            room.details = request.POST.get("details")
            if 'photo' in request.FILES:                
                room.photo = request.FILES['photo']        
            room.price = request.POST.get("price")
            roomform = RoomForm(request.POST)
            if roomform.is_valid():
                room.save()
                return HttpResponseRedirect(reverse('room_index'))
            else:
                return render(request, "room/edit.html", {"form": roomform})
        else:
            # Загрузка начальных данных
            roomform = RoomForm(initial={'kind': room.kind, 'title': room.title, 'floor': room.floor, 'details': room.details, 'photo': room.photo, 'price': room.price, })
            return render(request, "room/edit.html", {"form": roomform})
    except Room.DoesNotExist:
        return HttpResponseNotFound("<h2>Room not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def room_delete(request, id):
    try:
        room = Room.objects.get(id=id)
        room.delete()
        return HttpResponseRedirect(reverse('room_index'))
    except Room.DoesNotExist:
        return HttpResponseNotFound("<h2>Room not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
#@login_required
def room_read(request, id):
    try:
        #room = Room.objects.get(id=id) 
        room = ViewRoom.objects.get(id=id) 
        # Отзывы на данный отель
        reviews = Reviews.objects.filter(room_id=id).exclude(rating=None)
        return render(request, "room/read.html", {"room": room, "reviews": reviews})
    except Room.DoesNotExist:
        return HttpResponseNotFound("<h2>Room not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def claim_index(request):
    try:
        claim = Claim.objects.all().order_by('-datec')
        return render(request, "claim/index.html", {"claim": claim,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
#@group_required("Managers")
def claim_create(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        print(room)
        if request.method == "POST":
            claim = Claim()
            claim.user = request.user
            #claim.room = Room.objects.filter(id=request.POST.get("room")).first()
            claim.room_id = room_id
            claim.start = request.POST.get("start")
            claim.finish = request.POST.get("finish")
            claim.details = request.POST.get("details")
            claim.user_id = request.user.id
            claimform = ClaimForm(request.POST)
            if claimform.is_valid():
                claim.save()
                return HttpResponseRedirect(reverse('cabinet'))
            else:
                return render(request, "claim/create.html", {"form": claimform, "room": room, })
        else:        
            claimform = ClaimForm(initial={'start': (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d'), 'finish': (datetime.datetime.now() + datetime.timedelta(days=37)).strftime('%Y-%m-%d'), })
            return render(request, "claim/create.html", {"form": claimform, "room": room, })
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def claim_edit(request, id):
    try:
        claim = Claim.objects.get(id=id)
        if request.method == "POST":
            #claim.room = Room.objects.filter(id=request.POST.get("room")).first()
            #claim.start = request.POST.get("start")
            #claim.finish = request.POST.get("finish")
            #claim.details = request.POST.get("details")
            claim.result = request.POST.get("result")
            claimform = ClaimFormEdit(request.POST)
            if claimform.is_valid():
                claim.save()
                return HttpResponseRedirect(reverse('claim_index'))
            else:
                return render(request, "claim/edit.html", {"form": claimform, "claim": claim, })
        else:
            # Загрузка начальных данных
            claimform = ClaimFormEdit(initial={'result': claim.result, })
            return render(request, "claim/edit.html", {"form": claimform, "claim": claim, })
    except Claim.DoesNotExist:
        return HttpResponseNotFound("<h2>Claim not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def claim_delete(request, id):
    try:
        claim = Claim.objects.get(id=id)
        claim.delete()
        return HttpResponseRedirect(reverse('claim_index'))
    except Claim.DoesNotExist:
        return HttpResponseNotFound("<h2>Claim not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
def claim_read(request, id):
    try:
        claim = Claim.objects.get(id=id) 
        return render(request, "claim/read.html", {"claim": claim})
    except Claim.DoesNotExist:
        return HttpResponseNotFound("<h2>Claim not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для просмотра
def reviews_list(request):
    try:
        reviews = Reviews.objects.all().order_by('-dater')
        return render(request, "reviews/list.html", {"reviews": reviews})        
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра с кнопкой удалить
@login_required
@group_required("Managers")
def reviews_index(request):
    try:
        reviews = Reviews.objects.all().order_by('-dater')
        return render(request, "reviews/index.html", {"reviews": reviews})        
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
def reviews_create(request, room_id):
    try:
        print(room_id)
        room = Room.objects.get(id=room_id)
        if request.method == "POST":
            reviews = Reviews()        
            #reviews.room = Room.objects.filter(id=request.POST.get("room")).first()
            reviews.room_id = room_id
            reviews.rating = request.POST.get("rating")
            reviews.details = request.POST.get("details")
            reviews.user = request.user
            reviewsform = ReviewsForm(request.POST)
            if reviewsform.is_valid():
                reviews.save()
                return HttpResponseRedirect(reverse('cabinet'))
            else:
                return render(request, "reviews/create.html", {"form": reviewsform,  "room": room, })     
        else:        
            reviewsform = ReviewsForm(initial={'rating': 5, })
            return render(request, "reviews/create.html", {"form": reviewsform, "room": room, })        
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def reviews_delete(request, id):
    try:
        reviews = Reviews.objects.get(id=id)
        reviews.delete()
        return HttpResponseRedirect(reverse('reviews_index'))
    except Reviews.DoesNotExist:
        return HttpResponseNotFound("<h2>Reviews not found</h2>")


###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def news_index(request):
    try:
        #news = News.objects.all().order_by('surname', 'name', 'patronymic')
        #return render(request, "news/index.html", {"news": news})
        news = News.objects.all().order_by('-daten')
        return render(request, "news/index.html", {"news": news})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)


# Список для просмотра
def news_list(request):
    try:
        news = News.objects.all().order_by('-daten')
        return render(request, "news/list.html", {"news": news})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def news_create(request):
    try:
        if request.method == "POST":
            news = News()        
            news.daten = request.POST.get("daten")
            news.title = request.POST.get("title")
            news.details = request.POST.get("details")
            if 'photo' in request.FILES:                
                news.photo = request.FILES['photo']        
            news.save()
            return HttpResponseRedirect(reverse('news_index'))
        else:        
            #newsform = NewsForm(request.FILES, initial={'daten': datetime.datetime.now().strftime('%Y-%m-%d'),})
            newsform = NewsForm(initial={'daten': datetime.datetime.now().strftime('%Y-%m-%d'), })
            return render(request, "news/create.html", {"form": newsform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def news_edit(request, id):
    try:
        news = News.objects.get(id=id) 
        if request.method == "POST":
            news.daten = request.POST.get("daten")
            news.title = request.POST.get("title")
            news.details = request.POST.get("details")
            if "photo" in request.FILES:                
                news.photo = request.FILES["photo"]
            news.save()
            return HttpResponseRedirect(reverse('news_index'))
        else:
            # Загрузка начальных данных
            newsform = NewsForm(initial={'daten': news.daten.strftime('%Y-%m-%d'), 'title': news.title, 'details': news.details, 'photo': news.photo })
            return render(request, "news/edit.html", {"form": newsform})
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def news_delete(request, id):
    try:
        news = News.objects.get(id=id)
        news.delete()
        return HttpResponseRedirect(reverse('news_index'))
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
#@login_required
def news_read(request, id):
    try:
        news = News.objects.get(id=id) 
        return render(request, "news/read.html", {"news": news})
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Регистрационная форма 
def signup(request):
    try:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                auth_login(request, user)
                return HttpResponseRedirect(reverse('index'))
                #return render(request, 'registration/register_done.html', {'new_user': user})
        else:
            form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Изменение данных пользователя
@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    try:
        model = User
        fields = ('first_name', 'last_name', 'email',)
        template_name = 'registration/my_account.html'
        success_url = reverse_lazy('index')
        #success_url = reverse_lazy('my_account')
        def get_object(self):
            return self.request.user
    except Exception as exception:
        print(exception)

# Выход
from django.contrib.auth import logout
def logoutUser(request):
    logout(request)
    return render(request, "index.html")

