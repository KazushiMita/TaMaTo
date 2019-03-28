from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone
now = timezone.now

import urllib,time

import tweepy
from user_auth.lib.twitter import getTwitterAppApi, getTwitterUserApi,\
    getLoginedUser, lookupUsers
tw_app_api = getTwitterAppApi()

from user_auth.models import TWUser
from social_django.models import UserSocialAuth

def getOriginalTweets(screen_name, max_length=20):
    ret = []
    for tweet in tweepy.Cursor(
            tw_app_api.user_timeline, screen_name=screen_name).items():
        if 'retweeted_status' in dir(tweet):
            author = tweet.retweeted_status.author
        else:
            author = tweet.author
        if author.screen_name == screen_name:
            ret.append(tweet)
            print('tweet.text ==>',tweet.text)
        if len(ret) >= max_length:
            return ret
    return ret


def getRetweetors(tweets):
    if isinstance(tweets,list) is not True:
        tweets = [ tweets ]
    ret = []
    for tweet in tweets :
        for retweet_status in tweet.retweets() :
            ret.append(retweet_status.author)
    return ret


def getFavoriters(screen_name):
    ret = []
    for favorite in tweepy.Cursor(
            tw_app_api.favorites, screen_name=screen_name).items():
        if favorite.user.id not in [ r.id for r in ret] :
            ret.append( favorite.user )
    return ret


def getReplies(tweet):
    user = tweet.user.screen_name
    tweet_id = tweet.id
    max_id = None
    while True:
        q = urllib.parse.urlencode({"q": "to:%s" % user})
        try:
            replies = tw_app_api.search(
                q=q, since_id=tweet_id, max_id=max_id, count=100)
            print('<<search>>')
        except tweepy.error.TweepError as e:
            print('<<sleep60>>',e)
            time.sleep(60)
            continue
        print('len(replies) ==>',len(replies))
        for reply in replies:
            if reply.in_reply_to_status_id == tweet_id:
                yield reply
                for reply_to_reply in get_replies(reply):
                    yield reply_to_reply
            max_id = reply.id
        if len(replies) != 100:
            break


def getReplyers(tweets):
    replyers = []
    for tweet in tweets :
        replies = getReplies(tweet)
        for reply in replies :
            if reply.user.id not in [ replyer.user.id for replyer in replyers ]:
                replyers.append(reply.user)
    return replyers


def getActedUsers(screen_name, max_length=20):
    # get original tweets
    tweets = getOriginalTweets(screen_name, max_length)
    # get users who retweet favorite, and replay to tweet
    retweetors = getRetweetors(tweets)
    print('len(retweetors) ==>',len(retweetors))
    favoriters = getFavoriters(screen_name)
    print('len(favoriters) ==>',len(favoriters))
    replyers = getReplyers(tweets)
    print('len(replyers) ==>',len(replyers))
    # exclude double count
    actedUsers = retweetors[:]
    for favoriter in favoriters:
        if favoriter.id not in [ actedUser.id for actedUser in actedUsers ] :
            actedUsers.append(favoriter)
    for replyer in replyers :
        if replyer.id not in [ actedUser.id for actedUser in actedUsers ] :
            actedUsers.append(replyer)
    print('len(actedUsers) ==>',len(actedUsers))
    return actedUsers


class ActedUserList(TemplateView,LoginRequiredMixin):
    template_name = "user_auth/actedusers.html"

    def post(self, request, *args, **kwargs):
        if request.POST['mode'] == "Get users who acted on me":
            print('here we are!!')
            user = getLoginedUser(request)
            screen_name = user.access_token['screen_name']
            max_length = 20
            actedUsers = getActedUsers(screen_name, max_length)
            # renew actedUsers with tw_user_api
            tw_user_api = getTwitterUserApi(
                user.extra_data['access_token']['oauth_token'],
                user.extra_data['access_token']['oauth_token_secret'])
            actedUsers = lookupUsers(tw_user_api,[ user.id for user in actedUsers ])
            # turn TWUsers `acted` off
            old_acted_users = TWUser.objects.filter(
                logined_user_id=request.user.id,acted=True)
            for old_acted_user in old_acted_users:
                old_acted_user.acted = False
                old_acted_user.save()
            # add actedUsers to TWUser
            for au in actedUsers :
                defaults={
                    'name':au.name,
                    'screen_name':au.screen_name,
                    'statuses_count':au.statuses_count,
                    'followers_count':au.followers_count,
                    'friends_count':au.friends_count,
                    'favourites_count':au.favourites_count,
                    'listed_count':au.listed_count,
                    'profile_image_url':au.profile_image_url,
                    'created_at':au.created_at.astimezone(),
                    'description':au.description,
                    'location':au.location,
                    'protected':au.protected,
                    'following':au.following,
                    'modified_at':now(),
                    'acted':True,
                }
                obj,updated = TWUser.objects.update_or_create(
                    logined_user_id=UserSocialAuth.objects.get(
                        id=request.user.id),
                    user_id=au.id,
                    defaults=defaults,
                )
                obj.save()
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acted_users'] = TWUser.objects.filter(
            logined_user_id=self.request.user.id, acted=True, neglect=False).order_by('-followers_count')
        return context



