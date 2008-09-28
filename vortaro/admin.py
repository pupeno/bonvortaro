from bonvortaro.vortaro.models import Root, Word, Definition, Translation
from django.contrib import admin

class RootAdmin(admin.ModelAdmin):
    list_display = ["root", "kind", "begining", "ending", "ofc"]
    list_filter = ["begining", "ending", "kind", "ofc"]

admin.site.register(Root, RootAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display = ["word", "kind", "begining", "root", "ending", "ofc", "mrk"]
    list_filter = ["ending", "kind", "ofc", "begining"]

admin.site.register(Word, WordAdmin)

class DefinitionAdmin(admin.ModelAdmin):
    list_display = ["word", "definition"]

admin.site.register(Definition, DefinitionAdmin)

class TranslationAdmin(admin.ModelAdmin):
     list_display = ["word", "language", "translation"]

     def word(self, translation):
         return translation.definition.word

admin.site.register(Translation, TranslationAdmin)
