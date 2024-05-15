from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'is_subscribed', 'credits', 'is_active']
        read_only_fields = ['user', 'is_active']




from .models import Quiz

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('id', 'question', 'options', 'correct_answer')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['options'] = instance.get_options_list()
        return representation





from .models import FAQs

class FAQsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQs
        fields = ['id', 'question', 'answer']




from .models import Slider

class SliderSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Slider
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
