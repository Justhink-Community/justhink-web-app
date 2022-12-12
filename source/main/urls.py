from django.urls import path, include
from .views import (
    IndexView,
    RegisterView,
    LogoutView,
    PublishIdeaView,
    LikePostView,
    InspectIdeaView,
    SendCommentView,
    LikeCommentView,
    DislikeCommentView,
    IdeasOverview,
    FavouriteIdeasView,
    TrendIdeasView,
    IdeasOverview,
    EditIdeaView,
    LeaderboardView,
    StatusView,
    StatisticsView,
    ShopView,
    LandingView,
    AuthenticationView,
    ProfileView,
    AboutUsView,
    UpdatesView,
    IpToLocView,
    DashBoardView,
    ViewNotificationView,
    ForgotPasswordView,
    ChangeThemeView
)
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSiteMap 

sitemaps = {
    'static': StaticViewSiteMap
}

urlpatterns = [
    path("", IndexView, name="index-page"),
    path("home", LandingView, name="home"),
    path("dashboard", DashBoardView, name="dashboard-page"),
    path("about-us", AboutUsView, name = "about-us-page"),
    path("login", AuthenticationView, name = "authentication"),
    path("register", RegisterView, name="register-page"),
    path('forgot-password', ForgotPasswordView, name = 'forgot-password-page'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('robots.txt', include('robots.urls')),
    path('shuffle-ideas', IdeasOverview, name = 'random-ideas-page'),
    path('status', StatusView),
    path('stats', StatisticsView),
    path('shop', ShopView, name = 'shop-page'),
    path('change-theme', ChangeThemeView, name = 'change-theme-page'),
    path('updates', UpdatesView),
    path('ideas', FavouriteIdeasView, name = 'ideas-page'),
    path('leaderboard', LeaderboardView, name = 'leaderboard-page'),
    # path('banned', BannedView, name = 'banned-page'),
    path('iptoloc', IpToLocView, name = 'ip-to-loc-page'),
    # path('trend-ideas', TrendIdeasView, name = 'trend-ideas-page'),
    path("logout", LogoutView, name="logout-page"),
    path('edit-idea/<int:idea_id>', EditIdeaView, name = 'edit-idea-page'),
    path("publish-idea", PublishIdeaView, name="publish-idea-page"),
    path("like-idea/<int:post_id>", LikePostView, name="like-post-page"),
    path("inspect-idea/<int:idea_id>", InspectIdeaView, name="inspect-idea-page"),
    path("send-comment/<int:idea_id>", SendCommentView, name = 'send-comment-page'),
    path('like-comment/<int:idea_id>/<int:comment_id>', LikeCommentView, name = 'like-comment-page'),
    path('dislike-comment/<int:idea_id>/<int:comment_id>', DislikeCommentView, name = 'dislike-comment-page'),
    path('profile', ProfileView, name = 'profile-page'),
    path('view-notification/<str:notification_key>', ViewNotificationView, name = 'view-notification-page')

]
