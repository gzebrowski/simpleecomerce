from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from .models import StaticPage


class HomePage(TemplateView):
    template_name = 'index.html'


class StaticPageView(TemplateView):
    template_name = 'static_page.html'

    def get(self, request, *args, **kwargs):
        self.obj = get_object_or_404(StaticPage, url=request.path)
        return super(StaticPageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.obj
        return super(StaticPageView, self).get_context_data(**kwargs)


class CakeCompose(TemplateView):
    template_name = 'cake_compose.html'
