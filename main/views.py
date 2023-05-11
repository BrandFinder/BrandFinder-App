from django.shortcuts import render
from django.http import HttpResponse
from .forms import SearchBrandForm
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

# Create your views here.

def index(request):
    if request.method == 'POST':
        # we retrieve the values from the post 
        form = SearchBrandForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            fs = FileSystemStorage()
            fs.save(image.name, image)
            # call the algorithm with the image saved and the color

    else: 
        form = SearchBrandForm()

    return render(request, 'index.html', {'form': form})