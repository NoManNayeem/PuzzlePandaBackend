from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Quiz, Profile, Performance
from .serializer import PerformanceSerializer
from datetime import date
from django.db.models import F

class UserPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        performances = Performance.objects.filter(user=user).order_by('date_played')
        serializer = PerformanceSerializer(performances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ValidateResultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = user.profile

        if not profile.is_subscribed:
            return Response({"error": "User is not subscribed."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        quiz_ids = data.get('quiz_ids', [])
        user_answers = data.get('user_answers', [])

        if not quiz_ids or not user_answers:
            return Response({"error": "Quiz IDs and User Answers are required."}, status=status.HTTP_400_BAD_REQUEST)

        if len(quiz_ids) != len(user_answers):
            return Response({"error": "Quiz IDs and User Answers length mismatch."}, status=status.HTTP_400_BAD_REQUEST)

        correct_answers = 0
        wrong_answers = 0
        today = date.today()

        for quiz_id, user_answer in zip(quiz_ids, user_answers):
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                if quiz.correct_answer == user_answer:
                    correct_answers += 1
                else:
                    wrong_answers += 1
            except Quiz.DoesNotExist:
                return Response({"error": f"Quiz with ID {quiz_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        performance, created = Performance.objects.get_or_create(
            user=user,
            date_played=today,
            defaults={
                'total_quizzes_played': 1,
                'correct_answers': correct_answers,
                'wrong_answers': wrong_answers
            }
        )

        if not created:
            performance.total_quizzes_played = F('total_quizzes_played') + 1
            performance.correct_answers = F('correct_answers') + correct_answers
            performance.wrong_answers = F('wrong_answers') + wrong_answers
            performance.save(update_fields=['total_quizzes_played', 'correct_answers', 'wrong_answers'])

        # Deducting credit points
        profile.credit = F('credit') - 10
        profile.save(update_fields=['credit'])

        serializer = PerformanceSerializer(performance)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
