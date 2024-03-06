from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone', 'surname', 'name', 'patronymic',]


class CoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coords
        fields = '__all__'


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    data = serializers.URLField()

    class Meta:
        model = Photo
        fields = ['data', 'title']


class MountSerializer(WritableNestedModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer(allow_null=True)
    photo = PhotoSerializer(many=True)

    class Meta:
        model = Mount
        depth = 1
        fields = ('id', 'user', 'beautyTitle', 'title', 'other_titles', 'connect', 'coords', 'level', 'photo', 'add_time')
        read_only_fields = ['status']

    def create(self, validated_data, **kwargs):
        user = validated_data.pop('user')
        coords = validated_data.pop('coords')
        level = validated_data.pop('level')
        photo = validated_data.pop('photo')

        selected_user = User.objects.filter(email=user['email'])
        if selected_user.exists():
            user_serializer = UserSerializer(data=user)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
        else:
            user = User.objects.create(**user)

        coords = Coords.objects.create(**coords)
        level = Level.objects.create(**level)
        mount = Mount.objects.create(**validated_data, user=user, coords=coords, level=level, status='new')

        for image in photo:
            data = image.pop('data')
            title = image.pop('title')
            Photo.objects.create(data=data, mount=mount, title=title)

        return mount

