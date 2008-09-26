from bonvortaro.vortaro import models
from bonvortaro.vortaro import views
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.list_detail import object_list, object_detail

admin.autodiscover()

roots = {
    "queryset": models.Root.objects.order_by("root"),
    "template_object_name": "root"
}
words = {
    "queryset": models.Word.objects.order_by("word"),
    "template_object_name": "word"
}

urlpatterns = patterns(
    '',
    
    url(r"^root/$", object_list, roots, name="roots"),
    url(r"^root/(?P<object_id>\d+)/$", object_detail, roots, name="root"),
    url(r"^word/$", object_list, words, name="words"),
    url(r"^word/(?P<object_id>\d+)/$", object_detail, words, name="word"),
    url(r"^search/$", views.search, name="search"),
    
    url(r'^admin/(.*)', admin.site.root, name="admin"),
)
