from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(default=False)
    credits = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.is_subscribed:
            self.is_active = False
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username





class Quiz(models.Model):
    question = models.CharField(max_length=255)
    options = models.TextField()  # Comma-separated options
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question

    def get_options_list(self):
        return self.options.split(',')





class FAQs(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question






class Slider(models.Model):
    image = models.ImageField(upload_to='sliders/')

    def __str__(self):
        return f"Slider {self.id}"
