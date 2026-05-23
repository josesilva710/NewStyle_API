from Users.models import Users, Address
from Users.serializers import UsersSerializer, AddressSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

class RegisterView(APIView):
    permission_classes = [AllowAny]

    serializer_class = UsersSerializer

    def post(self, request):

        serializer = UsersSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {"message":"usuário cadastrado com sucesso!" }, 
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

#Criada apenas com o objetivo de listar os usuários e endereços cadastrados, para facilitar os testes. 
# Em um cenário real, não seria recomendado expor essas informações.
class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdminUser]

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer