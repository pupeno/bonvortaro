from django.db import models

class Word(models.Model):
    word = models.CharField(max_length=70)
    natural_ending = models.CharField(max_length=1)
    
    # Not used or unknown.
    ofc = models.CharField(max_length=1)
    
    # Reta-vortaro specific.
    mrk = models.CharField(max_length=100)

    class Admin:
        list_display = ("word", "natural_ending")
