import datetime
import httpagentparser
import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

from user_profile.models import Profile
from idea.models import Idea, Comment, Topic

from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail

from django.core.cache import cache


NOTIFICATION_TAGS = {
    "success": "/static/images/icons/check-circle-outline.svg",
    "error": "/static/images/icons/cross-circled.svg",
    "warning": "/static/images/icons/warning-circle-outline.svg",
    "info": "/static/images/icons/info-outline.svg",
}

POINT_POLICY = {
    "like_idea": 1,
    "daily_strike": {
        0: 10,
        1: 15,
        2: 20,
        3: 25,
        4: 30,
        5: 40,
        6: 50,
    },
}


def IncrementLogin(request):
    if not request.user.is_anonymous:
        agent = request.META["HTTP_USER_AGENT"]
        parsed_agent = httpagentparser.detect(agent)
        platform, os, is_bot, browser = (
            " ".join(parsed_agent["platform"].values()),
            " ".join(parsed_agent["os"].values()),
            parsed_agent["bot"],
            " ".join(parsed_agent["browser"].values()),
        )

        try:
            user_profile = Profile.objects.get(account=request.user)
        except Profile.DoesNotExist:
            pass
        else:
            if user_profile.last_logged_in.day != datetime.datetime.now().day:
                if user_profile.login_strike is None:
                    user_profile.login_strike = 0
                try:
                    user_profile.total_point = (
                        int(user_profile.total_point)
                        + POINT_POLICY["daily_strike"][user_profile.login_strike]
                    )
                except:
                    user_profile.total_point = POINT_POLICY["daily_strike"][
                        user_profile.login_strike
                    ]
                user_profile.login_strike += 1
                if user_profile.login_strike >= 7:
                    user_profile.login_strike = 0

            user_profile.login_count += 1
            user_profile.last_logged_in = datetime.datetime.now()
            logged_time = user_profile.last_logged_in - request.user.date_joined
            user_profile.total_logged_time = logged_time

            user_profile.profile_user = "Belirlenemedi"

            try:
                user_profile.profile_platforms[platform] = str(
                    user_profile.last_logged_in
                )
            except TypeError:
                user_profile.profile_platforms = {}
                user_profile.profile_platforms[platform] = str(
                    user_profile.last_logged_in
                )

            try:
                user_profile.profile_oses[os] = str(user_profile.last_logged_in)
            except TypeError:
                user_profile.profile_oses = {}
                user_profile.profile_oses[os] = str(user_profile.last_logged_in)

            try:
                user_profile.profile_browsers[browser] = str(
                    user_profile.last_logged_in
                )
            except TypeError:
                user_profile.profile_browsers = {}
                user_profile.profile_browsers[browser] = str(
                    user_profile.last_logged_in
                )

            user_profile.is_bot = is_bot
            if user_profile.profile_rank is None:
                user_profile.profile_rank = "rookie"

            user_profile.save()


def GivePoint(user, amount):
    try:
        user_profile = Profile.objects.get(account=user)
    except Profile.DoesNotExist:
        pass
    else:
        try:
            user_profile.total_point = int(user_profile.total_point) + int(amount)
        except:
            user_profile.total_point = 0
        user_profile.save()


# def TakePoint(user, amount):
#     try:
#         user_profile = Profile.objects.get(account=request.user)
#     except Profile.DoesNotExist:
#         pass
#     else:
#         try:
#             if user_profile.total_point >= amount
#             user_profile.total_point -= amount
#         except:
#             user_profile.total_point = 0
#         user_profile.save()


def get_user_profile(user):
    try:
        profile = Profile.objects.get(account=user)
    except Profile.DoesNotExist:
        return False
    except TypeError:
        return False
    else:
        return profile


def IndexView(request):
    ideas = Idea.objects.filter(Q(idea_archived=False))

    comments = Comment.objects.filter(Q(comment_archived=False))

    IncrementLogin(request)

    return render(
        request,
        "index.html",
        {
            "profile": get_user_profile(request.user),
            "topic": Topic.objects.first(),
            "top_ideas": random.sample([*ideas], 2) if len(ideas) >= 2 else ideas,
            "comments_count": len(comments),
            "ideas_count": len(ideas),
            "section": "summary",
        },
    )


def ShopView(request):
    IncrementLogin(request)

    return render(
        request,
        "shop.html",
        {
            "profile": get_user_profile(request.user),
            "section": "shop",
        },
    )

