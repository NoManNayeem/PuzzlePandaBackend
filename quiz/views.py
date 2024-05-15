from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Quiz, Profile
from .serializer import QuizSerializer, ProfileSerializer
from django.db.models import Count
import random
from rest_framework import generics, permissions


class ProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class ProfileCreate(generics.CreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)






class QuizListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            n = int(request.query_params.get('n', 10))  # Default to 10 if 'n' is not provided
        except ValueError:
            return Response({"error": "Invalid value for 'n'"}, status=400)
        
        quizzes = Quiz.objects.all()[:n]
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)


class PlayAgainView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            n = int(request.query_params.get('n', 10))  # Default to 10 if 'n' is not provided
        except ValueError:
            return Response({"error": "Invalid value for 'n'"}, status=400)

        quiz_count = Quiz.objects.aggregate(count=Count('id'))['count']
        if n > quiz_count:
            n = quiz_count  # Adjust n if it exceeds the number of available quizzes

        random_ids = random.sample(range(1, quiz_count + 1), n)
        quizzes = Quiz.objects.filter(id__in=random_ids)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)
    
    
    
    



from rest_framework import generics
from .models import FAQs
from .serializer import FAQsSerializer

class FAQsList(generics.ListAPIView):
    queryset = FAQs.objects.all()
    serializer_class = FAQsSerializer
    permission_classes = []




from rest_framework import generics
from .models import Slider
from .serializer import SliderSerializer

class SliderList(generics.ListAPIView):
    queryset = Slider.objects.all()
    serializer_class = SliderSerializer
    permission_classes = []
