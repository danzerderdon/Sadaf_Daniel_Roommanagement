import webuntis
from rooms.models import Building, Room

session = webuntis.Session(server='https://webuntis.com',
                           username='danzer',
                           password='Gullasch123!',
                           school='Hochschule Augsburg',
                           useragent='RaumManagementApp')
def import_rooms():
    session.login()  # Anmeldung bei WebUntis

    # Gebäude und Räume abrufen
    rooms = session.rooms()  # Alle Räume abrufen

    for room in rooms:
        building_name = room.name.split('-')[0]  # Annahme: Gebäude im Raumname kodiert
        room_number = room.name
        capacity = room.capacity if hasattr(room, 'capacity') else 0
        equipment = "N/A"  # Falls WebUntis keine Ausstattung bereitstellt

        # Gebäude erstellen oder abrufen
        building, created = Building.objects.get_or_create(
            id=building_name,
            defaults={'name': building_name, 'floor_count': 1}  # Standardwerte für neue Gebäude
        )

        # Raum erstellen
        Room.objects.get_or_create(
            number=room_number,
            building=building,
            defaults={'capacity': capacity, 'equipment': equipment}
        )

    session.logout()

def preview_import_rooms():
    session.login()  # Anmeldung bei WebUntis

    # Gebäude und Räume abrufen
    rooms = session.rooms()  # Alle Räume abrufen

    buildings_set = set()  # Zum Speichern einzigartiger Gebäude
    rooms_list = []        # Zum Speichern der Räume

    for room in rooms:
        building_name = room.name.split('-')[0]  # Annahme: Gebäude im Raumname kodiert
        room_number = room.name
        capacity = room.capacity if hasattr(room, 'capacity') else 0
        equipment = "N/A"  # Falls WebUntis keine Ausstattung bereitstellt

        buildings_set.add(building_name)  # Gebäude zur Menge hinzufügen
        rooms_list.append({
            'Raum': room_number,
            'Gebäude': building_name,
            'Kapazität': capacity,
            'Ausstattung': equipment
        })

    session.logout()  # Abmelden

    # Gebäude und Räume ausgeben
    print("\nGefundene Gebäude:")
    for building in buildings_set:
        print(f"- {building}")

    print("\nGefundene Räume:")
    for room in rooms_list:
        print(f"- Raum: {room['Raum']}, Gebäude: {room['Gebäude']}, Kapazität: {room['Kapazität']}, Ausstattung: {room['Ausstattung']}")
