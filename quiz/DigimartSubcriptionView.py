# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from quiz.models import Profile
from quiz.DigimartSubscriptionModel import DigimartSubscription, DigimartChargingSubscriberModel
import hashlib
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
import requests
import string
import random


def generate_request_id(user_id):
    user_id_str = str(user_id)
    if len(user_id_str) >= 14:
        raise ValueError("User ID is too long to generate a 15 character request ID.")
    
    remaining_length = 14 - len(user_id_str)  # 14 because 1 character is for the underscore
    alphanumeric_characters = string.ascii_letters + string.digits
    random_chars = ''.join(random.choices(alphanumeric_characters, k=remaining_length))
    
    return f"{user_id_str}_{random_chars}"


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
            request_id = generate_request_id(user.id)
            current_time_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            signature_data = f'{api_key}|{current_time_utc}|{api_secret}'
            hashed_signature = hashlib.sha512(signature_data.encode()).hexdigest()

            api_endpoint = f"https://user.digimart.store/sdk/subscription/authorize?apiKey={api_key}&requestId={request_id}&requestTime={current_time_utc}&signature={hashed_signature}&redirectUrl={redirect_url}&msisdn={msisdn}"
            
            if api_endpoint:
                digimart_subscriber, created = DigimartChargingSubscriberModel.objects.get_or_create(
                    user=user,
                    defaults={
                        'plain_msisdn': msisdn,
                        'request_id': request_id,
                        'masked_msisdn': '',
                        'subscription_status': 'UnKnown',
                        'subscription_notification': '',
                        'subscription_confirm_notification': ''
                    }
                )
                if not created:
                    digimart_subscriber.plain_msisdn = msisdn
                    digimart_subscriber.request_id = request_id
                    digimart_subscriber.save()
                
            return Response({"api_endpoint": api_endpoint}, status=status.HTTP_200_OK)

        except DigimartSubscription.DoesNotExist:
            return Response({"error": "Subscription configuration not found."}, status=status.HTTP_404_NOT_FOUND)


class NotifyMeView(APIView):
    permission_classes = [permissions.AllowAny]

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
        subscriberId = request.query_params.get('subscriberId')
        requestId = request.query_params.get('requestId')
        subscriptionStatus = request.query_params.get('subscriptionStatus')

        if not subscriberId:
            return Response({"message": "subscriberId is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not requestId:
            return Response({"message": "requestId is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not subscriptionStatus:
            return Response({"message": "subscriptionStatus is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            digimart_subscriber = DigimartChargingSubscriberModel.objects.filter(request_id=requestId).first()
            if not digimart_subscriber:
                return Response({"message": "Subscriber not found."}, status=status.HTTP_404_NOT_FOUND)

            user = digimart_subscriber.user
            if subscriberId:
                digimart_subscriber.masked_msisdn = subscriberId
            if subscriptionStatus and subscriptionStatus == "S1000":
                digimart_subscriber.subscription_status = "Registered"
                
            request_data_dict = {
                "subscriberId": subscriberId,
                "subscriptionStatus": subscriptionStatus,
                "requestId": requestId
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

        try:
            subscriber = DigimartChargingSubscriberModel.objects.filter(user=user).first()
            if not subscriber:
                return Response({"error": "Subscriber not found."}, status=status.HTTP_404_NOT_FOUND)
            subscriberId = subscriber.masked_msisdn
            digimartApp = DigimartSubscription.objects.last()
            if not digimartApp:
                return Response({"error": "Subscription configuration not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            applicationId = digimartApp.APP_ID
            appPassword = digimartApp.API_Password

            payload = {
                "applicationId": applicationId,
                "password": appPassword,
                "subscriberId": f"tel:{subscriberId}",
                "action": '0'
            }

            response = requests.post('https://api.digimart.store/subs/unregistration', json=payload)
            response_data = response.json()
            subscriber.unSubscription_notification = response_data
            user_profile = Profile.objects.get(user=user)
            user_profile.is_subscribed = False
            user_profile.save()
            subscriber.subscription_status = "UNREGISTER"
            subscriber.save()
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
            response_data, response_status = get_subscriber_charging_info(user)
            return Response(response_data, status=response_status)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#### Digimart Subscription Status Checking ####

def get_subscriber_charging_info(user):
    try:
        subscriber = DigimartChargingSubscriberModel.objects.filter(user=user).last()
        if not subscriber:
            return {"error": "Subscriber not found."}, status.HTTP_404_NOT_FOUND

        subscriber_id = subscriber.masked_msisdn
        digimart_app = DigimartSubscription.objects.last()
        if not digimart_app:
            return {"error": "Subscription configuration not found."}, status.HTTP_500_INTERNAL_SERVER_ERROR

        application_id = digimart_app.APP_ID
        app_password = digimart_app.API_Password

        payload = {
            "applicationId": application_id,
            "password": app_password,
            "subscriberId": f"tel:{subscriber_id}"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-Forwarded-For': '103.121.105.14',
        }
        response = requests.post('https://api.digimart.store/subscription/subscriberChargingInfo', headers=headers, json=payload)
        response_data = response.json()
        if response.status_code == 200:
            subscription_status = response_data.get('subscriberInfo', [{}])[0].get('subscriptionStatus', 'UNKNOWN')
            user_profile = Profile.objects.get(user=user)
            if subscription_status == 'REGISTERED':
                user_profile.is_subscribed = True
                user_profile.save()
            else:
                user_profile.is_subscribed = False
                user_profile.save()

        return {"message": response_data}, response.status_code
    except requests.RequestException as e:
        return {"error": str(e)}, status.HTTP_400_BAD_REQUEST
