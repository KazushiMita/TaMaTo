from django.urls import path,include
from . import views
#app_name='user_auth'

urlpatterns=[
    #path('top/',views.top_page, name="top"),
    path('top/', views.TopView.as_view(), name="top"),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('tw_user/construct/', views.TWUserConstructView.as_view(), name='tuc'),
    path('tw_user/<slug:mode>',views.TWUserListView.as_view(),name='tw_user'),
    #
    path('statistics/', views.StatsView.as_view(), name='stats'),
    #
    path('retweet_queues/', views.RetweetQueueListView.as_view(), name='rqs'),
    path('retweet_queue_create/',
         views.RetweetQueueCreateView.as_view(),
         name='rq_create'),
    path('retweet_queue_detail/<int:pk>/',
         views.RetweetQueueDetailView.as_view(),
         name='rq_detail'),
    path('retweet_queue_update/<int:pk>/',
         views.RetweetQueueUpdateView.as_view(),
         name='rq_update'),
    path('retweet_queue_delete/<int:pk>/',
         views.RetweetQueueDeleteView.as_view(),
         name='rq_delete'),
    path('do_reretweet_and_refavorite/',
         views.doReretweetAndRefavorite,
         name="rq_do"),
]
