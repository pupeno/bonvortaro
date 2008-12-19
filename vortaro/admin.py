from bonvortaro.vortaro.models import Root, Word, Definition, Translation
from django.contrib import admin

class RootAdmin(admin.ModelAdmin):
    list_display = ["root", "kind", "begining", "ending", "ofc"]
    list_filter = ["begining", "ending", "kind", "ofc"]

admin.site.register(Root, RootAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display = ["language", "word", "kind", "begining", "root", "ending", "ofc", "mrk"]
    list_filter = ["ending", "kind", "ofc", "begining", "language"]

admin.site.register(Word, WordAdmin)

class DefinitionAdmin(admin.ModelAdmin):
    list_display = ["word", "definition"]

admin.site.register(Definition, DefinitionAdmin)
