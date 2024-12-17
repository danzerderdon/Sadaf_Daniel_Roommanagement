from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_account/', views.create_account, name='create_account'),
    path('', views.home_view, name='home'),
    path('buildings/', views.building_list, name='building_list'),
    path('buildings/<str:building_id>/rooms/', views.room_list, name='room_list'),
    path('filter_rooms/', views.filter_rooms, name='filter_rooms'),
    path('free_rooms/', views.free_rooms, name='free_rooms'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('book_room/<int:room_id>/', views.book_room, name='book_room'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('settings/', views.account_settings, name='account_settings'),
]
