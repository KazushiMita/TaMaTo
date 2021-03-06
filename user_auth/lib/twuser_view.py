from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, ListView
from django.http import JsonResponse

from social_django.models import UserSocialAuth

from user_auth.models import TWUser, Recode

from user_auth.lib.twitter import getTwitterAppApi, getTwitterUserApi
from user_auth.lib.twitter import getLoginedUser, getLoginedUserAndAnthorizedApi
tw_app_api = getTwitterAppApi()
from user_auth.lib.twitter import lookupUsers, getFollowersIds, isFollowed

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
        #return render(request, self.template_name, context=context)
        return JsonResponse({})

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

        print('total',len(followers_ids))
        followers_ids_temp = []
        for follower_id in followers_ids:
            try:
                obj = TWUser.objects.get(
                    logined_user_id=request.user.id,user_id=follower_id)
                if (now() - obj.modified_at).total_seconds() < 60*60:
                    followers_ids.remove(follower_id)
                    followers_ids_temp.append(follower_id)
            except TWUser.DoesNotExist:
                pass
        print('update',len(followers_ids),'not update',len(followers_ids_temp))

        for follower in lookupUsers(tw_app_api, followers_ids):
            #print('user :', follower.name)
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
            obj, created = TWUser.objects.update_or_create(
                logined_user_id=UserSocialAuth.objects.get(id=self.request.user.id),
                user_id=follower.id,
                defaults=defaults,
            )
            obj.save()
            if created == True:
                stat['created_count'] += 1
            else:
                stat['updated_count'] += 1

        followers_ids = followers_ids + followers_ids_temp
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

        print('total',len(friends_ids))
        friends_ids_temp = []
        for friend_id in friends_ids:
            try:
                obj = TWUser.objects.get(
                    logined_user_id=request.user.id,user_id=friend_id,followed=False)
                if (now() - obj.modified_at).total_seconds() < 60*60:
                    friends_ids.remove(friend_id)
                    friends_ids_temp.append(friend_id)
                    obj.following = True
                    obj.save()
            except TWUser.DoesNotExist:
                pass
        print('update',len(friends_ids),'not update',len(friends_ids_temp))

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
            #print('user :', friend.name)
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
            obj, created = TWUser.objects.update_or_create(
                logined_user_id=UserSocialAuth.objects.get(id=self.request.user.id),
                user_id=friend_id, defaults=defaults, )
            obj.save()
            if created == True:
                stat['created_count'] += 1
            else:
                stat['updated_count'] += 1
        friends_ids = friends_ids + friends_ids_temp
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
                logined_user_id=self.request.user.id,
                followed=True, neglect=False,
            ).order_by('-followers_count')
        elif self.mode == 'friends':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id,
                following=True, neglect=False,
            ).order_by('-followers_count')
        elif self.mode == 'fol_not_in_fri':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id,
                followed=True, following=False, neglect=False,
            ).order_by('-followers_count')
        elif self.mode == 'fri_not_in_fol':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id,
                followed=False, following=True, neglect=False,
            ).order_by('-followers_count')
        elif self.mode == 'neglected':
            self.queryset = TWUser.objects.filter(
                logined_user_id=self.request.user.id,
                neglect=True,
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


def on_click_follow(request):
    target_user_id = request.POST.get('user_id')
    logined_user_id = request.user.id
    _, tw_user_api = getLoginedUserAndAnthorizedApi(request)
    target = tw_user_api.get_user(target_user_id)
    target.follow()
    target_obj = TWUser.objects.get(
        logined_user_id=logined_user_id, user_id=target_user_id)
    target_obj.following = True
    target_obj.save()
    ret = { 'user_id':target_user_id,
            'logined_user_id':logined_user_id,
    }
    return JsonResponse(ret)

def on_click_unfollow(request):
    target_user_id = request.POST.get('user_id')
    logined_user_id = request.user.id
    _, tw_user_api = getLoginedUserAndAnthorizedApi(request)
    target = tw_user_api.destroy_friendship(target_user_id)
    target_obj = TWUser.objects.get(
        logined_user_id=logined_user_id, user_id=target_user_id)
    target_obj.following = False
    target_obj.save()
    ret = { 'user_id':target_user_id,
            'logined_user_id':logined_user_id,
    }
    return JsonResponse(ret)

def on_click_neglect(request):
    target_user_id = request.POST.get('user_id')
    logined_user_id = request.user.id
    target_obj = TWUser.objects.get(
        logined_user_id=logined_user_id, user_id=target_user_id)
    target_obj.neglect = True
    target_obj.save()
    ret = { 'user_id':target_user_id,
            'logined_user_id':logined_user_id,
    }
    return JsonResponse(ret)

def on_click_respect(request):
    target_user_id = request.POST.get('user_id')
    logined_user_id = request.user.id
    target_obj = TWUser.objects.get(
        logined_user_id=logined_user_id, user_id=target_user_id)
    target_obj.neglect = False
    target_obj.save()
    ret = { 'user_id':target_user_id,
            'logined_user_id':logined_user_id,
    }
    return JsonResponse(ret)

def on_click_update(request):
    target_user_id = request.POST.get('user_id')
    logined_user_id = request.user.id
    _, tw_user_api = getLoginedUserAndAnthorizedApi(request)
    i = tw_app_api.get_user(_.uid)
    u = tw_user_api.get_user(target_user_id)

    t = TWUser.objects.get(
        logined_user_id=logined_user_id, user_id=target_user_id)

    t.name = u.name
    t.screen_name = u.screen_name
    t.statuses_count = u.statuses_count
    t.followers_count = t.followers_count
    t.friends_count = u.friends_count
    t.favourites_count = u.favourites_count
    t.listed_count = u.listed_count
    t.profile_image_url = u.profile_image_url
    t.description = u.description
    t.location = u.location
    t.protected = u.protected
    t.modified_at = now()
    # friendship
    t.following = u.following
    print('>',t.screen_name, t.following)
    t.followed = isFollowed(tw_app_api, i, u)
    print('<',t.screen_name, t.followed)
    t.save()
    ret = {
        'user_id':target_user_id,
        'logined_user_id':logined_user_id,
        'name' : u.name,
        'screen_name' : u.screen_name,
        'statuses_count' : u.statuses_count,
        'followers_count' : t.followers_count,
        'friends_count' : u.friends_count,
        'favourites_count' : u.favourites_count,
        'listed_count' : u.listed_count,
        'profile_image_url' : u.profile_image_url,
        'description' : u.description,
    }
    return JsonResponse(ret)
    
