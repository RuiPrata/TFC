from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView
from django.views import generic
from django.contrib import messages
from django.http import Http404
from django.core.files import File
from django.db.models import Max
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.utils.encoding import smart_text
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import (    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
    View
)
from tootsie.forms import UserUpdateForm, ProfileUpdateForm
from .models import Client, Event, Profile, Modalidade,Room, Booking,Epoca
from django.urls import reverse, reverse_lazy
from .forms import SessionFilterForm, ClientFilterForm, ClientUpdateForm, AvailabilityForm, EventFormBooking
from clients.booking_functions import availability
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingSerializer
from rest_framework import generics
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime,date, timedelta
import calendar
from .utils import CalendarBooking
from django.utils.safestring import mark_safe
# Create your views here.


@login_required
def client_list_view(request):
    clients_qs = Client.objects.all()
    result = False

    clientOrder = request.GET.get('idOrder')
    balance = request.GET.get('balance')
    debt = request.GET.get('debt')
    discount = request.GET.get('discount')
    clientId = request.GET.get('clientID')

    if clients_qs.exists():
        result = True
        clients_qs = clients_qs.order_by('-pk')
        s = []

        if clientId != None and clientId != "":
            clients_qs = clients_qs.filter(id=clientId)
            template_name = 'clients/list.html'
            context = {'clients': clients_qs, 'form': ClientFilterForm}
            return render(request, template_name, context)

        if clientOrder != None:
            if clientOrder == "descending":
                clients_qs = clients_qs.order_by('-pk')
            else:
                clients_qs = clients_qs.order_by('pk')

        if balance != None:
            if balance == "ascending":
                clients_qs = sorted(clients_qs, key=lambda ModelClass: int(
                    ModelClass.balance))
            elif balance == "descending":
                clients_qs = sorted(clients_qs, key=lambda ModelClass: int(
                    ModelClass.balance), reverse=True)

        if debt != None:
            if debt == "ascending":
                clients_qs = sorted(clients_qs, key=lambda ModelClass: int(
                    ModelClass.debt))
            elif debt == "descending":
                clients_qs = sorted(clients_qs, key=lambda ModelClass: int(
                    ModelClass.debt), reverse=True)

        if discount != None:
            if discount == "ascending":
                clients_qs = sorted(clients_qs, key=lambda ModelClass: int(
                    ModelClass.discount))
            elif discount == "descending":
                clients_qs = sorted(clients_qs, key=lambda ModelClass: int(
                    ModelClass.discount), reverse=True)

    if result:
        template_name = 'clients/list.html'
        context = {'clients': clients_qs, 'form': ClientFilterForm}
    else:
        template_name = 'clients/list.html'
        context = {'clients': None, 'form': ClientFilterForm}

    return render(request, template_name, context)


class client_delete_view(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    success_url = '/'  # Home

    def test_func(self):
        return True


class staff_delete_view(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Profile
    success_url = '/staff-list'

    def test_func(self):
        return True


def client_edit_view(request, id=None):
    instance = Client()
    if id:
        instance = get_object_or_404(Client, pk=id)
    else:
        instance = Client()

    if request.method == 'POST':
        form = ClientUpdateForm(request.POST, instance=instance)

        if request.POST and form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('client_show', kwargs={'client_id': id}))

    else:
        form = ClientUpdateForm(instance=instance)

    context = {
        'form': form,
    }

    return render(request, 'clients/edit.html', context)


def staff_edit_view(request, id=None):
    instance = Profile()
    if id:
        instance = get_object_or_404(Profile, pk=id)
    else:
        instance = Profile()

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=instance.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=instance)

        if request.POST and u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return HttpResponseRedirect(reverse('staff-list'))

    else:
        u_form = UserUpdateForm(instance=instance.user)
        p_form = ProfileUpdateForm(instance=instance)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'staff/edit.html', context)


def delete_staff(request, id):
    obj = get_object_or_404(Profile, id=id)
    if request.method == "POST":
        obj.delete_user()
        return redirect('staff-list')
    context = {
        "object": obj
    }
    return render(request, "staff/profile_delete.html", context)


