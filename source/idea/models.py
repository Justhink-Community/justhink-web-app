import datetime
from user_profile.models import Profile
from django.contrib.auth.models import User
from django.db import models

from django.contrib.postgres import fields
from django.core.mail import send_mail

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection, EmailMultiAlternatives


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)

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

    idea_topic = models.CharField(max_length=100, default="Belirlenemedi.", null=True, editable=True)

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

    comment_topic = models.CharField(max_length=100, default="Belirlenemedi.", null=True, editable=True)

    comment_archived = models.BooleanField(default=False)
    
class Topic(models.Model):
  topic_name = models.CharField(max_length=100)
  topic_sources = models.TextField()
  topic_keywords = models.CharField(max_length=40)
  topic_date = models.DateTimeField()
#   topic_suggested_user = models.ForeignKey(to=User, on_delete=models.CASCADE, default=User.objects.get(models.Q(username = 'justhink')))
  topic_video_id = models.CharField(max_length=16)
  topic_rate = models.JSONField(default=dict, null=True, blank=True, editable=True)
  topic_survey = models.JSONField(null=False, blank=False, default=dict)
  special_topic_message = models.CharField(max_length=70, default="Bu pazar günü Yıldızlararası filmini tartışıyoruz!", blank=False, null=False)

  def save(self, *args, **kwargs):
    today = datetime.datetime.now()
    # print(args, kwargs)
    if today.date() != self.topic_date.date(): 
        self.topic_date = today 
    
        

    # t = threading.Thread(target=self.send_mail,)
    # t.start()   

    
    super().save(*args, **kwargs)
  def send_mail(self):
        ctx = {
        'subtitle': 'Günün konusu hazır:',
        'title': self.topic_name,
        'paragraph_1': self.topic_sources[:500] + '...'
        }
        html_message = render_to_string('dynamic_mail.html', ctx)
        plain_message = strip_tags(html_message)
        send_mass_html_mail(
            [('Günün konusu hazır! - justhink.net', plain_message, html_message, 'iletisim@justhink.net', [user.email]) for user in [User.objects.get(username="justhink")]],
        fail_silently=True)


UPDATE_GENRES = (
    ('bugfix', 'Bugfix'),
    ('design', 'Design'),
    ('development', 'Development'),
    ('cybersecurity', 'Cyber Security'),
    ('dbms', 'DBMS'),
)

class Update(models.Model):
    update_genre = models.CharField(choices=UPDATE_GENRES, max_length=20)
    update_work = models.CharField(max_length=75)
    update_date = models.DateTimeField(auto_now_add=True)
    update_authors = models.CharField(max_length=20)
    
class Product(models.Model):
  product_name = models.CharField(max_length=20)
  product_description = models.CharField(max_length=100)
  product_fee = models.IntegerField()
  product_image = models.URLField()
  product_sold_count = models.IntegerField(editable=False, null=False, default=0)


class Feedback(models.Model):
    feedback_author = models.ForeignKey(to=Profile, on_delete=models.CASCADE)
    feedback_fullname = models.CharField(max_length=40)
    feedback_email = models.EmailField()
    feedback_message = models.TextField()