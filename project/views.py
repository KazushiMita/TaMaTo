from django.shortcuts import render
from django.views.generic import TemplateView

class IndexFormView(TemplateView):
    template_name = 'home.html'
    def post(self, request, *args, **kwargs):
        ps = request.POST['input_text']
        if ps == "1922nen7gatsu15nichi":
            return render(request, 'user_auth/login.html')
        else:
            return render(request, self.template_name)
