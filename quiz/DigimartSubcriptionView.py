# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.contrib.auth.models import User
from quiz.models import Profile
from quiz.DigimartSubscriptionModel import DigimartSubscription, DigimartChargingSubscriberModel
import hashlib
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
import requests






class GenerateApiEndpointView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Generate API endpoint for Digimart subscription",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'msisdn': openapi.Schema(type=openapi.TYPE_STRING, description='Mobile number')
            },
        ),
        responses={
            200: openapi.Response(description="API endpoint generated successfully", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'api_endpoint': openapi.Schema(type=openapi.TYPE_STRING, description='API endpoint URL')
                }
            )),
            400: "Bad request",
            404: "Not found",
            500: "Internal server error"
        }
    )
    def post(self, request):
        user = request.user
        msisdn = request.data.get('msisdn')
        print('msisdn===',msisdn)

        if not msisdn:
            profile = Profile.objects.filter(user=user).first()
            if profile and profile.primary_phone:
                msisdn = profile.primary_phone[2:]  # Remove the first two characters
            else:
                return Response({"error": "msisdn is required and not found in profile"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            digimart_subscription = DigimartSubscription.objects.last()  # Assuming only one record
            if not digimart_subscription:
                return Response({"error": "DigimartSubscription configuration is missing."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            api_key = digimart_subscription.API_Key
            api_secret = digimart_subscription.API_Secret
            redirect_url = digimart_subscription.redirect_URL
            request_id = f"0000{msisdn}"
            current_time_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            signature_data = f'{api_key}|{current_time_utc}|{api_secret}'
            hashed_signature = hashlib.sha512(signature_data.encode()).hexdigest()

            api_endpoint = f"https://user.digimart.store/sdk/subscription/authorize?apiKey={api_key}&requestId={request_id}&requestTime={current_time_utc}&signature={hashed_signature}&redirectUrl={redirect_url}&msisdn={msisdn}"
            
            if api_endpoint:
                digimart_subscriber, created = DigimartChargingSubscriberModel.objects.get_or_create(
                    user=user,
                    defaults={
                        'plain_msisdn': msisdn,
                        'masked_msisdn': '',
                        'subscription_status': 'UnKnown',
                        'subscription_notification': '',
                        'subscription_confirm_notification': ''
                    }
                )
                if not created:
                    digimart_subscriber.plain_msisdn = msisdn
                    digimart_subscriber.save()
                
            return Response({"api_endpoint": api_endpoint}, status=status.HTTP_200_OK)

        except DigimartSubscription.DoesNotExist:
            return Response({"error": "Subscription configuration not found."}, status=status.HTTP_404_NOT_FOUND)





class NotifyMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Receive notification and update subscription status",
        manual_parameters=[
            openapi.Parameter('timeStamp', openapi.IN_QUERY, description="Timestamp", type=openapi.TYPE_STRING),
            openapi.Parameter('subscriberId', openapi.IN_QUERY, description="Subscriber ID", type=openapi.TYPE_STRING),
            openapi.Parameter('applicationId', openapi.IN_QUERY, description="Application ID", type=openapi.TYPE_STRING),
            openapi.Parameter('version', openapi.IN_QUERY, description="Version", type=openapi.TYPE_STRING),
            openapi.Parameter('frequency', openapi.IN_QUERY, description="Frequency", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Status", type=openapi.TYPE_STRING),
            openapi.Parameter('subscriberRequestId', openapi.IN_QUERY, description="Subscriber Request ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(description="Subscription notification updated successfully", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            )),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Not found")
        }
    )
    def get(self, request):
        user = request.user
        print("request.body==>",request.body)
        
        timeStamp = request.query_params.get('timeStamp')
        subscriberId = request.query_params.get('subscriberId')
        applicationId = request.query_params.get('applicationId')
        version = request.query_params.get('version')
        frequency = request.query_params.get('frequency')
        status = request.query_params.get('status')
        subscriberRequestId = request.query_params.get('subscriberRequestId')

        if not user:
            return Response({"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            digimart_subscriber = DigimartChargingSubscriberModel.objects.get(user=user)

            if subscriberId:
                digimart_subscriber.masked_msisdn = subscriberId
            if status and status == "REGISTERED":
                digimart_subscriber.subscription_status = "Registered"
                
            request_data_dict = {
                "timeStamp": timeStamp,
                "subscriberId": subscriberId,
                "applicationId": applicationId,
                "version": version,
                "frequency": frequency,
                "status": status,
                "subscriberRequestId": subscriberRequestId
            }

            digimart_subscriber.subscription_notification = json.dumps(request_data_dict)
            digimart_subscriber.save()
            return Response({"message": "Subscription notification updated successfully."}, status=status.HTTP_200_OK)
        except DigimartChargingSubscriberModel.DoesNotExist:
            return Response({"error": "DigimartChargingSubscriberModel not found for the user."}, status=status.HTTP_404_NOT_FOUND)
        
        
        
        
        
class ConfirmNotificationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Receive confirmation notification and update subscription confirmation status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'timeStamp': openapi.Schema(type=openapi.TYPE_STRING, description='Timestamp'),
                'subscriberId': openapi.Schema(type=openapi.TYPE_STRING, description='Subscriber ID'),
                'applicationId': openapi.Schema(type=openapi.TYPE_STRING, description='Application ID'),
                'version': openapi.Schema(type=openapi.TYPE_STRING, description='Version'),
                'frequency': openapi.Schema(type=openapi.TYPE_STRING, description='Frequency'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status')
            }
        ),
        responses={
            200: openapi.Response(description="Subscription confirmation notification updated successfully", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            )),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Not found")
        }
    )
    def post(self, request):
        timeStamp = request.data.get('timeStamp')
        subscriberId = request.data.get('subscriberId')
        applicationId = request.data.get('applicationId')
        version = request.data.get('version')
        frequency = request.data.get('frequency')
        status = request.data.get('status')

        if not subscriberId:
            return Response({"message": "subscriberId is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            digimart_subscriber = DigimartChargingSubscriberModel.objects.get(masked_msisdn=subscriberId)

            request_data_dict = {
                "timeStamp": timeStamp,
                "subscriberId": subscriberId,
                "applicationId": applicationId,
                "version": version,
                "frequency": frequency,
                "status": status
            }

            digimart_subscriber.subscription_confirm_notification = json.dumps(request_data_dict)
            digimart_subscriber.save()
            return Response({"message": "Subscription confirmation notification updated successfully."}, status=status.HTTP_200_OK)
        except DigimartChargingSubscriberModel.DoesNotExist:
            return Response({"error": "DigimartChargingSubscriberModel not found for the subscriberId."}, status=status.HTTP_404_NOT_FOUND)
        
        

class UnsubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Handle unsubscription by sending a POST request to the unsubscription URL",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'action': openapi.Schema(type=openapi.TYPE_STRING, description='Action')
            }
        ),
        responses={
            200: openapi.Response(description="Unsubscription request processed successfully", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message')
                }
            )),
            400: openapi.Response(description="Bad request")
        }
    )
    def post(self, request):
        user = request.user
        action = 0

        if not action:
            return Response({"error": "Action is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscriberId = DigimartChargingSubscriberModel.objects.filter(user=user).first().masked_msisdn
            digimartApp = DigimartSubscription.objects.last()
            applicationId = digimartApp.APP_ID
            appPassword = digimartApp.API_Password

            payload = {
                "applicationId": applicationId,
                "password": appPassword,
                "subscriberId": subscriberId,
                "action": action
            }

            response = requests.post('https://api.digimart.store/subs/unregistration', json=payload)
            response_data = response.json()
            print("Response Data:", response_data)
            return Response({"message": response_data}, status=response.status_code)
        except DigimartChargingSubscriberModel.DoesNotExist:
            return Response({"error": "Subscriber not found."}, status=status.HTTP_404_NOT_FOUND)
        except DigimartSubscription.DoesNotExist:
            return Response({"error": "Subscription configuration not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        

        

class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Check subscription status by sending a POST request to the subscription status URL",
        responses={
            200: openapi.Response(description="Subscription status retrieved successfully", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message')
                }
            )),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Not found"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):
        user = request.user

        try:
            subscriberId = DigimartChargingSubscriberModel.objects.filter(user=user).first().masked_msisdn
            digimartApp = DigimartSubscription.objects.last()
            applicationId = digimartApp.APP_ID
            appPassword = digimartApp.API_Password

            payload = {
                "applicationId": applicationId,
                "password": appPassword,
                "subscriberId": subscriberId
            }

            response = requests.post('https://api.digimart.store/subscription/subscriberChargingInfo', json=payload)
            response_data = response.json()
            print("Response Data:", response_data)
            return Response({"message": response_data}, status=response.status_code)
        except DigimartChargingSubscriberModel.DoesNotExist:
            return Response({"error": "Subscriber not found."}, status=status.HTTP_404_NOT_FOUND)
        except DigimartSubscription.DoesNotExist:
            return Response({"error": "Subscription configuration not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)