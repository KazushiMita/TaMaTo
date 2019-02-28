from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

import tweepy
from user_auth.lib.twitter import getTwitterAppApi, getLoginedUser
tw_app_api = getTwitterAppApi()


def getOriginalTweet(screen_name, max_length=20):
    ret = []
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name).items():
        if tweet.author.screen_name == screen_name:
            ret.append(tweet)
        if len(ret) >= max_length:
            return ret
    return ret


def genRetweetor_ids(tweet):
     for retweet_status in tweet.retweets() :
         yield retweet_status.author.id


def getActedUsers(screen_name, max_length=20):
    pass
    
class ActedUserList(TemplateView,LoginRequiredMixin):
    template_name = "user_auth/actedusers.html"

    def post(self, request, *args, **kwargs):
        if request.POST['mode'] == "Get users who acted on me":
            print('here we are!!')
            user = getLoginedUser(request)
            screen_name = user.access_token.screen_name
            max_length = 20
            tweets = getOriginalTweet(screen_name,max_length)
        context = {}
        return render(request, self.template_name, context=context)