@login_required
def session_list_view(request):

    sessionOrder = request.GET.get('sessionOrder')
    p = request.GET.get('payed')
    t = request.GET.get('time')
    m = request.GET.get('modality')
    d = request.GET.get('driver')
    i = request.GET.get('instructor')
    b = request.GET.get('boat')
    c = request.GET.get('sessionID')
    print("form")
    form = SessionFilterForm()
    #newForm = form.save()
    # print(newForm)

    if p == "False":
        sessions_qs = Event.objects.filter(payed=False)
        sessions_qs = sessions_qs.order_by('-pk')
    elif p == "True":
        sessions_qs = Event.objects.filter(payed=True)
        sessions_qs = sessions_qs.order_by('-pk')
    else:
        sessions_qs = Event.objects.all()
        sessions_qs = sessions_qs.order_by('-pk')

    if sessions_qs.exists():
        s = []

        if c != None and c != '':
            sessions_qs = sessions_qs.filter(id=c)
            template_name = 'Session/sessions_list.html'
            context = {'events': sessions_qs, 'form': form}
            return render(request, template_name, context)

        if sessionOrder != None:
            if sessionOrder == "descending":
                sessions_qs = sessions_qs.order_by('-pk')
            else:
                sessions_qs = sessions_qs.order_by('pk')

        if t != None and t != "indifferent":
            if t == "descending":
                sessions_qs = sessions_qs.order_by('-time')
            else:
                sessions_qs = sessions_qs.order_by('time')

        if m != None and m != "All":
            for session in sessions_qs:
                if session.modality.name == m:
                    s.append(session)
            sessions_qs = s
            s = []
        else:
            print("modality = All")

        if d != None and d != "All":
            for session in sessions_qs:
                if session.driver.firstName == d:
                    s.append(session)
            sessions_qs = s
            s = []
        else:
            print("driver = All")

        if i != None and i != "All":
            for session in sessions_qs:
                if session.instructor.firstName == i:
                    s.append(session)
            sessions_qs = s
            s = []
        else:
            print("instructor = All")

        if b != None and b != "All":
            for session in sessions_qs:
                if session.boat.name == b:
                    s.append(session)
            sessions_qs = s
            s = []
        else:
            print("Boat = All")

        template_name = 'Session/sessions_list.html'
        context = {'events': sessions_qs, 'form': form}
    else:
        template_name = 'Session/sessions_list.html'
        context = {'events': None, 'form': form}

    return render(request, template_name, context)


@login_required
def sessions_choices_ajax(request):
    uf = request.GET.get('payed')
    if uf == "False":
        sessions_qs = Event.objects.filter(payed=False)
    elif uf == "True":
        sessions_qs = Event.objects.filter(payed=True)
    else:
        sessions_qs = Event.objects.all()

    template_name = 'Session/sessions_choices_ajax.html'
    context = {'events': sessions_qs}
    return render(request, template_name, context)


@login_required
def staff_list_view(request):
    profile_qs = Profile.objects.all()
    template_name = 'staff/list.html'

    context = {'profile': profile_qs}
    return render(request, template_name, context)



##Booking Stuff

class GenericAPIView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin):
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
    lookup_field = 'id'
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id= None):
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)
        

    def post(self, request):
        return self.create(request)
    
    def put(self, request, id=None):
        return self.update(request, id)

    def delete(self,request,id):
        return self.destroy(request, id)

