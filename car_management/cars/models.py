from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the user model (default or custom)

class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.JSONField(default=list)  # Stores tags like ["sedan", "Toyota", "dealer"]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="car_images/")

    def __str__(self):
        return f"Image for {self.car.title}"
