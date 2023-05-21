from django.shortcuts import render
from django.http import HttpResponse
from .forms import SearchBrandForm
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .utils import get_car_brand
from PIL import Image
import numpy as np
from tensorflow import keras

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

            brand = get_car_brand(image, color)
            if brand is not None:
                try:
                    brand = Image.fromarray(brand)
                    brand_url = 'media/' + image.name + '_brand.png'
                    brand.save(brand_url)

                    brand_to_predict = Image.open(brand_url)
                    brand_to_predict = brand_to_predict.resize((240, 194))
                    img_array = np.array(brand_to_predict)
                    img_array = img_array[:, :, :3]
                    img_array = np.expand_dims(img_array, axis=0)
                    model = keras.models.load_model('model.h5')
                    predictions = model.predict(img_array, verbose=0)
                    print(predictions)
                    predicted_class = np.argmax(predictions)

                    brand_title = ["Hyundai","Lexus","Mazda","Mercedes","Opel","Skoda","Toyota","Volkswagen"][predicted_class]

                    # If max probability is less than 0.999999999, we don't trust the prediction
                    if predictions[0][predicted_class] < 0.999999999:
                        brand_title = None
                
                except Exception as e:
                    print(e)
                    brand_url = None
                    brand_title = None
      
            else:
                brand_url = None
                brand_title = None

            context = {
                'image': uploaded_file_url,
                'brand_image': brand_url,
                'color': color,
                'brand': brand_title,
                'form': form
            }


    else:
        form = SearchBrandForm()
        context = {
            'form': form
        }

    return render(request, 'index.html', context)