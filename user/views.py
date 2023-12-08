from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import UserSerializer, AuthTokenSerializer
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from termcolor import colored
from pyfiglet import figlet_format


User = get_user_model()



class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):

        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_201_CREATED
        response.data = {
            'message': 'user created successfully'
        }
        text1 = f"{request.data['first_name']} {request.data['last_name']}"
        text2 = "User has been created :"

        print(colored(figlet_format(text2), color="green") + colored(figlet_format(text1), color="blue"))

        return response


class CustomAuthToken(ObtainAuthToken):
    serializer_class = AuthTokenSerializer  

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data,context={'request': request})
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            raise ValidationError({'message': e.detail['non_field_errors']})
        user = serializer.validated_data['user']

        Token.objects.filter(user=user).delete()

        token = Token.objects.create(user=user)
        
        text1 = f"{user.first_name} {user.last_name}"
        text2 = "has just logged in"

        print(colored(figlet_format(text1), color="blue") + colored(figlet_format(text2), color="green"))

        return Response({
            'message':'You have successfully logged in.',
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'location': user.location,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
