# Generated by Django 5.1.4 on 2024-12-09 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_useraccount_is_active_useraccount_is_staff_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
