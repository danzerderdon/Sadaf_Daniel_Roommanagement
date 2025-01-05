from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserAccount, Building, Room, RoomBooking, UserCalendar
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime
from .models import Room, RoomBooking
from django.contrib.auth import get_user_model

def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def create_account(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            user = UserAccount.objects.create_user(email=email, password=password)
            messages.success(request, "Account created successfully.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'create_account.html')

@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def building_list(request):
    buildings = Building.objects.all()
    return render(request, 'building_list.html', {'buildings': buildings})

@login_required
def room_list(request, building_id):
    building = Building.objects.get(id=building_id)
    rooms = Room.objects.filter(building=building)
    return render(request, 'room_list.html', {'building': building, 'rooms': rooms})

@login_required
def filter_rooms(request):
    if request.method == "POST":
        room_type = request.POST.get('room_type')
        equipment = request.POST.getlist('equipment')
        rooms = Room.objects.all()

        if room_type:
            rooms = rooms.filter(category__name=room_type)

        for item in equipment:
            rooms = rooms.filter(equipment__icontains=item)

        return render(request, 'filtered_rooms.html', {'rooms': rooms})

    return render(request, 'filter_rooms.html')

@login_required
def book_room(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == "POST":
        booking_date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        RoomBooking.objects.create(
            user=request.user,
            room=room,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time
        )
        messages.success(request, "Room booked successfully.")
        return redirect('my_bookings')
    return render(request, 'book_room.html', {'room': room})

@login_required
def free_rooms(request):
    datetime_str = request.GET.get('datetime')
    rooms = Room.objects.all()
    if datetime_str:
        datetime_obj = parse_datetime(datetime_str)
        if datetime_obj:
            booked_rooms = RoomBooking.objects.filter(
                start_time__lte=datetime_obj, end_time__gte=datetime_obj
            ).values_list('room_id', flat=True)
            rooms = rooms.exclude(id__in=booked_rooms)
    return render(request, 'free_rooms.html', {'rooms': rooms})

@login_required
def my_bookings(request):
    bookings = RoomBooking.objects.filter(user=request.user)
    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required
def delete_booking(request, booking_id):
    booking = RoomBooking.objects.get(id=booking_id)
    if booking.user == request.user:
        booking.delete()
        messages.success(request, "Booking deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this booking.")
    return redirect('my_bookings')

@login_required
def account_settings(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = request.user
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, "Account updated successfully.")
    return render(request, 'account_settings.html')



