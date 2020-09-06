from django.shortcuts import render
from django.http import HttpResponse,  HttpRequest, HttpResponseRedirect
from . import util
from django import forms
from django.urls import reverse
from random import choice
from difflib import SequenceMatcher as SM

from markdown2 import Markdown
markdowner = Markdown()

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    definition = forms.CharField(label="Definition", widget=forms.Textarea(attrs={'rows': 1,
                                  'cols': 40,
                                  'style': 'height: 6em;'}))

class EditPageForm(forms.Form):
    title =None
    definition= None
    
    



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, name):
    
    return render(request, "encyclopedia/wiki.html", {
        "entry": markdowner.convert( util.get_entry(name)), "title":name
    })
    
def create(request):
    if request.method == 'POST':
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            definition = form.cleaned_data["definition"]
            if title in util.list_entries():
                print("Entro al if ")
                return render(request, "encyclopedia/wiki.html", {
                    "entry": markdowner.convert("##The page already exist"), "title":"Error"
                    })
            util.save_entry(title,definition)
            return HttpResponseRedirect("wiki/" + str(title))
        else:
            print("Form is not valid")
    else:
        return render(request, "encyclopedia/create.html",{"form": NewPageForm()})

def edit(request, name):
    if request.method == 'POST':
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            definition = form.cleaned_data["definition"]
            util.edit_entry(title,definition)
            return HttpResponseRedirect("/wiki/" + str(title))
        else:
            print("Form is not valid")

    definition=util.get_entry(name)
    div = definition.split("\n")
    div.pop(0) #remove title 
    definition= ''.join(div)
    
    form = NewPageForm(initial={'title': name , 'definition': definition})
    
    return render(request, "encyclopedia/edit.html",{"form":form ,"title":name  })


def random(request):
    
    page=choice(util.list_entries())
    
    return HttpResponseRedirect("wiki/" + str(page))

def search(request):
    query = request.GET.get('q')
    pages=util.list_entries()
    matches=[]
    if query in pages:
        return HttpResponseRedirect("wiki/" + str(query))
    
    for page in pages:
        coef=SM(None, page, query).ratio()
        if coef>=0.3:
            matches.append(page)
    
    return render(request, "encyclopedia/results.html", {
        "entries": matches
    }) 