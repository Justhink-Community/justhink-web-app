# from django import template
# from django.db.models import Q
# from idea.models import Idea

# register = template.Library()

# @register.filter(name='like_idea')
# def like_idea(idea, user):
#     try:
#       user.attented += 1
#     except:
#       user.attented = 0
#       return False
#     else:
#       if user.attented != len(Idea.objects.filter(Q(idea_archived = False))):
#         return False

#     if not user.is_anonymous and not idea.idea_archived:
  
#       try:
#           idea.idea_likes[user.username]
#       except KeyError:
#           idea.idea_like_count += 1
#           idea.idea_likes[user.username] = True
#           idea.save()
#       else:
#           idea.idea_like_count -= 1
#           del idea.idea_likes[user.username]
#           idea.save()
#       return True 
#     else:
#       return False