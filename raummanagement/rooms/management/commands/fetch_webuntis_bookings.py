from django.core.management.base import BaseCommand
import webuntis
import datetime
from rooms.models import Room, RoomBooking, UserAccount

class Command(BaseCommand):
    help = 'Holt die Buchungen aus WebUntis und speichert sie in der Datenbank'

    def handle(self, *args, **kwargs):
        # WebUntis API-Verbindung
        with webuntis.Session(
            username='danzer',
            password='Gullasch123!',
            server='melpomene.webuntis.com',
            school='HS-Augsburg',
            useragent='WebUntis Test'
        ).login() as s:
            self.stdout.write(self.style.SUCCESS("Login erfolgreich!"))

            # Holen aller Räume aus WebUntis
            untis_rooms = s.rooms()  # Hier wird das WebUntis Raum-Objekt umbenannt
            room_mapping = {}

            # Räume abgleichen und Zuordnung erstellen (WebUntis name -> Django number)
            for untis_room in untis_rooms:  # Umbenannt zu untis_room
                room_mapping[untis_room.name] = untis_room.id  # WebUntis name zu WebUntis room.id

            # Datum für den Zeitraum (letzter Monat bis heute)
            today = datetime.date.today()
            last_month = today - datetime.timedelta(days=30)

            # Gehe durch alle Räume in der Django-Datenbank
            for room in Room.objects.all():  # Dies bleibt der Django Room
                if room.number in room_mapping:  # Vergleiche Django room.number mit WebUntis room.name
                    webuntis_room_id = room_mapping[room.number]  # Verwende die Zuordnung basierend auf room.number

                    # Abrufen des Stundenplans für den Raum aus WebUntis
                    timetable = s.timetable(room=webuntis_room_id, start=last_month, end=today)

                    # Buchungen speichern
                    for event in timetable:
                        print(event)
                        # Extrahiere das Datum (YYYYMMDD) und konvertiere es zu einem Datum
                        booking_date = datetime.datetime.strptime(str(event['date']), "%Y%m%d").date()

                        # Extrahiere Start- und Endzeit (HHMM) und konvertiere sie in Zeitobjekte
                        start_time = datetime.datetime.strptime(str(event['startTime']).zfill(4), "%H%M").time()
                        end_time = datetime.datetime.strptime(str(event['endTime']).zfill(4), "%H%M").time()

                        # Extrahiere die Raum-ID
                        room_id = event['ro'][0]['id']  # Hier verwenden wir die erste Raum-ID

                        # Finde den entsprechenden Raum in der Datenbank anhand der ID
                        try:
                            room = Room.objects.get(id=room_id)
                        except Room.DoesNotExist:
                            print(f"Raum mit ID {room_id} wurde nicht gefunden.")
                            continue

                        # Speichern der Buchung in der Django-Datenbank
                        RoomBooking.objects.create(
                            user=UserAccount.objects.get(email="danzerdaniel@yahoo.com"),
                            room=room,
                            booking_date=booking_date,
                            start_time=start_time,
                            end_time=end_time
                        )

                        self.stdout.write(self.style.SUCCESS(
                            f"Buchung für Raum {room.number} am {booking_date} von {start_time} bis {end_time} wurde erfolgreich hinzugefügt."))
