from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Car, CarImage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image']

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Car
        fields = ['id', 'title', 'description', 'tags', 'owner', 'images', 'uploaded_images']
        extra_kwargs = {'owner': {'read_only': True}}

    def create(self, validated_data):
        images_data = validated_data.pop('uploaded_images', [])
        car = Car.objects.create(**validated_data)

        for image in images_data[:10]:  # Limit to 10 images
            CarImage.objects.create(car=car, image=image)
        
        return car

    def update(self, instance, validated_data):
        images_data = validated_data.pop('uploaded_images', None)

        # Update Car Fields
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.save()

        # If new images are uploaded, replace the old ones
        if images_data:
            instance.images.all().delete()
            for image in images_data[:10]:
                CarImage.objects.create(car=instance, image=image)

        return instance

