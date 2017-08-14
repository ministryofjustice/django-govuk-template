from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('demo_service.urls', namespace='demo')),
    url(r'^admin/', admin.site.urls),
]
