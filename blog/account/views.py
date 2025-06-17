from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework import status



# Handles user registration


class RegisterView(APIView):
    # Handles POST requests
    def post(self , request):
        try:
            # Get the data sent by the user (from the request body)
            data = request.data
              # Pass the data to our RegisterSerializer

            serializer = RegisterSerializer(data = data)

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message':'something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)
            
             # Save the user if data is valid
            
            serializer.save()

            return Response({
                'data':{},
                'message': "your account is created"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                    'data': {},
                    'message':'something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)
        


# Handles user login

class LoginView(APIView):

    def post(self, request):
        try:

            data = request.data
            serializer = LoginSerializer(data = data)

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message':'something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            response = serializer.get_jwt_token(serializer.data)

            return Response(response,status= status.HTTP_200_OK)  



        except Exception as e:
            return Response({
                    'data': {},
                    'message':'something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)


    