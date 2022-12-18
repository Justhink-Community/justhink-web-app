import datetime
import random
import string
import httpagentparser
import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

from user_profile.models import Profile
from idea.models import Idea, Comment, Topic, Update, Product

from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection, EmailMultiAlternatives

from idea.models import send_mass_html_mail

from django.core.cache import cache

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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

BADGES = {
    'ADMINISTRATION_TEAM': 'static/images/badges/admin.svg',
    'CONTENT_TEAM': 'static/images/badges/content-team.svg',
    'SOFTWARE_TEAM': 'static/images/badges/software-team.svg',
    'SOFTWARE_LEAD': 'static/images/badges/software-lead.svg'
}


def get_user_badge(user) -> str:
    user_groups = [str(group) for group in user.groups.all()]

    if 'Administration Team' in user_groups:
        user_admin_badge = 'SOFTWARE_LEAD' if 'Software Team' in user_groups else 'ADMINISTRATION_TEAM'
        return open(BADGES[user_admin_badge], encoding='utf-8').read() 
    elif 'Content Team' in user_groups:
        return open(BADGES['CONTENT_TEAM'], encoding='utf-8').read()
    elif 'Software Team' in user_groups:
        return open(BADGES['SOFTWARE_TEAM'], encoding='utf-8').read()

    return ''

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_time_span(compared):
    compared = compared.split('.')[0]
    compared = datetime.datetime.strptime(compared, '%Y-%m-%d %H:%M:%S')
    time_span = (datetime.datetime.now() - compared).seconds
    if ((time_span // 60) // 60) // 24 >= 1:
      time_span = f'{((time_span // 60) // 60)} gün önce'
    elif (time_span // 60) // 60 >= 1:
      time_span = f'{(time_span // 60) // 60} saat önce'
    elif (time_span // 60) >= 1:
      time_span = f'{(time_span // 60)} dakika önce'
    else:
      time_span = f'{(time_span)} saniye önce'
    return time_span
  
def create_hash(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

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
            try:
                if user_profile.user_restricted:
                    return render(request, "404.html")
            except KeyError:
                pass 

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
            try:
                user_profile.ip_addresses[get_client_ip(request)] = str(user_profile.last_logged_in)
            except TypeError:
                user_profile.ip_addresses = {}
                user_profile.ip_addresses[get_client_ip(request)] = str(user_profile.last_logged_in)

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

            # print(user_profile.web_theme)
            
            today_topic = Topic.objects.first()
            
            try:
              user_profile.user_notifications[today_topic.topic_name]
            except TypeError:
              user_profile.user_notifications = {}
              
              user_profile.user_notifications[today_topic.topic_name] = {
                'notification_content': f'Günün konusu yayında: {today_topic.topic_name}',
                'notification_details': str(today_topic.topic_date),
                'notification_image': 'robot',
                'notification_link': '/',
                'viewed': False
              }
            except KeyError: 
              
              user_profile.user_notifications[today_topic.topic_name] = {
                'notification_content': f'Günün konusu yayında: {today_topic.topic_name}',
                'notification_details': str(today_topic.topic_date),
                'notification_image': 'robot',
                'notification_link': '/',
                'viewed': False
              }
              
            

            user_profile.save()


def GivePoint(user, amount):
    try:
        user_profile = Profile.objects.get(account=user)
    except Profile.DoesNotExist:
        return False
    try:
        user_profile.total_point = int(user_profile.total_point) + int(amount)
    except:
        user_profile.total_point = 0
    user_profile.save()


def TakePoint(user, amount):
    try:
        user_profile = Profile.objects.get(account=user)
    except Profile.DoesNotExist:
        return False
    try:
        user_profile.total_point = int(user_profile.total_point) - int(amount)
    except:
        user_profile.total_point = 0
    user_profile.save()


def get_user_profile(user):
    try:
        profile = Profile.objects.get(account=user)
    except Profile.DoesNotExist:
        return False
    except TypeError:
        return False
    else:
        profile.user_notifications = dict(
          sorted(profile.user_notifications.items(), 
                key=lambda notification: notification[1]['notification_details'],
                reverse=True
                )
          )

        profile.save()
        return profile

def DashBoardView(request):
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

def IndexView(request):
    if request.user.is_anonymous:
        return LandingView(request)

    return DashBoardView(request)

@user_passes_test(lambda u: not u.is_anonymous)
def ShopView(request):
    user_profile = get_user_profile(request.user)
  
  
    if request.POST:
      product_name = request.POST['product_name']
      
      try:
        product = Product.objects.get(Q(product_name=product_name))
      except Product.DoesNotExist:
        messages.error(request, 'Ürün veritabanında bulunamadı!', extra_tags=NOTIFICATION_TAGS['error'])
      else:
        if user_profile.total_point >= product.product_fee:
          try:
            user_profile.shop_bought_products[product_name]
          except KeyError:
            pass 
          except TypeError:
            user_profile.shop_bought_products = {}
          else:
            return messages.error(request, 'Bu ürünü zaten almışsın!', extra_tags=NOTIFICATION_TAGS["error"])
          
          user_profile.web_theme = product_name
          user_profile.total_point -= product.product_fee
          user_profile.shop_bought_products[product_name] = str(datetime.datetime.now())
          product.product_sold_count += 1
          
          user_profile.save()
          product.save()
          
          messages.success(request, 'Ürün başarıyla satın alındı!', extra_tags=NOTIFICATION_TAGS['success'])
          
        else:
          messages.error(request, 'Puanınız yetersiz!', extra_tags=NOTIFICATION_TAGS['error'])
          

    IncrementLogin(request)

    return render(
        request,
        "shop.html",
        {
            "profile": user_profile,
            "section": "shop",
            "products": Product.objects.all()
        },
    )

@user_passes_test(lambda u: not u.is_anonymous)
def ChangeThemeView(request):
  if request.GET:
    user_profile = get_user_profile(request.user)
    product_name = request.GET['product_name']
    
    if product_name != 'Thinker Tema':

        try:
            user_profile.shop_bought_products[product_name]
        except KeyError:
            messages.error(request, 'Bu ürün satın alınmamış.', extra_tags=NOTIFICATION_TAGS['error'])
        except TypeError:
            user_profile.shop_bought_products = {}
            user_profile.save()
            messages.error(request, 'Bu ürün satın alınmamış.', extra_tags=NOTIFICATION_TAGS['error'])
        else:
            product_code = product_name
            if user_profile.web_theme != product_code:
                user_profile.web_theme = product_code
                user_profile.save()
                messages.success(request, f'Tema değiştirildi: {product_name}', extra_tags=NOTIFICATION_TAGS["success"])
            else:
                messages.error(request, 'Zaten bu tema aktifleştirilmiş.', extra_tags=NOTIFICATION_TAGS['error'])
        finally:
            return render(request, 'shop.html',         {
                    "profile": user_profile,
                    "section": "shop",
                    "products": Product.objects.all(),
                },)
    else:
        product_code = product_name
        if user_profile.web_theme != product_code:
            user_profile.web_theme = product_code
            user_profile.save()
            messages.success(request, f'Tema değiştirildi: {product_name}', extra_tags=NOTIFICATION_TAGS["success"])
        else:
            messages.error(request, 'Zaten bu tema aktifleştirilmiş.', extra_tags=NOTIFICATION_TAGS['error'])
    return render(request, 'shop.html',         {
        "profile": user_profile,
        "section": "shop",
        "products": Product.objects.all(),
    },)


def LandingView(request):
    IncrementLogin(request)

    topic = Topic.objects.first()

    return render(
        request,
        "home.html",
        {
            "profile": get_user_profile(request.user),
            "topic_name": topic.topic_name[:40],
            "topic_sources": topic.topic_sources[:300],
            "section": "home",
        },
    ) 
    
def AboutUsView(request):
  IncrementLogin(request)
  
  return render(request, "about_us.html", {"section": "about-us", "profile": get_user_profile(request.user)})

@user_passes_test(lambda u: u.is_anonymous)
def AuthenticationView(request):
    if request.POST:
      
      username, password = request.POST["username"], request.POST["password"]
      user = authenticate(username=username, password=password)

      if user is not None:
          login(request, user)
          print(user)

          messages.success(
              request,
              f"Başarıyla giriş yaptın: {username}",
              extra_tags=NOTIFICATION_TAGS["success"],
          )
          
          return redirect('profile-page')
      else:
          messages.error(
              request,
              "Bilgilerinde hata var, kontrol et!",
              extra_tags=NOTIFICATION_TAGS["error"],
          )

      return redirect("index-page")
  
    IncrementLogin(request)

    return render(
        request,
        "authentication.html",
        {
            "profile": get_user_profile(request.user),
            "section": "home-authentication",
        },
    ) 

@user_passes_test(lambda u: not u.is_anonymous) 
def ProfileView(request):
  profile = Profile.objects.get(account = request.user)
  ideas = Idea.objects.filter(Q(idea_author = profile)).order_by('-idea_publish_date')
  return render(request, 'profile.html', {'profile': profile, 'user_ideas': ideas, 'user_comments': Comment.objects.filter(Q(comment_author = profile)).order_by('-comment_publish_date')})




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
            'section': 'ideas'
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

def UpdatesView(request):
    return render(request, 'updates.html', {'updates': Update.objects.all()[::-1]})

def StatusView(request):
    return redirect('https://stats.uptimerobot.com/NyKm0fZmO3')

def IpToLocView(request):
    return redirect('https://ipapi.co/json')

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
                user_register_dates[str(user.date_joined.day) +  '-' + str(user.date_joined.month)] += 1
            except KeyError:
                user_register_dates[str(user.date_joined.day) + '-' + str(user.date_joined.month)] = 1

        idea_publish_dates = {}

        for idea in ideas:
            try:
                idea_publish_dates[str(idea.idea_publish_date.day) +  '-' + str(idea.idea_publish_date.month)] += 1
            except KeyError:
                idea_publish_dates[str(idea.idea_publish_date.day) + '-' + str(idea.idea_publish_date.month)] = 1

        comment_publish_dates = {}

        for comment in comments:
            try:
                comment_publish_dates[str(comment.comment_publish_date.day) +  '-' + str(comment.comment_publish_date.month)] += 1
            except KeyError:
                comment_publish_dates[str(comment.comment_publish_date.day) +  '-' + str(comment.comment_publish_date.month)] = 1

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
        idea_object = Idea.objects.get(Q(id=idea_id) & (Q(idea_archived=False) | Q(idea_author=Profile.objects.get(Q(account = request.user)))))
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
                "profile": get_user_profile(request.user),
                "user_icon": get_user_badge(idea_object.idea_author.account)
            },
        )


def LeaderboardView(request):
    ideas = Idea.objects.filter(Q(idea_archived = False))

    comments = Comment.objects.filter(Q(comment_archived = False))
    all_profiles =  Profile.objects.all().filter(Q(account__is_superuser = False) & Q(account__is_staff = False)).order_by('-total_point')
    profiles = all_profiles[:10]


    IncrementLogin(request)

    return render(
        request,
        "leaderboard.html",
        {
            "profile": get_user_profile(request.user),
            "profiles": profiles,
            "topic": Topic.objects.first(),
            "comments_count": len(comments),
            "ideas_count": len(ideas),
            'section': 'leaderboard'
        },
    ) 

def EditIdeaView(request, idea_id: int):
    return redirect(request.META.get("HTTP_REFERER"))




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
            return redirect(request.META.get("HTTP_REFERER"))

        else:
          
            username, password, email = request.POST["username"], request.POST["password"], request.POST["email"]

            try:
                found_user = User.objects.filter(Q(username=username) | Q(email=email))
                found_profile = Profile.objects.filter(Q(ip_addresses__has_key = get_client_ip(request)))
            except User.DoesNotExist:
                pass 
            else:
                if found_user or False:
                    messages.error(
                        request,
                        "Bu bilgilere ait bir hesap zaten var!",
                        extra_tags=NOTIFICATION_TAGS["error"],
                    )
                    return redirect(request.META['HTTP_REFERER'])
            kvkk_check = True

            try:
                request.POST["emailperm"]
            except KeyError:
                email_perm = False
            else:
                email_perm = True

            try:
                validate_email(email)

                if email.endswith('.com') or email.endsiwth('.net'):
                    pass 
                else:
                    messages.error(request, 'Bu e-posta adresi ile kayıt olamazsınız.', extra_tags=NOTIFICATION_TAGS["error"],)
                    return redirect(request.META['HTTP_REFERER']) 
            except ValidationError:
                messages.error(request, 'Bu e-posta adresi ile kayıt olamazsınız.', extra_tags=NOTIFICATION_TAGS["error"],)
                return redirect(request.META['HTTP_REFERER'])
            

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
                    web_theme="Thinker Tema",
                    kvkk_agreed=kvkk_check,
                    email_permission=email_perm,
                    total_logged_time=datetime.timedelta(seconds=1),
                    last_logged_in=datetime.datetime.now(),
                    profile_rank="rookie",
                ).save()
                
                ctx = {
                'subtitle': 'Günün konusu hazır:',
                'title': f'Hoş geldin {username}',
                'paragraph_1': 'Aramıza hoş geldin. Bu platformda fikirlerini paylaşırken eğlenmeyi unutma! Birazdan gelen kutuna gelecek olan linke tıklayarak e-posta adresini doğrulayabilirsin.',
                'paragraph_2': 'Eğer bu işlemi sen gerçekleştirmediysen güvenli bir şekilde bu iletiyi silebilirsin.'
                }
                html_message = render_to_string('dynamic_mail.html', ctx)
                plain_message = strip_tags(html_message)
                send_mail('Hesabın oluşturuldu! - justhink.net', plain_message, 'iletisim@justhink.net', [email], html_message=html_message,  fail_silently=True)

            else:
                messages.error(
                    request,
                    "Hesabınız bizden kaynaklı bir sorundan ötürü oluşturulamadı. [#0001]",
                    extra_tags=NOTIFICATION_TAGS["error"],
                )

    return redirect("index-page")

    return redirect('authentication')

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
            idea_topic=Topic.objects.first().topic_name
        ).save()

        messages.success(
            request,
            "Başarıyla fikrinizi paylaştınız!",
            extra_tags=NOTIFICATION_TAGS["success"],
        )


        return redirect(request.META['HTTP_REFERER'])


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

            idea_object.idea_author.user_notifications[create_hash(16)] = {
              'notification_content': f'{request.user.username} fikrinizi beğendi',
              'notification_details': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
              'notification_image': 'robot',
              'notification_link': f'/inspect-idea/{post_id}',
              'viewed': False
            }
            
            idea_object.idea_author.save()
            
            GivePoint(idea_object.idea_author.account, POINT_POLICY["like_idea"])

        else:
            idea_object.idea_like_count -= 1
            del idea_object.idea_likes[request.user.username]
            idea_object.save()

            TakePoint(idea_object.idea_author.account, POINT_POLICY["like_idea"])


        return redirect(request.META["HTTP_REFERER"])



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


            comment_content = request.POST['comment_content']
            
            Comment.objects.create(comment_idea = idea_object, comment_author = Profile.objects.get(account=request.user), comment_content = comment_content, comment_topic=Topic.objects.first().topic_name).save()
            idea_object.idea_comments += 1
            idea_object.save()
            
            idea_object.idea_author.user_notifications[create_hash(16)] = {
              'notification_content': f'{request.user.username} fikrinize yorum yaptı',
              'notification_details': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              'notification_image': 'robot',
              'notification_link': f'/inspect-idea/{idea_id}',
              'viewed': False
              }
            
            idea_object.idea_author.save()
            
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
                comment_object.comment_author.user_notifications[create_hash(16)] = {
                  'notification_content': f'{request.user.username} yorumunuzu beğendi',
                  'notification_details': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'notification_image': 'robot',
                  'notification_link': f'/inspect-idea/{idea_id}',
                  'viewed': False
                }
            
                comment_object.comment_author.save()
              
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
                comment_object.comment_author.user_notifications[create_hash(16)] = {
                  'notification_content': f'{request.user.username} yorumunuzu beğenmedi',
                  'notification_details': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'notification_image': 'robot',
                  'notification_link': f'/inspect-idea/{idea_id}',
                  'viewed': False
                }
            
                comment_object.comment_author.save()
              
                comment_object.comment_dislike_count += 1
                comment_object.comment_dislikes[request.user.username] = True
                comment_object.save()
        else:
            comment_object.comment_dislike_count -= 1
            del comment_object.comment_dislikes[request.user.username]
            comment_object.save()

        return redirect("inspect-idea-page", idea_id)

def ViewNotificationView(request, notification_key):
  profile = get_user_profile(request.user)
  try:
    profile.user_notifications[notification_key]
  except KeyError:
    return redirect('index-page')
  else:
    profile.user_notifications[notification_key]['viewed'] = True 
    profile.save()

    return redirect(profile.user_notifications[notification_key]["notification_link"])
    
def handle_404(request, exception):
    return render(request, "404.html")

@user_passes_test(lambda u: u.is_anonymous)
def ForgotPasswordView(request):
  IncrementLogin(request)
  if request.POST:
    return 
  else:
    return render(
        request,
        "forgot_password.html",
        {
            "section": "forgot-password",
        },
    ) 

@user_passes_test(lambda u: not u.is_anonymous)
def RateTopicView(request):
    if request.GET:
        topic = Topic.objects.first()
        try:
            topic_voted = topic.topic_rate['voted']
        except KeyError:
            topic.topic_rate = {'rate': 0, 'voted': {}}
            topic_voted = topic.topic_rate['voted']
        except TypeError:
            topic.topic_rate = {'rate': 0, 'voted': {}}
            topic_voted = topic.topic_rate['voted']
        
        if request.user.username not in topic_voted:
            user_rate = request.GET['rate']
            topic.topic_rate['voted'][request.user.username] = int(user_rate) 
            topic.topic_rate['rate'] = sum([int(topic_rate) for topic_rate in topic.topic_rate['voted'].values()]) / len(topic.topic_rate['voted'])
            topic.save()
            return redirect('index-page')
        else:
            return redirect('index-page')