def FavouriteIdeasView(request):
    ideas = Idea.objects.filter(Q(idea_archived=False))
    comments = Comment.objects.filter(Q(comment_archived=False))
    IncrementLogin(request)

    return render(
        request,
        "index.html",
        {
            "profile": get_user_profile(request.user),
            "topic": Topic.objects.first(),
            "top_ideas": ideas.order_by("-idea_like_count")
            if len(ideas) >= 2
            else ideas,
            "comments_count": len(comments),
            "ideas_count": len(ideas),
            "section": "favourites",
        },
    )


def TrendIdeasView(request):
    ideas = Idea.objects.filter(Q(idea_archived=False))
    comments = Comment.objects.filter(Q(comment_archived=False))
    IncrementLogin(request)
    return render(
        request,
        "index.html",
        {
            "profile": get_user_profile(request.user),
            "topic": Topic.objects.first(),
            "top_ideas": ideas.order_by("-idea_comments") if len(ideas) >= 2 else ideas,
            "comments_count": len(comments),
            "ideas_count": len(ideas),
            "section": "trends",
        },
    )


def IdeasOverview(request):
    ideas = Idea.objects.filter(Q(idea_archived=False))
    comments = Comment.objects.filter(Q(comment_archived=False))
    IncrementLogin(request)
    return render(
        request,
        "ideas_overview.html",
        {
            "profile": get_user_profile(request.user),
            "topic": Topic.objects.first(),
            "random_idea": random.choice(ideas) if len(ideas) >= 2 else ideas,
            "comments_count": len(comments),
            "ideas_count": len(ideas),
            "section": "idea-overview",
        },
    )


def StatusView(request):
    return redirect("https://stats.uptimerobot.com/NyKm0fZmO3")


def StatisticsView(request):
    if request.user.is_superuser:
        users, ideas, comments = (
            User.objects.all(),
            Idea.objects.all(),
            Comment.objects.all(),
        )
        users_who_has_written_idea = set([idea.idea_author for idea in ideas])

        users_who_has_used_website_2_days = [
            idea.idea_author
            for idea in ideas
            if len(Idea.objects.filter(Q(idea_author=idea.idea_author))) >= 2
        ]

        char_count_of_total_ideas = sum([len(idea.idea_content) for idea in ideas])
        word_count_of_total_ideas = sum(
            [len(idea.idea_content.split(" ")) for idea in ideas]
        )
        sentence_count_of_total_ideas = sum(
            [len(idea.idea_content.split(".")) for idea in ideas]
        )

        char_count_of_total_comments = sum(
            [len(comment.comment_content) for comment in comments]
        )
        word_count_of_total_comments = sum(
            [len(comment.comment_content.split(" ")) for comment in comments]
        )
        sentence_count_of_total_comments = sum(
            [len(comment.comment_content.split(".")) for comment in comments]
        )

        words = [
            word.lower() for idea in ideas for word in idea.idea_content.split(" ")
        ] + [
            word.lower()
            for comment in comments
            for word in comment.comment_content.split(" ")
        ]

        temporary = {}
        show_case = {}

        for sub in words:
            try:
                temporary[sub] += 1
            except KeyError:
                temporary[sub] = 1

        for temp, tval in temporary.items():
            if tval >= 10:
                show_case[temp] = f"{((tval * 100) / len(words))} %"
                # tval ?
                # total 100

        user_register_dates = {}

        for user in users:
            try:
                user_register_dates[user.date_joined.day] += 1
            except KeyError:
                user_register_dates[user.date_joined.day] = 1

        idea_publish_dates = {}

        for idea in ideas:
            try:
                idea_publish_dates[idea.idea_publish_date.day] += 1
            except KeyError:
                idea_publish_dates[idea.idea_publish_date.day] = 1

        comment_publish_dates = {}

        for comment in comments:
            try:
                comment_publish_dates[comment.comment_publish_date.day] += 1
            except KeyError:
                comment_publish_dates[comment.comment_publish_date.day] = 1

        print(
            """JUSTHINK STATS 

        Total Users: {}
        Total Ideas: {}
        Total Comments: {}

        Users Who Has Written An Idea: {}
        Users Who Has Used the Website At Least 2 Days: {}

        Total Idea Char Count: {}
        Total Idea Word Count: {}
        Total Idea Sentence Count: {}
        Avr. Ideas' Word Length: {} 

        Total Comment Char Count: {}
        Total Comment Word Count: {}
        Total Comment Sentence Count: {}
        Avr. Comment' Word Length: {} 

        Total Char Count: {}
        Total Word Count: {}
        Total Sentence Count: {}
        Avr. Word Length: {}

        Max Used Words: {}
        User Dates: {}
        Idea Dates: {}
        Comment Dates: {}

        """.format(
                len(users),
                len(ideas),
                len(comments),
                len(users_who_has_written_idea),
                len(users_who_has_used_website_2_days),
                char_count_of_total_ideas,
                word_count_of_total_ideas,
                sentence_count_of_total_ideas,
                char_count_of_total_ideas / word_count_of_total_ideas,
                char_count_of_total_comments,
                word_count_of_total_comments,
                sentence_count_of_total_comments,
                char_count_of_total_comments / word_count_of_total_comments,
                char_count_of_total_ideas + char_count_of_total_comments,
                word_count_of_total_ideas + word_count_of_total_comments,
                sentence_count_of_total_comments + sentence_count_of_total_ideas,
                (
                    (char_count_of_total_comments / word_count_of_total_comments)
                    + (char_count_of_total_ideas / word_count_of_total_ideas)
                )
                / 2,
                show_case,
                user_register_dates,
                idea_publish_dates,
                comment_publish_dates,
            )
        )
        return redirect("index-page")


