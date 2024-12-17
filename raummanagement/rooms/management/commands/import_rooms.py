import csv
from django.core.management.base import BaseCommand
from rooms.models import Room, Building

class Command(BaseCommand):
    help = 'Import rooms from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="The path to the CSV file to be imported")

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Ensure the building exists, and use 'defaults' for floor_count
                    building, created = Building.objects.get_or_create(
                        id=row['building_id'],
                        defaults={'name': f"Building {row['building_id']}", 'floor_count': row.get('floor_count', 1)}
                    )

                    # Create a room for the building
                    Room.objects.create(
                        number=row['number'],
                        capacity=row['capacity'],
                        equipment=row['equipment'],
                        building=building
                    )
            self.stdout.write(self.style.SUCCESS('Rooms imported successfully!'))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File {csv_file} not found"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
