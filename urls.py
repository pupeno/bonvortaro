from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^bonvortaro/', include('bonvortaro.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),
)
