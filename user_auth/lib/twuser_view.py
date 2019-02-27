from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, ListView

from social_django.models import UserSocialAuth

from user_auth.models import TWUser, Recode

from user_auth.lib.twitter import getTwitterAppApi, getTwitterUserApi
from user_auth.lib.twitter import getLoginedUser, getLoginedUserAndAnthorizedApi
tw_app_api = getTwitterAppApi()
from user_auth.lib.twitter import lookupUsers

import tweepy
from django.utils import timezone
now = timezone.now


class TWUserConstructView(TemplateView,LoginRequiredMixin):
    template_name = 'user_auth/tw_user_construct.html'
    params = {}
    
    def post(self, request):
        start = now()
        followers_ids, stat1 = self.updateFollowers(request)
        friends_ids, stat2 = self.updateFriends(request, followers_ids)
        self.updateUnfollowUnfriend(followers_ids, friends_ids)
        stat = {
            'updated_count' : stat1['updated_count'] + stat2['updated_count'],
            'created_count' : stat1['created_count'] + stat2['created_count'],
        }
        end = now()
        print('%i followers and %i friends ids have been got.'\
              % (len(followers_ids),len(friends_ids)))
        interval = (end-start).total_seconds()
        rec = Recode.objects.create(
            logined_user_id=UserSocialAuth.objects.get(id=self.request.user.id),
            modified_at=now(),
            p_time = interval,
            created_count=stat['created_count'],
            updated_count=stat['updated_count'],
        )
        rec.save()
        context = {}
        context['recodes'] = Recode.objects.filter(
            logined_user_id=self.request.user.id).order_by('-modified_at')[:5]
        return render(request, self.template_name, context=context)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recodes'] = Recode.objects.filter(
            logined_user_id=self.request.user.id).order_by('-modified_at')[:5]
        return context


    def updateFollowers(self, request):
        followers_ids = []
        stat = { 'updated_count':0, 'created_count':0, }

        user = tw_app_api.get_user(getLoginedUser(request))
        followers_ids = [
            follower_id for follower_id in tweepy.Cursor(
                tw_app_api.followers_ids,
                screen_name=user.screen_name
            ).items()
        ]

        for follower in lookupUsers(tw_app_api, followers_ids):
            print('user :', follower.name)
            defaults={
                'name':follower.name,
                'screen_name':follower.screen_name,
                'statuses_count':follower.statuses_count,
                'followers_count':follower.followers_count,
                'friends_count':follower.friends_count,
                'favourites_count':follower.favourites_count,
                'listed_count':follower.listed_count,
                'profile_image_url':follower.profile_image_url,
                'created_at':follower.created_at.astimezone(),
                'description':follower.description,
                'location':follower.location,
                'protected':follower.protected,
                'followed':True,
                'modified_at':now(),
            }
            obj, updated = TWUser.objects.update_or_create(
                logined_user_id=UserSocialAuth.objects.get(id=self.request.user.id),
                user_id=follower.id,
                defaults=defaults,
            )
            obj.save()
            if updated == True:
                stat['updated_count'] += 1
            else:
                stat['created_count'] += 1
            print('updated :', updated)
            
        return followers_ids, stat


    def updateFriends(self, request, followers_ids ):
        friends_ids = []
        stat = { 'updated_count':0, 'created_count':0, }

        user = tw_app_api.get_user(getLoginedUser(request))
        friends_ids = [
            friend_id for friend_id in tweepy.Cursor(
                tw_app_api.friends_ids,
                screen_name=user.screen_name,
            ).items()
        ]

        # exclude followers(who have been updated above.)
        friends_notin_followers_ids = []
        for friend_id in friends_ids :
            if friend_id in followers_ids:
                obj = TWUser.objects.get(
                    logined_user_id=self.request.user.id,
                    user_id=friend_id)
                obj.following = True
                obj.save()
                updated = True
            else :
                friends_notin_followers_ids.append(friend_id)

        # get friend info
        for friend in lookupUsers(tw_app_api, friends_notin_followers_ids):
            print('user :', friend.name)
            defaults={
                'name':friend.name,
                'screen_name':friend.screen_name,
                'statuses_count':friend.statuses_count,
                'followers_count':friend.followers_count,
                'friends_count':friend.friends_count,
                'favourites_count':friend.favourites_count,
                'listed_count':friend.listed_count,
                'profile_image_url':friend.profile_image_url,
                'created_at':friend.created_at.astimezone(),
                'description':friend.description,
                'location':friend.location,
                'protected':friend.protected,
                'following':True,
                'modified_at':now(),
            }
            obj, updated = TWUser.objects.update_or_create(
                logined_user_id=UserSocialAuth.objects.get(id=self.request.user.id),
                user_id=friend_id, defaults=defaults, )
            obj.save()
            if updated == True:
                stat['updated_count'] += 1
            else:
                stat['created_count'] += 1
            print('updated :', updated)
        return friends_ids, stat


    def updateUnfollowUnfriend(self, followers_ids, friends_ids):
        for obj in TWUser.objects.filter(
                logined_user_id=self.request.user.id,
                followed=True):
            if obj.user_id not in followers_ids :
                obj.followed = False
                obj.save()
        for obj in TWUser.objects.filter(
                logined_user_id=self.request.user.id,
                following=True):
            if obj.user_id not in friends_ids :
                obj.following = False
                obj.save()


class TWUserDetailView(DetailView,LoginRequiredMixin):
    template_name = "user_auth/tw_user_detail.html"
    Model = TWUser


class TWUserListView(ListView, LoginRequiredMixin):
    model = TWUser
    paginate_by = 30

    def get(self, request, *args, **kwargs):
        self.mode = kwargs['mode']
        if self.mode == 'followers':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id, followed=True
            ).order_by('-followers_count')
        elif self.mode == 'friends':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id, following=True
            ).order_by('-followers_count')
        elif self.mode == 'fol_not_in_fri':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id, followed=True, following=False
            ).order_by('-followers_count')
        elif self.mode == 'fri_not_in_fol':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id, followed=False, following=True
            ).order_by('-followers_count')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = self.mode
        # counter numbering for each page
        if 'page' in self.request.GET :
            num = int(self.request.GET.get('page'))-1
        else:
            num = 0
        context['count_pre_page'] = num * self.paginate_by
        return context
