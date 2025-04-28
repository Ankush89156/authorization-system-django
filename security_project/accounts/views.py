from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UserProfile

class CustomLoginAPIView(APIView):
    def post(self, request):
        username_or_email = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username_or_email, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Token creation
        token, created = Token.objects.get_or_create(user=user)

        # Handle IP detection
        ip = self.get_client_ip(request)
        profile, created = UserProfile.objects.get_or_create(user=user)

        if profile.ip_address is None:
            profile.ip_address = ip
            profile.save()
        elif profile.ip_address != ip:
            # Send an email if the IP is different
            send_mail(
                'New Login Detected',
                f'A new login was detected from IP: {ip}',
                'admin@example.com',
                [user.email],
                fail_silently=False,
            )
            profile.ip_address = ip
            profile.save()

        return Response({'token': token.key})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
