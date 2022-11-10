# Generated by Django 4.0.3 on 2022-11-10 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idea', '0003_idea_idea_like_count_alter_idea_idea_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_dislike_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_dislikes',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_like_count',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_likes',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='idea',
            name='idea_likes',
            field=models.JSONField(default=dict),
        ),
    ]