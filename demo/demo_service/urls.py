from django.conf.urls import url
from django.views.generic import TemplateView

app_name = 'demo'
urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='demo_service/demo.html'), name='demo'),
]