def InspectIdeaView(request, idea_id: int):
    try:
        idea_object = Idea.objects.get(Q(id=idea_id) & Q(idea_archived=False))
        comments = (
            Comment.objects.filter(comment_idea=idea_object)
            .order_by("comment_like_count")
            .reverse()
        )
    except Idea.DoesNotExist:
        return redirect("index-page")
    else:
        ideas = Idea.objects.filter(Q(idea_archived=False))
        all_comments = Comment.objects.filter(Q(comment_archived=False))
        return render(
            request,
            "inspect_idea.html",
            {
                "topic": Topic.objects.first(),
                "idea": idea_object,
                "comments": comments,
                "comments_count": len(all_comments),
                "ideas_count": len(ideas),
                "section": "inspect-idea",
            },
        )


def EditIdeaView(request, idea_id: int):
    return redirect(request.META.get("HTTP_REFERER"))


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

            profile = Profile.objects.get(account=user)
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
                found_user = User.objects.filter(Q(username=username) | Q(email=email))
            except User.DoesNotExist:
                pass
            else:
                if found_user:
                    messages.error(
                        request,
                        "Bu bilgilere ait bir hesap zaten var!",
                        extra_tags=NOTIFICATION_TAGS["error"],
                    )
                    return redirect("index-page")
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

                Profile.objects.create(
                    account=user,
                    web_theme="default-theme",
                    kvkk_agreed=kvkk_check,
                    email_permission=email_perm,
                    total_logged_time=datetime.timedelta(seconds=1),
                    last_logged_in=datetime.datetime.now(),
                    profile_rank="rookie",
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
    ),

    logged_out = datetime.datetime.now()
    profile = Profile.objects.get(account=request.user)
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
        return redirect(request.META["HTTP_REFERER"])

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
        return redirect("index-page")

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

            GivePoint(idea_object.idea_author.account, POINT_POLICY["like_idea"])

        else:
            idea_object.idea_like_count -= 1
            del idea_object.idea_likes[request.user.username]
            idea_object.save()

        return redirect(request.META["HTTP_REFERER"])


def SendCommentView(request, idea_id: int):
    if request.user.is_anonymous:
        messages.error(
            request,
            "Bu işlem için giriş yapman gerekiyor!",
            extra_tags=NOTIFICATION_TAGS["error"],
        )
        return redirect("index-page")

    if request.POST:
        try:
            idea_object = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return redirect("inspect-idea-page", idea_id)
        else:
            comment_content = request.POST["comment-content"]

            Comment.objects.create(
                comment_idea=idea_object,
                comment_author=Profile.objects.get(account=request.user),
                comment_content=comment_content,
            ).save()
            idea_object.idea_comments += 1
            idea_object.save()

            messages.success(
                request,
                "Başarıyla yorumunuzu paylaştınız!",
                extra_tags=NOTIFICATION_TAGS["success"],
            )

            return redirect("inspect-idea-page", idea_id)


def LikeCommentView(request, idea_id: int, comment_id: int):
    if request.user.is_anonymous:
        messages.error(
            request,
            "Bu işlem için giriş yapman gerekiyor!",
            extra_tags=NOTIFICATION_TAGS["error"],
        )
        return redirect(request.META["HTTP_REFERER"])

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


def DislikeCommentView(request, idea_id: int, comment_id: int):
    if request.user.is_anonymous:
        messages.error(
            request,
            "Bu işlem için giriş yapman gerekiyor!",
            extra_tags=NOTIFICATION_TAGS["error"],
        )
        return redirect(request.META["HTTP_REFERER"])

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
    return render(request, "404.html")
