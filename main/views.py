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
            color = form.cleaned_data['color']
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            uploaded_file_url = fs.url(filename)
            # brand = algorithm(image, color) <-- se le pasa la red neuronal, devolverá 'none' si no hay algún resultado claro
            context = {
                'image': uploaded_file_url,
                'color': color,
                'brand': 'opel',
                'form': form
            }


    else: 
        form = SearchBrandForm()
        context = {
            'form': form
        }

    return render(request, 'index.html', context)