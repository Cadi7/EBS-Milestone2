# Generated by Django 3.1.14 on 2022-09-19 12:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelog',
            name='duration',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='timelog',
            name='started_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
