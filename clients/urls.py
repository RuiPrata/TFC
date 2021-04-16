from django.urls import path, re_path
from . import views
from .views import (
    client_list_view,
    session_list_view,
    client_delete_view,
    staff_list_view,
    staff_delete_view,
    delete_staff,
    staff_edit_view,
    client_edit_view,
    sessions_choices_ajax,
    BookingList,
    RoomListView,
    RoomDetailView,
    CancelBookingView,
    BookingAPIView,
    GenericAPIView,
    CalendarViewBooking   
)

#app_name= 'clients'

urlpatterns = [
    path('',views.client_list_view, name='home'),
    path('clients/<int:pk>/delete',
         client_delete_view.as_view(), name='client-delete'),
    path('sessions-list/', session_list_view, name='sessions-list'),
    path('sessions-list/sessions_choices_ajax/',
         sessions_choices_ajax,
         name='sessions_choices_ajax'),
    path('staff-list/', staff_list_view, name='staff-list'),
    path('staff-list/<int:id>/delete-staff',
         delete_staff, name='delete-staff'),
    path('staff-list/<int:id>/edit', staff_edit_view, name='staff-edit'),
    path('clients/<int:id>/edit', client_edit_view, name='client-edit'),



    ##Booking Stuff
    path('room_list/',RoomListView, name = 'RoomListView'),
    path('booking_list/',BookingList.as_view(), name = 'BookingList'),
    path('room/<category>', RoomDetailView.as_view(), name='RoomDetailView'),
    path('booking_list/api',BookingAPIView.as_view()),
    path('booking_list/api/<int:id>/',GenericAPIView.as_view()),
    path('booking/cancel/<pk>', CancelBookingView.as_view(), name='CancelBookingView'),
    path('booking_list/calendar/', CalendarViewBooking.as_view(), name = 'CalendarBooking'),
]

