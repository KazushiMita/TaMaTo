from django.db import models
from django.utils import timezone
import datetime
from social_django.models import UserSocialAuth


class TWUser(models.Model):
    logined_user_id = models.ForeignKey(UserSocialAuth,on_delete=False,to_field='id')
    user_id = models.IntegerField()
    name = models.CharField(max_length=32)
    screen_name = models.CharField(max_length=32)
    statuses_count = models.IntegerField(default=0)
    followers_count = models.IntegerField()
    friends_count = models.IntegerField()
    favourites_count = models.IntegerField()
    listed_count = models.IntegerField()
    following = models.BooleanField(default=False)
    profile_image_url = models.URLField()
    created_at = models.DateTimeField()
    description = models.CharField(max_length=2**10)
    location = models.CharField(max_length=32,blank=True)
    protected = models.BooleanField(default=False)
    followed = models.BooleanField(default=False)
    modified_at = models.DateTimeField(default=timezone.now)
    acted = models.BooleanField(default=False)
    neglect = models.BooleanField(default=False)
    class Meta:
        unique_together = (('logined_user_id','user_id'),)


class Recode(models.Model):
    """recode of upadate proccess"""
    logined_user_id = models.ForeignKey(UserSocialAuth,on_delete=False,to_field='id')
    modified_at = models.DateTimeField(
        default=timezone.now,
    )
    p_time = models.IntegerField(default=0)
    created_count = models.IntegerField(default=0)
    updated_count = models.IntegerField(default=0)
    class Meta:
        unique_together = (('logined_user_id','modified_at'),)


class RetweetQueue(models.Model):
    logined_user_id = models.ForeignKey(UserSocialAuth,on_delete=False,to_field='id')
    status_id = models.CharField(max_length=64)
    user_name = models.CharField(max_length=16, blank=False)
    screen_name = models.CharField(max_length=32, default='')
    created_at = models.DateTimeField(null=True)
    last_retweeted_at = models.DateTimeField(null=True)
    retweet_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    retweeted = models.BooleanField(default=False)
    text = models.CharField(max_length=256, blank=True)
    media_url_https = models.TextField(blank=True)
    running = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    profile_image_url_https = models.URLField(blank=True)
    class Meta:
        unique_together = (('logined_user_id','status_id'),)


class Tweet(models.Model):
    status_id = models.IntegerField(unique=True)
    author = models.ForeignKey(TWUser,on_delete=False)
    text = models.TextField()
    created_at = models.DateTimeField()
    retweet_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    media_url_https = models.URLField(blank=True)


class UserStat(models.Model):
    logined_user_id = models.ForeignKey(UserSocialAuth,on_delete=False,to_field='id')
    term = models.CharField(max_length=64)
    number = models.IntegerField(default=0)
    class Meta:
        unique_together = (('logined_user_id','term'),)

