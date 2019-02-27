import tweepy
from project.settings import TW_API_CONSUMER_KEY,\
    TW_API_CONSUMER_SECRET, TW_API_ACCESS_TOKEN, TW_API_ACCESS_TOKEN_SECRET
from social_django.models import UserSocialAuth


def getTwitterAppApi():
    """ tw_app_api = getTwitterAppApi() """
    auth = tweepy.OAuthHandler(TW_API_CONSUMER_KEY, TW_API_CONSUMER_SECRET)
    auth.set_access_token(TW_API_ACCESS_TOKEN, TW_API_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)


def getTwitterUserApi(access_token, access_token_secret):
    """
    tw_user_api = getTwitterUserApi(
    access_token='xxx', access_token_secret='xxx'
    )
    """
    auth = tweepy.OAuthHandler(TW_API_CONSUMER_KEY, TW_API_CONSUMER_SECRET)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True)


def getLoginedUser(request='',user_id=''):
    print("dir(request.user) ==>",dir(request.user))
    print("request.user.id ==>",request.user.id)
    print("request.user.pk ==>",request.user.pk)
    print("request.user.pk ==>",request.user.username)
    print("request.user.social_auth ==>",request.user.social_auth)
    if request == '' :
        return UserSocialAuth.objects.get(user_id=user_id)
    elif user_id == '':
        return UserSocialAuth.objects.get(user_id=request.user.id)
    else:
        raise ValueError()

def getLoginedUserAndAnthorizedApi(request='', user_id=''):
    # user
    user = getLoginedUser(request,user_id)
    # twitter api
    api = getTwitterUserApi(
        access_token=user.access_token['oauth_token'],
        access_token_secret=user.access_token['oauth_token_secret'],
    )
    return user, api


def lookupUsers(api, user_ids, batch_size=100):
    ids_size = len(user_ids)
    for i in range(0, ids_size, batch_size):
        users = api.lookup_users(user_ids=user_ids[i:min(i+100,ids_size)])
        for user in users :
            yield user

