# Generated by Django 5.0.7 on 2024-07-10 23:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_location_max_capacity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'permissions': [('can_manage_storage', 'Can manage storage')]},
        ),
    ]
