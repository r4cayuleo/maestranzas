# Generated by Django 5.0.7 on 2024-07-11 02:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_material_condition_material_date_added_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='material',
            options={'permissions': [('can_analyze_inventory', 'Can analyze inventory')]},
        ),
    ]
