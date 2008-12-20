from bonvortaro.vortaro.models import Root, Word, Definition #, Translation
from django.contrib import admin

class RootAdmin(admin.ModelAdmin):
    list_display = ["root", "kind", "begining", "ending", "ofc"]
    list_filter = ["begining", "ending", "kind", "ofc"]

admin.site.register(Root, RootAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display = ["language", "word", "kind", "begining", "root", "ending", "ofc", "mrk", "revo_link"]
    list_filter = ["ending", "kind", "ofc", "begining", "language"]
    
    def revo_link(self, word):
        return "<a href=\"%s\">%s</a>" % (word.revo_url(), word.revo_url())
    revo_link.short_description = "Reta Vortaro"
    revo_link.allow_tags = True

admin.site.register(Word, WordAdmin)

class DefinitionAdmin(admin.ModelAdmin):
    list_display = ["word", "definition"]

admin.site.register(Definition, DefinitionAdmin)
