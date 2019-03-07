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
    path('tw_user/follow/',views.on_click_follow,name='tw_follow'),
    path('tw_user/unfollow/',views.on_click_unfollow,name='tw_unfollow'),
    path('tw_user/neglect/',views.on_click_neglect,name='tw_neglect'),
    path('tw_user/respect/',views.on_click_respect,name='tw_respect'),
    path('tw_user/update/',views.on_click_update,name='tw_update'),
    #
    path('statistics/', views.StatsView.as_view(), name='stats'),
    #
    path('actedusers/', views.ActedUserList.as_view(), name='actedusers'),
    #
    path('retweet_queues/', views.RetweetQueueListView.as_view(), name='rqs'),
    path('retweet_queues/add/', views.on_click_addRetweetQueue, name='add_queue'),
    path('retweet_queues/trigger/', views.on_click_trigRunning, name='run_trigger'),
    path('retweet_queues/tl_see_more/', views.getTlSeeMore, name='tl_see_more'),
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
