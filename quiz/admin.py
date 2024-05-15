from django.contrib import admin
from .models import Profile, Quiz, FAQs, Slider
import base64

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_subscribed', 'credits', 'is_active')
    search_fields = ('user__username', 'user__email')
    list_filter = ('is_subscribed', 'is_active')
    readonly_fields = ('user', 'is_active')

    def save_model(self, request, obj, form, change):
        if not obj.is_subscribed:
            obj.is_active = False
        super().save_model(request, obj, form, change)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('question', 'options', 'correct_answer')
    search_fields = ('question', 'correct_answer')
    # Removed list_filter on correct_answer as it's not suitable for filtering

    def save_model(self, request, obj, form, change):
        obj._question = base64.b64encode(obj.question.encode('utf-8')).decode('utf-8')
        obj._options = base64.b64encode(obj.options.encode('utf-8')).decode('utf-8')
        obj._correct_answer = base64.b64encode(obj.correct_answer.encode('utf-8')).decode('utf-8')
        super().save_model(request, obj, form, change)

@admin.register(FAQs)
class FAQsAdmin(admin.ModelAdmin):
    list_display = ('question',)
    search_fields = ('question', 'answer')

    def save_model(self, request, obj, form, change):
        obj._question = base64.b64encode(obj.question.encode('utf-8')).decode('utf-8')
        obj._answer = base64.b64encode(obj.answer.encode('utf-8')).decode('utf-8')
        super().save_model(request, obj, form, change)

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')
    search_fields = ('id',)
