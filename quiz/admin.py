from django.contrib import admin
from .models import Profile

admin.site.register(Profile)




from .models import Quiz

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('question', 'correct_answer')




from .models import FAQs

@admin.register(FAQs)
class FAQsAdmin(admin.ModelAdmin):
    list_display = ('question',)






from .models import Slider

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')
