from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from social_django.models import UserSocialAuth
from user_auth.models import UserStat, TWUser

from user_auth.lib.twitter import getTwitterAppApi, getTwitterUserApi,\
    getLoginedUser, getLoginedUserAndAnthorizedApi, lookupUsers
tw_app_api = getTwitterAppApi()


class StatsView(TemplateView, LoginRequiredMixin):
    template_name = "user_auth/stats.html"
    
    def post(self, request, *args, **kwargs):
        print("here we are!!")
        tw_user = tw_app_api.get_user(
            getLoginedUser(self.request).access_token['screen_name'])
        obj, updated = UserStat.objects.update_or_create(
            logined_user_id=UserSocialAuth.objects.get(id=request.user.id),
            term='followers_count', defaults={'number':tw_user.followers_count})
        obj, updated = UserStat.objects.update_or_create(
            logined_user_id=UserSocialAuth.objects.get(id=request.user.id),
            term='friends_count', defaults={'number':tw_user.friends_count})
        obj, updated = UserStat.objects.update_or_create(    
            logined_user_id=UserSocialAuth.objects.get(id=request.user.id),
            term='secound_followers_count',
            defaults={'number':sum([
                follower.followers_count
                for follower in TWUser.objects.filter(
                        logined_user_id=request.user.id,
                        followed=True)])})
        obj.save()
        
        context = self.get_context_data(**kwargs)
        context['status'] = 1
        return render(request, self.template_name, context=context)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = tw_app_api.get_user(
            getLoginedUser(self.request).access_token['screen_name'])
        context['screen_name'] = user.screen_name
        context['stats'] = UserStat.objects.filter(logined_user_id=self.request.user.id)
        return context
