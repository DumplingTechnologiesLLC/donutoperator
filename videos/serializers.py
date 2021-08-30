from rest_framework import serializers
from .models import Video, Tag


class VideoSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    def get_state(self, obj):
        return obj.get_state_display()

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data

    class Meta:
        model = Video
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'text']
