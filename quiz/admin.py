from django.contrib import admin
from .models import Profile, Quiz, FAQs, Slider
from django import forms
import base64




@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_subscribed', 'credits', 'primary_phone', 'subscription_phone', 'operator', 'full_name')
    search_fields = ('user__username', 'user__email', 'primary_phone', 'subscription_phone', 'full_name')
    list_filter = ('is_subscribed', 'operator')
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        if not obj.is_subscribed:
            obj.is_active = False
        super().save_model(request, obj, form, change)



class QuizAdminForm(forms.ModelForm):
    question = forms.CharField(widget=forms.Textarea)
    options = forms.CharField(widget=forms.Textarea)
    correct_answer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Quiz
        fields = ['question', 'options', 'correct_answer']

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            # Decode fields for display
            self.fields['question'].initial = base64.b64decode(self.instance._question.encode('ascii')).decode('utf-8')
            self.fields['options'].initial = base64.b64decode(self.instance._options.encode('ascii')).decode('utf-8')
            self.fields['correct_answer'].initial = base64.b64decode(self.instance._correct_answer.encode('ascii')).decode('utf-8')

    def clean_question(self):
        question = self.cleaned_data['question']
        try:
            question_encoded = base64.b64encode(question.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            raise forms.ValidationError("Encoding error in question field")
        return question_encoded

    def clean_options(self):
        options = self.cleaned_data['options']
        try:
            options_encoded = base64.b64encode(options.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            raise forms.ValidationError("Encoding error in options field")
        return options_encoded

    def clean_correct_answer(self):
        correct_answer = self.cleaned_data['correct_answer']
        try:
            correct_answer_encoded = base64.b64encode(correct_answer.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            raise forms.ValidationError("Encoding error in correct_answer field")
        return correct_answer_encoded





class UploadFileForm(forms.Form):
    file = forms.FileField()




from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import admin, messages
from .models import Quiz
import pandas as pd
import base64

class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm
    list_display = ('decoded_question', 'decoded_options', 'decoded_correct_answer')
    search_fields = ('decoded_question', 'decoded_correct_answer')
    change_list_template = "admin/quiz_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-file/', self.admin_site.admin_view(self.upload_file), name='appname_quiz_upload_file')
        ]
        return custom_urls + urls

    def upload_file(self, request):
        if request.method == "POST":
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["file"]
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    question = row['question']
                    options = row['options']
                    correct_answer = row['correct_answer']
                    Quiz.objects.create(
                        _question=base64.b64encode(question.encode('utf-8')).decode('ascii'),
                        _options=base64.b64encode(options.encode('utf-8')).decode('ascii'),
                        _correct_answer=base64.b64encode(correct_answer.encode('utf-8')).decode('ascii')
                    )
                self.message_user(request, "Quizzes created successfully", messages.SUCCESS)
                return HttpResponseRedirect("../")
        else:
            form = UploadFileForm()
        context = {
            'form': form,
            'title': 'Upload Quizzes from file',
        }
        return render(request, "admin/upload_file.html", context)

    def decoded_question(self, obj):
        return base64.b64decode(obj._question.encode('ascii')).decode('utf-8')
    decoded_question.short_description = 'Question'

    def decoded_options(self, obj):
        return base64.b64decode(obj._options.encode('ascii')).decode('utf-8')
    decoded_options.short_description = 'Options'

    def decoded_correct_answer(self, obj):
        return base64.b64decode(obj._correct_answer.encode('ascii')).decode('utf-8')
    decoded_correct_answer.short_description = 'Correct Answer'

admin.site.register(Quiz, QuizAdmin)



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



from .models import Digimart

class DigimartAdmin(admin.ModelAdmin):
    list_display = ('APP_ID', 'API_Key', 'API_Secret', 'API_Password')
    search_fields = ('APP_ID', 'API_Key')

admin.site.register(Digimart, DigimartAdmin)






from .models import Performance

class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_quizzes_played', 'correct_answers', 'wrong_answers', 'date_played')
    list_filter = ('user', 'date_played')
    search_fields = ('user__username',)
    ordering = ('-date_played',)

admin.site.register(Performance, PerformanceAdmin)



# admin.py
from .models import Spin

class SpinAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'count')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)

admin.site.register(Spin, SpinAdmin)
