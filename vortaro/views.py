from django.shortcuts import render_to_response
from bonvortaro.vortaro import forms

def search(request):
    if request.method == 'POST':
        form = forms.SearchForm(request.POST)
    else:
        form = forms.SearchForm(request.GET)
    return render_to_response("vortaro/search.html", {
        "form": form
    })
