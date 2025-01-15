import datetime
import webuntis
from rooms.models import Room, RoomBooking, UserAccount
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Holt die Buchungen aus WebUntis und speichert sie in der Datenbank'

    def handle(self, *args, **kwargs):
        # WebUntis API-Verbindung
        with webuntis.Session(
            username='enter your username here',
            password='enter your password here',
            server='melpomene.webuntis.com',
            school='HS-Augsburg',
            useragent='WebUntis Test'
        ).login() as s:
            self.stdout.write(self.style.SUCCESS("Login erfolgreich!"))

            # Holen aller Räume
            rooms = s.rooms()
            room_mapping = {}

            # Räume abgleichen und Zuordnung erstellen
            for room in rooms:
                room_mapping[room.name] = room.id

            # Definiere den Zeitraum für Oktober, November und Dezember 2024
            year = 2024
            today = datetime.date.today()

            # Oktober: Beginn und Ende
            october_start = datetime.date(year, 10, 1)
            october_end = datetime.date(year, 10, 31)

            # November: Beginn und Ende
            november_start = datetime.date(year, 11, 1)
            november_end = datetime.date(year, 11, 30)

            # Dezember: Beginn und Ende
            december_start = datetime.date(year, 12, 1)
            december_end = datetime.date(year, 12, 31)

            # Gehe durch alle Räume in der Django-Datenbank
            for room in Room.objects.all():
                if room.number in room_mapping:
                    webuntis_room_id = room_mapping[room.number]

                    # Abrufen des Stundenplans für die einzelnen Monate
                    for start_date, end_date in [(october_start, october_end), (november_start, november_end), (december_start, december_end)]:
                        timetable = s.timetable(room=webuntis_room_id, start=start_date, end=end_date)

                        # Buchungen speichern
                        for event in timetable:
                            event_date = event.start.date()  # Datum
                            event_start_time = event.start.time()  # Startzeit
                            event_end_time = event.end.time()  # Endzeit

                            # Buchung in der Django-Datenbank speichern
                            RoomBooking.objects.create(
                                user=UserAccount.objects.get(email="danzerdaniel@yahoo.com"),
                                room=room,
                                booking_date=event_date,
                                start_time=event_start_time,
                                end_time=event_end_time
                            )

                    self.stdout.write(self.style.SUCCESS(f"Buchungen für {room.number} im Zeitraum Oktober bis Dezember 2024 wurden erfolgreich hinzugefügt."))
