import base64
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
