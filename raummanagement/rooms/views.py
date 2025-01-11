from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserAccount, Building, Room, RoomBooking, UserCalendar
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime
from .models import Room, RoomBooking
from django.shortcuts import render
from .models import Room
import ast  # Zum sicheren Auswerten von Listen-ähnlichen Zeichenketten
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

    # Dictionary mit Gebäude-ID und zugehörigem Bild
    building_images = {"C": "https://www.tha.de/Binaries/Binary9220/13-05-08-HSA-C-Trakt-164.jpg" }

    # Standardbild, falls kein Bild vorhanden
    default_image = "https://www.tha.de/Binaries/Binary39833/THA-lageplan-2024-mit-avv-300-RGB.jpg"
    return render(request, 'building_list.html', {
        'buildings': buildings,
        'building_images': building_images,
        'default_image': default_image
    })



@login_required
def room_list(request, building_id):
    building = Building.objects.get(id=building_id)
    rooms = Room.objects.filter(building=building)
    return render(request, 'room_list.html', {'building': building, 'rooms': rooms})

@login_required
def filter_rooms(request):
    rooms = Room.objects.all()  # Alle Räume abrufen
    buildings = Building.objects.all()  # Alle Gebäude abrufen

    # Dynamisch alle einzigartigen Ausstattungsoptionen sammeln
    all_equipment = set()
    for room in rooms:
        if room.equipment:  # Prüfen, ob der Raum eine Ausstattung hat
            # Entferne Klammern und Anführungszeichen, falls vorhanden
            equipment_list = room.equipment.strip("[]").replace("'", "").split(', ')
            all_equipment.update(equipment_list)

    # Ausstattung-Filter anwenden
    selected_equipment = request.GET.getlist('equipment')
    if selected_equipment:
        for equipment in selected_equipment:
            rooms = rooms.filter(equipment__icontains=equipment)

    # Gebäude-Filter anwenden
    selected_building = request.GET.get('building')
    if selected_building:
        rooms = rooms.filter(building__id=selected_building)

    # Ausstattungsliste bereinigen für die Anzeige
    for room in rooms:
        if room.equipment:
            room.equipment = room.equipment.strip("[]").replace("'", "").replace(" ", "").split(',')

    return render(request, 'rooms/filter_rooms.html', {
        'rooms': rooms,
        'all_equipment': sorted(all_equipment),  # Alphabetisch sortieren
        'selected_equipment': selected_equipment,
        'buildings': buildings,
        'selected_building': selected_building
    })


@login_required
def book_room(request, room_id):
    room = Room.objects.get(id=room_id)
    bookings = RoomBooking.objects.filter(room=room).order_by('booking_date', 'start_time')

    # Zeige das Formular nur, wenn der Benutzer ein Planner ist
    if request.user.role == 'planner' and request.method == "POST":
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
        return redirect('book_room', room_id=room_id)

    # Render die Seite unabhängig von der Rolle
    return render(request, 'book_room.html', {
        'room': room,
        'bookings': bookings,
        'is_planner': request.user.role == 'planner'
    })

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
        role = request.POST['role']
        user = request.user

        if email:
            user.email = email
        if password:
            user.set_password(password)
        if role in ['viewer', 'planner']:
            user.role = role
        user.save()

        messages.success(request, "Account und Rolle wurden erfolgreich aktualisiert.")
        return redirect('account_settings')

    return render(request, 'account_settings.html')
