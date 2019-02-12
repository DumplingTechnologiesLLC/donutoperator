from rest_framework import serializers
from bodycams.models import Bodycam
from roster.models import Shooting
from roster import serializers as ros
# from roster.serializers import ShootingSerializer


# this shouldn't be necessary, but imports are failing for some reason
class ShootingSerializerForBodycam(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    race = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    bodycam = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()

    def get_sources(self, obj):
        sources = obj.sources.all()
        sources_serialized = []
        for source in sources:
            sources_serialized.append(ros.SourceSerializer(source, read_only=True).data)
        return sources_serialized

    def get_bodycam(self, obj):
        if obj.has_bodycam:
            return BodycamSerializer(obj.bodycams.all().first()).data
        else:
            return None

    def get_tags(self, obj):
        tags = obj.tags.all()
        tags_serialized = []
        for tag in tags:
            tags_serialized.append(ros.TagSerializer(tag, read_only=True).data)
        return tags_serialized

    def get_state(self, obj):
        return obj.get_state_display()

    def get_race(self, obj):
        return obj.get_race_display()

    def get_gender(self, obj):
        return obj.get_gender_display()

    class Meta:
        model = Shooting
        fields = (
            "state", "city", "description", "name",
            "race", "gender", "date", "age", "tags",
            "bodycam", "sources", "id",
        )


class BodycamWithShootingSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()
    shooting = ShootingSerializerForBodycam(read_only=True)
    tags = serializers.SerializerMethodField()

    def get_state(self, obj):
        return obj.get_state_display()

    def get_tags(self, obj):
        tags = obj.tags.all()
        tags_serialized = []
        for tag in tags:
            tags_serialized.append(ros.TagSerializer(tag, read_only=True).data)
        return tags_serialized

    class Meta:
        model = Bodycam
        fields = (
            "title", "video", "description", "department", "state", "city", "date",
            "shooting", "tags", "id"
        )


class BodycamSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        tags = obj.tags.all()
        tags_serialized = []
        for tag in tags:
            tags_serialized.append(ros.TagSerializer(tag, read_only=True).data)
        return tags_serialized

    def get_state(self, obj):
        return obj.get_state_display()

    class Meta:
        model = Bodycam
        fields = (
            "title", "video", "description", "department", "state", "city", "date", "id",
            "tags",
        )
