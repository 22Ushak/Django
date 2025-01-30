# from django.urls import path
# from . import views

# urlpatterns = [
#     path('',views.index,name='index'),
#     path("details<int:id>/",views.details,name="details")
# ]


from django.urls import path
from . import views
from .views import like_dislike_comment

urlpatterns = [
    path('',views.index,name='index'),
    path("details<int:id>/",views.details,name="details"),
     path('comment/<int:comment_id>/<str:action>/', like_dislike_comment, name='like_dislike_comment'),
]