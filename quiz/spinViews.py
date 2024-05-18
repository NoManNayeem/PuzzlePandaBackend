# views.py
from datetime import date
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Spin, Profile
from .serializer import SpinSerializer

class SpinDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        today = date.today()
        try:
            spin = Spin.objects.get(user=user, date=today)
        except Spin.DoesNotExist:
            spin = Spin(user=user, date=today, count=0)
            spin.save()
        serializer = SpinSerializer(spin)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = request.user
        today = date.today()
        try:
            spin = Spin.objects.get(user=user, date=today)
        except Spin.DoesNotExist:
            spin = Spin(user=user, date=today, count=0)
        
        gift = request.data.get('gift', None)
        coins = request.data.get('coins', 0)
        print(f"Gift: {gift}, Coins: {coins}")
        
        if spin.count < 5:
            spin.count += 1
            spin.save()

            if coins > 0:
                profile, created = Profile.objects.get_or_create(user=user)
                profile.credits += coins
                profile.save()

            return Response({"message": "Spin count updated successfully", "count": spin.count, "gift": gift, "coins": coins}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Daily spin limit reached"}, status=status.HTTP_400_BAD_REQUEST)
