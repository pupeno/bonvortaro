from bonvortaro.vortaro.models import Root, Word
from django.contrib import admin

class RootAdmin(admin.ModelAdmin):
    list_display = ["root", "kind", "begining", "ending", "ofc"]
    list_filter = ["begining", "ending", "kind", "ofc"]

admin.site.register(Root, RootAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display = ["word", "begining", "root", "ending", "kind", "ofc"]
    list_filter = ["ending", "kind", "ofc", "begining"]

admin.site.register(Word, WordAdmin)
