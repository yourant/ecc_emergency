from django.views.generic.base import TemplateView


class Index(TemplateView):
    template_name = "emergency/m/index.html"
