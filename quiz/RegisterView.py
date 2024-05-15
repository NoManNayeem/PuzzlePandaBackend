from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .RegisterSerializer import RegisterSerializer  # Ensure you import RegisterSerializer correctly based on your project structure
from drf_yasg.utils import swagger_auto_schema

class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
