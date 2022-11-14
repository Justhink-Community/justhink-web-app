import datetime
import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

from user_profile.models import Profile
from idea.models import Idea, Comment, Topic 



NOTIFICATION_TAGS = {
    "success": "checkmark-circle-outline",
    "error": "close-circle-outline",
    "warning": "alert-circle-outline",
    "info": "information-circle-outline",
}


def IndexView(request):
    ideas = Idea.objects.filter(Q(idea_archived = False))
    comments = Comment.objects.filter(Q(comment_archived = False))
    return render(
        request,
        "index.html",
        {
            "topic": Topic.objects.first(),
            "top_ideas": ideas,
            "comments_count": len(comments),
            "ideas_count": len(ideas),
        },
    )


def IdeasOverview(request):
    ideas = Idea.objects.filter(Q(idea_archived = False))
    comments = Comment.objects.filter(Q(comment_archived = False))
    return render(
        request,
        "ideas_overview.html",
        {
            "topic": Topic.objects.first(),
            "random_idea": random.choice(ideas),
            "comments_count": len(comments),
            "ideas_count": len(ideas),
        },
    )

def StatusView(request):
    return redirect('https://stats.uptimerobot.com/NyKm0fZmO3')
    
def InspectIdeaView(request, idea_id: int):
    try:
        idea_object = Idea.objects.get(Q(id=idea_id) & Q(idea_archived = False))
        comments = Comment.objects.filter(comment_idea = idea_object).order_by('comment_like_count').reverse()
    except Idea.DoesNotExist:
        return redirect("index-page")
    else:
        ideas = Idea.objects.filter(Q(idea_archived = False))
        all_comments = Comment.objects.filter(Q(comment_archived = False))
        return render(request, "inspect_idea.html", {"topic": Topic.objects.first(),'idea': idea_object, 'comments': comments,             "comments_count": len(all_comments),
            "ideas_count": len(ideas),})

@user_passes_test(lambda u: u.is_anonymous)
def LoginView(request):
    if request.POST:
        username, password = request.POST["username"], request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            messages.success(
                request,
                f"Başarıyla giriş yaptın: {username}",
                extra_tags=NOTIFICATION_TAGS["success"],
            )
            logged_in = datetime.datetime.now()
            
            profile = Profile.objects.get(account = user)
            profile.login_count += 1
            profile.last_logged_in = logged_in.replace(tzinfo=None)
            profile.save()
        else:
            messages.error(
                request,
                "Bilgilerinde hata var, kontrol et!",
                extra_tags=NOTIFICATION_TAGS["error"],
            )

        return redirect("index-page")


@user_passes_test(lambda u: u.is_anonymous)
def RegisterView(request):
    if request.POST:
        try:
            kvkk_check = request.POST["kvkk"]
        except KeyError:
            messages.error(
                request,
                "Kayıt olmak için KVKK'yı kabul etmelisin.",
                extra_tags=NOTIFICATION_TAGS["error"],
            )
        else:
            username, password, email = (
                request.POST["username-register"],
                request.POST["password-register"],
                request.POST["email"],
            )

            try:
                found_user = User.objects.filter(Q(username = username) | Q(email = email))
            except User.DoesNotExist:
                pass 
            else:
                if found_user:
                    messages.error(
                        request,
                        "Bu bilgilere ait bir hesap zaten var!",
                        extra_tags=NOTIFICATION_TAGS["error"],
                    )
                    return redirect('index-page')
            kvkk_check = True

            try:
                request.POST["emailperm"]
            except KeyError:
                email_perm = False
            else:
                email_perm = True

            user = User.objects.create_user(
                username=username, password=password, email=email
            )

            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    "Başarıyla hesabınızı oluşturdunuz.",
                    extra_tags=NOTIFICATION_TAGS["success"],
                )

                print(kvkk_check, email_perm)

                Profile.objects.create(
                    account=user,
                    web_theme="default-theme",
                    kvkk_agreed=kvkk_check,
                    email_permission=email_perm,
                    total_logged_time=datetime.timedelta(seconds=1),
                    last_logged_in=datetime.datetime.now()
                ).save()

            else:
                messages.error(
                    request,
                    "Hesabınız bizden kaynaklı bir sorundan ötürü oluşturulamadı. [#0001]",
                    extra_tags=NOTIFICATION_TAGS["error"],
                )

        return redirect("index-page")


@user_passes_test(lambda u: not u.is_anonymous)
def LogoutView(request):
    messages.info(
        request,
        f"Hesabınızdan çıkış yaptınız: {request.user.username}",
        extra_tags=NOTIFICATION_TAGS["info"],
    )
    logged_out = datetime.datetime.now()
    profile = Profile.objects.get(account = request.user)
    logged_time = logged_out - profile.last_logged_in
    profile.total_logged_time = profile.total_logged_time + logged_time
    profile.save()
    
    logout(request)
    

    return redirect("index-page")