class BookingAPIView(APIView):
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        booking = Booking.objects.all()
        serializer = BookingSerializer(booking, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,template_name = 'room_list_view.html',status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

def RoomListView(request):
    room = Room.objects.all()[0]    
    room_categories = dict(room.ROOM_CATEGORIES)

    room_list=[]
    for room_category in room_categories:
        room = room_categories.get(room_category)
        room_url = reverse( "RoomDetailView" , kwargs={'category': room_category })
        room_list.append((room,room_url))
    context= {
        "room_list" : room_list,        
    }

    return render(request, 'booking/room_list_view.html',context)       


class BookingList(ListView):
    model = Booking
    template_name = "booking_list.html"
    
    def get_queryset(self, *args, **kwargs):
        booking_list = Booking.objects.all()
        print(booking_list)
        return booking_list

class RoomDetailView(View):
    def get(self, request, *args, **kwargs):
        category = self.kwargs.get('category', None)
        clients = Client.objects.all()
        epoca = Epoca.objects.all()
        form = AvailabilityForm()
        room_list = Room.objects.filter(category = category)
        if len(room_list) > 0:
            room = room_list[0]
            room_category = dict(room.ROOM_CATEGORIES).get(room.category,None)
            context = {
                'room_category': room_category,
                'clients':clients,
                'epocaViews' : epoca,
            }
            return render(request, 'booking/room_detail_view.html', context)
        else:
            return HttpResponse("Category does not exist")
    
    def post(self, request, *args, **kwargs):
        category = self.kwargs.get('category', None)
        room_list = Room.objects.filter(category = category)
        form = AvailabilityForm(request.POST)

        if(form.is_valid()):
            data = form.cleaned_data
            dia_checkin = int(data['check_in'].strftime("%d"))
            dia_checkout = int(data['check_out'].strftime("%d"))
            #print(dia_checkin,dia_checkout)
            num_noites = (data['check_out'] - data['check_in']).days
            #print(num_noites)
            num_fds = 0
             

            #calcular numero de fim de semana entre as duas datas
            for i in range(dia_checkin,dia_checkout):
                temp_data = datetime( int(data['check_in'].strftime("%Y")),  int(data['check_in'].strftime("%m")), i)
                if temp_data.strftime("%A") == "Friday": 
                    num_fds +=1
                elif temp_data.strftime("%A") == "Saturday":
                    num_fds +=1
                
            num_semana = num_noites - num_fds

            #print(data['check_in'].strftime("%d"))
            client_name = request.POST['nome_cliente']
            display = request.POST.get("premium", None)
            if display in [None]:
                display = False
            epoca = request.POST['epoca']
            premium_new = display
            
            #Calculos para preço total
            preco_total = 0
            if num_fds == 0: 
                if premium_new : 
                    if epoca == 'Alta':
                        preco_total = 65 * num_noites
                    else : 
                        preco_total = 50 * num_noites
                else : 
                    if epoca == 'Alta' : 
                        preco_total = 80 * num_noites
                    if epoca == 'Baixa':
                        preco_total = 60 * num_noites
            else : 
                if premium_new : 
                    if epoca == 'Alta':
                        preco_total = (65 * num_semana) + (75 * num_fds)
                    else : 
                        preco_total = (50 * num_semana) + (60 * num_fds)
                else : 
                    if epoca == 'Alta' : 
                        preco_total = (80 * num_semana) + (95 * num_fds)
                    if epoca == 'Baixa':
                        preco_total = (60 * num_semana) + (70 * num_fds)
            #print(preco_total)
            
        available_rooms = []
        for room in room_list:
            if availability.check_availability(room, data['check_in'], data['check_out']):
                available_rooms.append(room)

        if len(available_rooms) > 0:
            room = available_rooms[0]
            client_new = Client.objects.get(name = client_name) #se nao houver nomes duplicados
            epoca_new = Epoca.objects.get (epoca = epoca)
            booking = Booking.objects.create( user = self.request.user , room = room , check_in = data['check_in'] , check_out = data['check_out'] , 
                                            client = client_new, epoca = epoca_new, premium = premium_new, preco_total = preco_total  )
            booking.save()
            return HttpResponseRedirect('/booking_list/calendar/')
        else:
            return HttpResponse ("this category of rooms are booked")

class CancelBookingView(DeleteView):
    model = Booking
    template_name= 'booking/booking_cancel_view.html'
    success_url = reverse_lazy('CalendarBooking')

class CalendarViewBooking(generic.ListView):
    model = Event
    template_name = 'booking/calendar/calendar_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))
    
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        # Instantiate our calendar class with today's year and date
        cal = CalendarBooking(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month
