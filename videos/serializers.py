from rest_framework import serializers
from .models import Video, Tag


class VideoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'video',
            'description',
            'state',
            'city',
            'date',
        ]


class VideoSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    def get_state(self, obj):
        return obj.get_state_display()

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data

    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'video',
            'tags',
            'description',
            'state',
            'city',
            'date',
        ]


class TagSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    def get_display(self, obj):
        return obj.text

    def get_value(self, obj):
        return obj.text

    class Meta:
        model = Tag
        fields = ['id', 'text', 'value', 'display']