def PublishIdeaView(request):
    if request.user.is_anonymous: 
        messages.error(
            request,
            "Bu işlem için giriş yapman gerekiyor!",
            extra_tags=NOTIFICATION_TAGS["error"],
        )
        return redirect(request.META['HTTP_REFERER'])

    if request.POST:
        idea_content = request.POST["idea-content"]

        Idea.objects.create(
            idea_author=Profile.objects.get(account=request.user),
            idea_content=idea_content,
        ).save()

        messages.success(
            request,
            "Başarıyla fikrinizi paylaştınız!",
            extra_tags=NOTIFICATION_TAGS["success"],
        )

        return redirect("index-page")


def LikePostView(request, post_id: int):
    if request.user.is_anonymous: 
        messages.error(
            request,
            "Bu işlem için giriş yapman gerekiyor!",
            extra_tags=NOTIFICATION_TAGS["error"],
        )
        return redirect('index-page')
  
    try:
        idea_object = Idea.objects.get(id=post_id)
    except Idea.DoesNotExist:
        return redirect("index-page")
    else:
        try:
            idea_object.idea_likes[request.user.username]
        except KeyError:
            idea_object.idea_like_count += 1
            idea_object.idea_likes[request.user.username] = True
            idea_object.save()
        else:
            idea_object.idea_like_count -= 1
            del idea_object.idea_likes[request.user.username]
            idea_object.save()

        return redirect(request.META['HTTP_REFERER'])




def SendCommentView(request, idea_id: int):
  if request.user.is_anonymous: 
      messages.error(
          request,
          "Bu işlem için giriş yapman gerekiyor!",
          extra_tags=NOTIFICATION_TAGS["error"],
      )
      return redirect('index-page')
  
  if request.POST:
    try:
        idea_object = Idea.objects.get(id=idea_id)
    except Idea.DoesNotExist:
        return redirect("inspect-idea-page", idea_id)
    else:
      comment_content = request.POST['comment-content']
      
      Comment.objects.create(comment_idea = idea_object, comment_author = Profile.objects.get(account=request.user), comment_content = comment_content).save()
      idea_object.idea_comments += 1
      idea_object.save()
      
      messages.success(
            request,
            "Başarıyla yorumunuzu paylaştınız!",
            extra_tags=NOTIFICATION_TAGS["success"],
        )

      return redirect("inspect-idea-page", idea_id)
    
def LikeCommentView(request, idea_id: int,  comment_id: int):
    if request.user.is_anonymous: 
      messages.error(
          request,
          "Bu işlem için giriş yapman gerekiyor!",
          extra_tags=NOTIFICATION_TAGS["error"],
      )
      return redirect(request.META['HTTP_REFERER'])
  
    try:
        comment_object = Comment.objects.get(id=comment_id)
    except Idea.DoesNotExist:
        return redirect("inspect-idea-page", idea_id)
    else:
        try:
            comment_object.comment_likes[request.user.username]
        except KeyError:
            try:
              comment_object.comment_dislikes[request.user.username]
            except KeyError:
              pass 
            else:
              comment_object.comment_dislike_count -= 1
              del comment_object.comment_dislikes[request.user.username]
            finally:
              comment_object.comment_like_count += 1
              comment_object.comment_likes[request.user.username] = True
              comment_object.save()
              
        else:
            comment_object.comment_like_count -= 1
            del comment_object.comment_likes[request.user.username]
            comment_object.save()

        return redirect("inspect-idea-page", idea_id)

def DislikeCommentView(request, idea_id: int,  comment_id: int):
    if request.user.is_anonymous: 
        messages.error(
            request,
            "Bu işlem için giriş yapman gerekiyor!",
            extra_tags=NOTIFICATION_TAGS["error"],
        )
        return redirect(request.META['HTTP_REFERER'])
  
    try:
        comment_object = Comment.objects.get(id=comment_id)
    except Idea.DoesNotExist:
        return redirect("inspect-idea-page", idea_id)
    else:
        try:
            comment_object.comment_dislikes[request.user.username]
        except KeyError:
            try:
              comment_object.comment_likes[request.user.username]
            except KeyError:
              pass 
            else:
              comment_object.comment_like_count -= 1
              del comment_object.comment_likes[request.user.username]
            finally:
              comment_object.comment_dislike_count += 1
              comment_object.comment_dislikes[request.user.username] = True
              comment_object.save()
        else:
            comment_object.comment_dislike_count -= 1
            del comment_object.comment_dislikes[request.user.username]
            comment_object.save()

        return redirect("inspect-idea-page", idea_id)
      
def handle_404(request, exception):
  return render(request, '404.html')