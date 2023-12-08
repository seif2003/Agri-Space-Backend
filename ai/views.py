from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import os
from PIL import Image
import torchvision.transforms.functional as TF
import numpy as np
import torch
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from .CNN import CNN
from rest_framework.authtoken.models import Token


from termcolor import colored
from pyfiglet import figlet_format


def custom_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        authorization_header = request.headers.get('Authorization')

        if not authorization_header or not authorization_header.startswith('Token '):
            return JsonResponse({'error': 'Invalid or missing authorization token'}, status=401)

        token_key = authorization_header.split(' ')[1]

        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        request.authenticated_user = token.user

        return view_func(request, *args, **kwargs)

    return _wrapped_view



static_dir = settings.STATIC_ROOT
media_dir = os.path.join(settings.BASE_DIR, 'media')

disease_info_path = os.path.join(static_dir, 'disease_info.csv')
supplement_info_path = os.path.join(static_dir, 'supplement_info.csv')
model_path = os.path.join(static_dir, 'plant_disease_model_1_latest.pt')

disease_info = pd.read_csv(disease_info_path , encoding='cp1252')
supplement_info = pd.read_csv(supplement_info_path,encoding='cp1252')

model = CNN(39)    
model.load_state_dict(torch.load(model_path))
model.eval()

def prediction(image_path):
    image = Image.open(image_path)
    image = image.resize((224, 224))
    input_data = TF.to_tensor(image)
    input_data = input_data.view((-1, 3, 224, 224))
    output = model(input_data)
    output = output.detach().numpy()
    index = np.argmax(output)
    return index

@custom_login_required
def submit(request):
    if request.method == 'POST':
        """if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file found in the request.'})"""
        image = request.FILES['image']
        filename = image.name
        file_path = os.path.join(media_dir, filename) 
        with open(file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        pred = prediction(file_path)
        pred = int(prediction(file_path))
        title = disease_info['disease_name'][pred]
        description = disease_info['description'][pred]
        prevent = disease_info['Possible Steps'][pred]
        image_url = disease_info['image_url'][pred]
        supplement_name = supplement_info['supplement name'][pred]
        supplement_image_url = supplement_info['supplement image'][pred]
        supplement_buy_link = supplement_info['buy link'][pred]
        image_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
        response = {
            'title' : title,
            'desc' : description,
            'prevent' : prevent,
            'image_url' : image_url,
            'pred' : pred,
            'sname' : supplement_name,
            'simage' : supplement_image_url,
            'buy_link' : supplement_buy_link,
            'uimage': image_url
        }

        text = f"AI Submission"

        print(colored(figlet_format(text), color="green"))

        return JsonResponse(response)