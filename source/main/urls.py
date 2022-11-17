from django.urls import path, include
from .views import (
    IndexView,
    LoginView,
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
    StatusView
)
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSiteMap 
sitemaps = {
    'static': StaticViewSiteMap
}

urlpatterns = [
    path("", IndexView, name="index-page"),
    path("home", IndexView, name="home"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('robots.txt', include('robots.urls')),
    path('ideas-overview', IdeasOverview, name = 'ideas-page'),
    path('status', StatusView),
    path('favourite-ideas', FavouriteIdeasView, name = 'favourite-ideas-page'),
    path('trend-ideas', TrendIdeasView, name = 'trend-ideas-page'),
    path("login", LoginView, name="login-page"),
    path("register", RegisterView, name="register-page"),
    path("logout", LogoutView, name="logout-page"),
    path('edit-idea/<int:idea_id>', EditIdeaView, name = 'edit-idea-page'),
    path("publish-idea", PublishIdeaView, name="publish-idea-page"),
    path("like-idea/<int:post_id>", LikePostView, name="like-post-page"),
    path("inspect-idea/<int:idea_id>", InspectIdeaView, name="inspect-idea-page"),
    path("send-comment/<int:idea_id>", SendCommentView, name = 'send-comment-page'),
    path('like-comment/<int:idea_id>/<int:comment_id>', LikeCommentView, name = 'like-comment-page'),
    path('dislike-comment/<int:idea_id>/<int:comment_id>', DislikeCommentView, name = 'dislike-comment-page'),

]
