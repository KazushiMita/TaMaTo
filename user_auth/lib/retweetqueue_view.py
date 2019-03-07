from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView,\
    DetailView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from social_django.models import UserSocialAuth
from user_auth.models import RetweetQueue
from user_auth.forms import RetweetQueueForm, RetweetQueueUpdateForm

from user_auth.lib.twitter import getLoginedUser, getLoginedUserAndAnthorizedApi

from django.utils import timezone
now = timezone.now
import time
import json

class RetweetQueueListView(ListView, LoginRequiredMixin):
    """default template_name --> retweetqueue_list.html"""
    model = RetweetQueue

    def get_queryset(self):
        return self.model.objects.filter(logined_user_id=self.request.user.id)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user, tw_user_api = getLoginedUserAndAnthorizedApi(self.request)
        context['user_id'] = user.user_id
        context['screen_name'] = user.access_token['screen_name']
        tl_count = 20
        context['timeline'] = tw_user_api.user_timeline(context['screen_name'])[:tl_count]
        context['tl_count'] = tl_count
        return context


def getTlSeeMore(request):
    pass
    return JsonResponse({})
    
def addRetweetQueue(logined_user_id, status_id):
    user, tw_user_api = getLoginedUserAndAnthorizedApi(user_id=logined_user_id)
    status = tw_user_api.get_status(status_id)
    user_obj = UserSocialAuth.objects.get(id=logined_user_id)
    obj, updated = RetweetQueue.objects.update_or_create(
        logined_user_id=user_obj,
        status_id=status_id)
    obj.logined_user_id = user_obj
    obj.user_name = status.user.name
    obj.created_at = status.created_at.astimezone()
    obj.retweet_count = status.retweet_count
    obj.favorite_count = status.favorite_count
    obj.retweeted = status.retweeted
    obj.text = status.text
    if 'media' in status.entities.keys():
        obj.media_url_https = json.dump( [
            m['media_url_https'] for m in status.entities['media']] )            
    obj.priority = RetweetQueue.objects.filter(
        logined_user_id=logined_user_id).count()+1
    obj.save()

def on_click_addRetweetQueue(request):
    status_id = request.POST.get('status_id')
    logined_user_id = request.user.id
    addRetweetQueue(logined_user_id, status_id)
    return render(request, 'user_auth/retweetqueue_list.html')

def on_click_trigRunning(request):
    pk = request.POST.get('pk')
    obj = RetweetQueue.objects.get(pk=pk)
    if   obj.running == True:
        obj.running = False
    elif obj.running == False:
        obj.running = True
    else:
        obj.running = True
    obj.save()
    return JsonResponse({})

import re
class RetweetQueueCreateView(CreateView, LoginRequiredMixin):
    model = RetweetQueue
    form_class = RetweetQueueForm
    success_url = reverse_lazy('rqs')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        user, tw_user_api = getLoginedUserAndAnthorizedApi(self.request)
        if "http" in self.object.status_id :
            r = re.search("(?<=/)[0-9]+",self.object.status_id)
            if r != None:
                self.object.status_id = r.group(0)
            else :
                raise ValueError
        status = tw_user_api.get_status(self.object.status_id)
        self.object.logined_user_id = UserSocialAuth.objects.get(
            id=self.request.user.id)
        self.object.user_name = status.user.name
        self.object.created_at = status.created_at.astimezone()
        self.object.retweet_count = status.retweet_count
        self.object.favorite_count = status.favorite_count
        self.object.retweeted = status.retweeted
        self.object.text = status.text
        if 'media' in status.entities.keys():
            self.object.media_url_https = json.dump( [
                m['media_url_https'] for m in status.entities['media']] )            
        self.object.priority = RetweetQueue.objects.filter(
            logined_user_id=self.request.user.id).count()+1
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class RetweetQueueDetailView(DetailView, LoginRequiredMixin):
    model = RetweetQueue


class RetweetQueueUpdateView(UpdateView, LoginRequiredMixin):
    model = RetweetQueue
    form_class = RetweetQueueUpdateForm
    success_url = reverse_lazy('rqs')


class RetweetQueueDeleteView(DeleteView, LoginRequiredMixin):
    model = RetweetQueue
    success_url = reverse_lazy('rqs')


def doReretweetAndRefavorite(request):
    if request.POST['rq_do_mode'] == 'all':
        user_id = request.POST['user_id']
        user, tw_user_api = getLoginedUserAndAnthorizedApi(
            request='', user_id=user_id)
        for target in RetweetQueue.objects.filter(
                logined_user_id=request.user.id, running=True).order_by('priority'):
            time.sleep(0.5)
            status = tw_user_api.get_status(target.status_id)
            if status.retweeted == True:
                tw_user_api.unretweet(status.id)
            tw_user_api.retweet(target.status_id)
            if status.favorited == True:
                tw_user_api.destroy_favorite(status.id)
            status.favorite()
            target.last_retweeted_at = now()
            target.save()
            
    return HttpResponse('Done.')
