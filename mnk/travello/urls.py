from django.urls import path,include
from . import views
from .views import like_dislike_comment

urlpatterns = [
    path('',views.index,name='index'),
    path("details<int:id>/",views.details,name="details"),
    path('comment/<int:comment_id>/<str:action>/', like_dislike_comment, name='like_dislike_comment'),
    path('register_first/', views.register_first, name='register_first'),
    path('upload/', views.upload_csv, name='upload_csv'),
    
 
    
]





    
