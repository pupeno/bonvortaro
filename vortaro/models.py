from django.db import models

WORD_TYPES = (
    ("s", "suffix"),
    ("p", "prefix"),
    ("n", "noun"),
    ("nn", "plural noun"),
    ("a", "adjective"),
    ("aa", "plural adjective"),
    ("v", "verb"),
    ("d", "adverb")
)

class Word(models.Model):
    word = models.CharField(max_length=70)
    natural_ending = models.CharField(max_length=1)

    word_type = models.CharField(max_length=1, choices=WORD_TYPES)
    
    # Not used or unknown.
    ofc = models.CharField(max_length=2)
    fnt = models.CharField(max_length=20)
    
    # Reta-vortaro specific.
    mrk = models.CharField(max_length=100)

    class Admin:
        list_display = ("word", "natural_ending")
