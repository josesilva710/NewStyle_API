from Users.models import Users, Address, PasswordResetToken, Contato, MetodoPagamentoUsuario
from Users.serializers import (
    UsersSerializer, 
    AddressSerializer, 
    PasswordResetTokenSerializer, 
    ResetPasswordSerializer,
    MeuTokenPersonalizadoSerializer,
    ContatoSerializer,
    MetodoPagamentoUsuarioSerializer
)
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from django.core.mail import send_mail
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema

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
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):

        user = self.request.user

        if self.request.user.is_staff == True:

            return Users.objects.all()

        return Users.objects.filter(id = user.id)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    #   Fica registrado a intenção de incluir um CRUD p/ endereços do usuário, assim como se surgir um endereço
    # exatamente igual à algum registrado (Ex: prédio de trabalho)

class ForgotPasswordView(APIView):

    @extend_schema(
            
        request = PasswordResetTokenSerializer,
        responses={200: str}

    )

    def post(self, request):

        serializer = PasswordResetTokenSerializer(data=request.data)
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

    permission_classes = [AllowAny]

    @extend_schema(
            
        request = ResetPasswordSerializer,
        responses={200: dict}

    )

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
    permission_classes = [AllowAny]
    
    throttle_classes = [AnonRateThrottle]

    http_method_names = ['post']

    def create(self, request, *args, **kwargs):

        user_autenticado = request.user.is_authenticated

        if user_autenticado:
            
            if Contato.objects.filter(
                nome=request.user.fullname,
                email=request.data.get('email'),
                assunto=request.data.get('assunto'),
                mensagem=request.data.get('mensagem')
            ).exists():
                raise serializers.ValidationError("Você já enviou uma solicitação de contato com os mesmos detalhes. " \
                "Por favor, aguarde nossa resposta antes de enviar outra solicitação.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"message": "Sua mensagem foi recebida. Entraremos em contato em até 72h!"}
            , status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(nome=self.request.user.fullname)
        else:
            serializer.save()

class MetodoPagamentoViewSet(viewsets.ModelViewSet):

    #Apenas para o Swagger conseguir ler o formato
    queryset = MetodoPagamentoUsuario.objects.none()

    serializer_class = MetodoPagamentoUsuarioSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):

        user = self.request.user

        return MetodoPagamentoUsuario.objects.filter(cliente = user)
    
    # Garantindo que os usuários apenas deletem o seu próprio método.
    def destroy(self, request, *args, **kwargs):

        metodo_instancia = self.get_object()

        if metodo_instancia.cliente != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este método.")

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        user = self.request.user

        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception = True)

        serializer.save(cliente = request.user)

        return Response(serializer.data, status = status.HTTP_201_CREATED)

