from bonvortaro.vortaro import models
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.list_detail import object_list, object_detail

admin.autodiscover()

roots = {
    "queryset": models.Root.objects.all(),
    "template_object_name": "root"
}

urlpatterns = patterns(
    '',
    url(r"^root/$", object_list, roots, name="roots"),
    
    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),
)
