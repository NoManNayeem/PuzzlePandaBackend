from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView, TokenVerifyView
from quiz.RegisterView import RegisterView
from quiz.views import QuizListView,  ProfileCreate, ProfileDetail, FAQsList, SliderList
from .resultView import ValidateResultView, UserPerformanceView





urlpatterns = [

    path('user-performance/', UserPerformanceView.as_view(), name='user_performance'),
    path('validate-result/', ValidateResultView.as_view(), name='validate-result'),

    
    path('sliders/', SliderList.as_view(), name='slider-list'),
    path('faqs/', FAQsList.as_view(), name='faqs-list'),
    
    
    
    
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),


    path('profile/', ProfileDetail.as_view(), name='profile-detail'),
    path('profile/create/', ProfileCreate.as_view(), name='profile-create'),
    
    
    
    
    path('register/', RegisterView.as_view(), name='register'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
