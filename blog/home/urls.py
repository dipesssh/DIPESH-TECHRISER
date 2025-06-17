from django.urls import path
from home.views import BlogView, PublicBlogView, CommentView

urlpatterns = [
    path('blog/', BlogView.as_view()),
    path('public/', PublicBlogView.as_view()),
    
    path('blog/<uuid:blog_uid>/comments/', CommentView.as_view(), name='blog-comments'),
    
]
