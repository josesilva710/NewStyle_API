from Users.models import Users, Address, PasswordResetToken, Contato
from Users.serializers import (
    UsersSerializer, 
    AddressSerializer, 
    passwordResetTokenSerializer, 
    ResetPasswordSerializer,
    MeuTokenPersonalizadoSerializer,
    ContatoSerializer
)
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from django.core.mail import send_mail

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
    serializer_class = MeuTokenPersonalizadoSerializer

#Criada apenas com o objetivo de listar os usuários e endereços cadastrados, para facilitar os testes. 
# Em um cenário real, não seria recomendado expor essas informações.
class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdminUser]

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class ForgotPasswordView(APIView):

    def post(self, request):

        serializer = passwordResetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:

            user = Users.objects.get(email=email)

            reset_token = PasswordResetToken.objects.create(user=user)

            print(f"\n[DEBUG] TOKEN GERADO: {reset_token.token}\n")
            
            link = f"http://127.0.0.1:8000/auth/reset-password?token={reset_token.token}"

            send_mail(
                subject="Recuperação de Senha",
                message=f"Olá, {user.fullname}. Use o link a seguir para redefinir sua senha: {link}",
                from_email="no-reply@ecommerce.com",
                recipient_list=[email],
                fail_silently=False,
            )

        except Users.DoesNotExist:

            pass
        except Exception as e:

            print(f"Erro interno: {e}")

        return Response({"message": 
                         "Se um usuário com esse email existir, um link de recuperação de senha foi enviado."}, 
                         status=status.HTTP_200_OK)

class ResetPasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:

            reset_token = PasswordResetToken.objects.get(token=token)

            if not reset_token.is_valid():
                return Response({"error": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

            user = reset_token.user
            user.set_password(new_password)
            user.save()

            reset_token.is_used = True
            reset_token.save()

            return Response({"message": "Senha redefinida com sucesso!"}, status=status.HTTP_200_OK)

        except PasswordResetToken.DoesNotExist:

            return Response({"error": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

class ContatoViewSet(viewsets.ModelViewSet):
    queryset = Contato.objects.all()
    serializer_class = ContatoSerializer
    permission_classes = [IsAuthenticated]