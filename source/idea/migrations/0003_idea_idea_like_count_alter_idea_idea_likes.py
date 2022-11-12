# Generated by Django 4.0.3 on 2022-11-09 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idea', '0002_alter_idea_idea_comments_alter_idea_idea_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='idea_like_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='idea',
            name='idea_likes',
            field=models.JSONField(),
        ),
    ]
