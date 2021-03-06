from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views  import LoginView, LogoutView
from django.views.generic import TemplateView

from user_auth.models import Recode
from user_auth.lib.twitter import getLoginedUser


class UserLoginView(LoginView):
    template_name = 'user_auth/login.html'


class UserLogoutView(LogoutView):
    template_name = 'user_auth/logout.html'


class TopView(TemplateView, LoginRequiredMixin):
    """request.user.id == UserSocialAuth.user_id"""
    template_name = 'user_auth/top.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = getLoginedUser(self.request)
        context['user'] = user
        context['recent_recode'] = Recode.objects.filter(
            logined_user_id=user.user_id).order_by('-modified_at').first()
        return context


from user_auth.lib.twuser_view import TWUserConstructView,\
    TWUserDetailView, TWUserListView
from user_auth.lib.twuser_view import on_click_follow, on_click_unfollow,\
    on_click_neglect, on_click_respect, on_click_update
from user_auth.lib.stats_view import StatsView
from user_auth.lib.retweetqueue_view import RetweetQueueListView,\
    RetweetQueueCreateView, RetweetQueueDeleteView, RetweetQueueDetailView,\
    RetweetQueueUpdateView, doReretweetAndRefavorite,\
    on_click_addRetweetQueue, on_click_trigRunning, getTlSeeMore
from user_auth.lib.actedusers_view import ActedUserList
