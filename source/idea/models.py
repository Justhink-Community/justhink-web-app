from user_profile.models import Profile

from django.db import models


from django.contrib.postgres import fields


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


class Comment(models.Model):
    comment_idea = models.ForeignKey(to=Idea, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(to=Profile, on_delete=models.CASCADE)
    comment_content = models.TextField()
    comment_publish_date = models.DateTimeField(auto_now=True)

    comment_likes = models.JSONField(editable=False, default=dict)
    comment_like_count = models.IntegerField(editable=False, default=0)
    
    comment_dislikes = models.JSONField(editable=False, default=dict)
    comment_dislike_count = models.IntegerField(editable=False, default=0)
    
class Topic(models.Model):
  topic_name = models.CharField(max_length=100)
  topic_sources = models.TextField()
  topic_keywords = models.CharField(max_length=40)