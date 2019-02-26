from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView,\
    DetailView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse

from social_django.models import UserSocialAuth
from user_auth.models import RetweetQueue
from user_auth.forms import RetweetQueueForm, RetweetQueueUpdateForm

from user_auth.lib.twitter import getLoginedUser, getLoginedUserAndAnthorizedApi

import time


class RetweetQueueListView(ListView, LoginRequiredMixin):
    """default template_name --> retweetqueue_list.html"""
    model = RetweetQueue

    def get_queryset(self):
        return self.model.objects.filter(logined_user_id=self.request.user.id)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = getLoginedUser(self.request)
        context['user_id'] = user.user_id
        context['screen_name'] = user.access_token['screen_name']
        return context


class RetweetQueueCreateView(CreateView, LoginRequiredMixin):
    model = RetweetQueue
    form_class = RetweetQueueForm
    success_url = reverse_lazy('rqs')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        user, tw_user_api = getLoginedUserAndAnthorizedApi(self.request)
        status = tw_user_api.get_status(self.object.status_id)
        self.object.logined_user_id = UserSocialAuth.objects.get(
            id=self.request.user.id)
        self.object.user_name = status.user.name
        self.object.created_at = status.created_at.astimezone()
        self.object.retweet_count = status.retweet_count
        self.object.favorite_count = status.favorite_count
        self.object.retweeted = status.retweeted
        self.object.text = status.text
        #if 'urls' in status.entities.keys():
        #    if status.entities['urls'] 
        #    self.object.media_url_https = status.entities['media_url_https']
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


def test_ajax_response(request):
    input_text = request.POST.getlist("name_input_text")
    hoge = "Ajax Response: " + input_text[0]
    return HttpResponse(hoge)


def doReretweetAndRefavorite(request):
    if request.POST['rq_do_mode'] == 'all':
        user_id = request.POST['user_id']
        user, tw_user_api = getLoginedUserAndAnthorizedApi(
            request='', user_id=user_id)
        for target in RetweetQueue.objects.filter(
                logined_user_id=user.id, running=True):
            time.sleep(0.5)
            status = tw_user_api.get_status(target.status_id, include_my_retweet=1)
            if status.retweeted == True:
                tw_user_api.destroy_status(status.current_user_retweet['id'])
            tw_user_api.retweet(target.status_id)
            if status.favorited == True:
                tw_user_api.destroy_favorite(status.id)
            status.favorite()
            
    return HttpResponse('Done.')
