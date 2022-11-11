import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test

from user_profile.models import Profile
from idea.models import Idea, Comment, Topic


NOTIFICATION_TAGS = {
    "success": "checkmark-circle-outline",
    "error": "close-circle-outline",
    "warning": "alert-circle-outline",
    "info": "information-circle-outline",
}


def IndexView(request):
    return render(
        request,
        "index.html",
        {
            "topic": Topic.objects.first(),
            "top_ideas": Idea.objects.all(),
            "comments_count": len(Comment.objects.all()),
            "ideas_count": len(Idea.objects.all()),
        },
    )


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
                request.POST["username"],
                request.POST["password"],
                request.POST["email"],
            )

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
    print(logged_out, profile.last_logged_in)
    logged_time = logged_out - profile.last_logged_in
    profile.total_logged_time = logged_time
    profile.save()
    
    logout(request)
    

    return redirect("index-page")


@user_passes_test(lambda u: not u.is_anonymous)
def PublishIdeaView(request):
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


@user_passes_test(lambda u: not u.is_anonymous)
def LikePostView(request, post_id: int):
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

        return redirect("index-page")


def InspectIdeaView(request, idea_id: int):
    try:
        idea_object = Idea.objects.get(id=idea_id)
        comments = Comment.objects.filter(comment_idea = idea_object).order_by('comment_like_count').reverse()
    except Idea.DoesNotExist:
        return redirect("index-page")
    else:

        return render(request, "inspect_idea.html", {"topic": Topic.objects.first(),'idea': idea_object, 'comments': comments,             "comments_count": len(Comment.objects.all()),
            "ideas_count": len(Idea.objects.all()),})

@user_passes_test(lambda u: not u.is_anonymous)
def SendCommentView(request, idea_id: int):
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
    
@user_passes_test(lambda u: not u.is_anonymous)
def LikeCommentView(request, idea_id: int,  comment_id: int):
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
      
    
@user_passes_test(lambda u: not u.is_anonymous)
def DislikeCommentView(request, idea_id: int,  comment_id: int):
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
      
def DevToolsView(request):
  if request.user.is_superuser:
    return render(request, 'status.html', {'accounts': User.objects.all(), 'ideas': Idea.objects.all(), 'comments': Comment.objects.all(), 'profiles': Profile.objects.all()})
  else:
    return redirect('index-page')