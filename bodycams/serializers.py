from rest_framework import serializers
from bodycams.models import Bodycam
# from roster.serializers import ShootingSerializer


# class BodycamWithShootingSerializer(serializers.ModelSerializer):
#     state = serializers.SerializerMethodField()
#     shooting = ShootingSerializer(read_only=True)

#     def get_state(self, obj):
#         return obj.get_state_display()

#     class Meta:
#         model = Bodycam
#         fields = (
#             "title", "video", "description", "department", "state", "city", "date",
#             "shooting"
#         )


class BodycamSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    def get_state(self, obj):
        return obj.get_state_display()

    class Meta:
        model = Bodycam
        fields = (
            "title", "video", "description", "department", "state", "city", "date",
        )
