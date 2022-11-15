import datetime

from user_profile.models import Profile
from django.contrib.auth.models import User
from django.db import models

from django.contrib.postgres import fields
from django.core.mail import send_mail

from django.template import Context
from django.template.loader import render_to_string, get_template


class OldJSONField(fields.JSONField):
    def db_type(self, connection):
        return 'json'
class Idea(models.Model):
    idea_author = models.ForeignKey(to=Profile, on_delete=models.CASCADE)
    idea_content = models.TextField()
    idea_publish_date = models.DateTimeField(auto_now=True)

    idea_likes = models.JSONField(default=dict)
    idea_like_count = models.IntegerField(editable=False, default=0)
    idea_comments = models.IntegerField(editable=False, default=0)

    idea_archived = models.BooleanField(default=False)
    
class Comment(models.Model):
    comment_idea = models.ForeignKey(to=Idea, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(to=Profile, on_delete=models.CASCADE)
    comment_content = models.TextField()
    comment_publish_date = models.DateTimeField(auto_now=True)

    comment_likes = models.JSONField(editable=False, default=dict)
    comment_like_count = models.IntegerField(editable=False, default=0)
    
    comment_dislikes = models.JSONField(editable=False, default=dict)
    comment_dislike_count = models.IntegerField(editable=False, default=0)

    comment_archived = models.BooleanField(default=False)
    
class Topic(models.Model):
  topic_name = models.CharField(max_length=100)
  topic_sources = models.TextField()
  topic_keywords = models.CharField(max_length=40)
  topic_date = models.DateField(auto_created=True)
  topic_suggested_user = models.ForeignKey(to=User, on_delete=models.CASCADE, default=User.objects.get(models.Q(username = 'justhink')))

  def save(self, *args, **kwargs):
    today = datetime.datetime.now().date()
    if today != self.topic_date: 
        Idea.objects.all().update(idea_archived = True) 
        Comment.objects.all().update(comment_archived = True) 
    
    # ctx = {
    #     'subtitle': 'Günün konusu hazır:',
    #     'title': self.topic_name,
    #     'paragraph_1': self.topic_sources
    # }
    # message = get_template('dynamic_mail.html').render(ctx)
    # send_mail('Günün konusu hazır! - justhink.net', message, 'iletisim@justhink.net', ['furkanesen1900@gmail.com'])
    super().save(*args, **kwargs)