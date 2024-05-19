import base64
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    phone_regex = re.compile(r'^880\d{10}$')
    if not phone_regex.match(value):
        raise ValidationError('Invalid phone number, must be of the form 880XXXXXXXXXX')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(default=False)
    credits = models.IntegerField(default=0)
    primary_phone = models.CharField(validators=[validate_phone_number], max_length=13, blank=True)
    subscription_phone = models.CharField(validators=[validate_phone_number], max_length=13, blank=True)
    OPERATOR_CHOICES = [
        ('GP', 'Grameenphone'),
        ('BL', 'Banglalink'),
        ('RA', 'Robi/Airtel'),
        ('TT', 'Teletalk'),
    ]
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES, blank=True)
    full_name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.is_subscribed:
            self.user.is_active = False
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username 


class Quiz(models.Model):
    _question = models.TextField(db_column='question')
    _options = models.TextField(db_column='options')
    _correct_answer = models.TextField(db_column='correct_answer')

    @property
    def question(self):
        try:
            return base64.b64decode(self._question.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            return self._question

    @question.setter
    def question(self, value):
        try:
            self._question = base64.b64encode(value.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            self._question = value

    @property
    def options(self):
        try:
            return base64.b64decode(self._options.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            return self._options

    @options.setter
    def options(self, value):
        try:
            self._options = base64.b64encode(value.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            self._options = value

    @property
    def correct_answer(self):
        try:
            return base64.b64decode(self._correct_answer.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            return self._correct_answer

    @correct_answer.setter
    def correct_answer(self, value):
        try:
            self._correct_answer = base64.b64encode(value.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            self._correct_answer = value

    def __str__(self):
        return self.question

    def get_options_list(self):
        return self.options.split(',')


class FAQs(models.Model):
    _question = models.TextField(db_column='question')
    _answer = models.TextField(db_column='answer')

    @property
    def question(self):
        try:
            return base64.b64decode(self._question.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            return self._question

    @question.setter
    def question(self, value):
        try:
            self._question = base64.b64encode(value.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            self._question = value

    @property
    def answer(self):
        try:
            return base64.b64decode(self._answer.encode('ascii')).decode('utf-8')
        except (ValueError, UnicodeEncodeError, base64.binascii.Error):
            return self._answer

    @answer.setter
    def answer(self, value):
        try:
            self._answer = base64.b64encode(value.encode('utf-8')).decode('ascii')
        except UnicodeEncodeError:
            self._answer = value

    def __str__(self):
        return self.question


class Slider(models.Model):
    image = models.ImageField(upload_to='sliders/')

    def __str__(self):
        return f"Slider {self.id}"





from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Performance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performances')
    total_quizzes_played = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    date_played = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.user.username} - {self.date_played}"

    @property
    def total_questions(self):
        return self.correct_answers + self.wrong_answers



# models.py
from django.contrib.auth.models import User
from django.db import models

class Spin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.count} spins"
