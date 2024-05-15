from rest_framework import serializers
from .models import Profile, Quiz, FAQs, Slider
import base64

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'is_subscribed', 'credits', 'is_active']
        read_only_fields = ['user', 'is_active']


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('id', 'question', 'options', 'correct_answer')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['question'] = base64.b64decode(instance._question.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            representation['question'] = instance._question

        try:
            representation['options'] = base64.b64decode(instance._options.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            representation['options'] = instance._options

        try:
            representation['correct_answer'] = base64.b64decode(instance._correct_answer.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            representation['correct_answer'] = instance._correct_answer

        return representation

    def create(self, validated_data):
        validated_data['_question'] = base64.b64encode(validated_data['question'].encode('utf-8')).decode('ascii')
        validated_data['_options'] = base64.b64encode(validated_data['options'].encode('utf-8')).decode('ascii')
        validated_data['_correct_answer'] = base64.b64encode(validated_data['correct_answer'].encode('utf-8')).decode('ascii')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance._question = base64.b64encode(validated_data.get('question', instance.question).encode('utf-8')).decode('ascii')
        instance._options = base64.b64encode(validated_data.get('options', instance.options).encode('utf-8')).decode('ascii')
        instance._correct_answer = base64.b64encode(validated_data.get('correct_answer', instance.correct_answer).encode('utf-8')).decode('ascii')
        instance.save()
        return instance


class FAQsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQs
        fields = ['id', 'question', 'answer']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['question'] = base64.b64decode(instance._question.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            representation['question'] = instance._question

        try:
            representation['answer'] = base64.b64decode(instance._answer.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            representation['answer'] = instance._answer

        return representation

    def create(self, validated_data):
        validated_data['_question'] = base64.b64encode(validated_data['question'].encode('utf-8')).decode('ascii')
        validated_data['_answer'] = base64.b64encode(validated_data['answer'].encode('utf-8')).decode('ascii')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance._question = base64.b64encode(validated_data.get('question', instance.question).encode('utf-8')).decode('ascii')
        instance._answer = base64.b64encode(validated_data.get('answer', instance.answer).encode('utf-8')).decode('ascii')
        instance.save()
        return instance


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
