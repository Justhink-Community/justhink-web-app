# Generated by Django 4.0.3 on 2022-11-11 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_alter_profile_average_logged_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='average_logged_time',
        ),
    ]
