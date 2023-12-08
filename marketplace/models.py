from django.db import models
from user.models import CustomUser

class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    images = models.ManyToManyField('Image', related_name='products')
    phone = models.CharField(max_length=15)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        app_label = 'marketplace'

class Image(models.Model):
    image = models.ImageField(upload_to='product_images/')

    class Meta:
        app_label = 'marketplace'
