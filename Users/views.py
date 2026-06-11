from Users.models import Users, Address, PasswordResetToken, Contact, PaymentMethodUser
from Users.serializers import (
    UsersSerializer, 
    AddressSerializer, 
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
    ContactSerializer,
    PaymentMethodUserSerializer
)
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
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

    serializer_class = CustomTokenObtainPairSerializer


# Criada apenas com o objetivo de listar os usuários e endereços cadastrados, para facilitar os testes. 
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
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):

        return self.request.user.addresses.all()

    def create(self, request, *args, **kwargs):

        user = self.request.user

        address = Address.objects.filter(

            street = request.data.get('street'),
            number = request.data.get('number'),
            city = request.data.get('city'),
            state = request.data.get('state'),
            cep = request.data.get('cep')

        ).first()

        # Caso o endereço da tentativa de criação existir, apenas associá-lo diretamente ao usuário,
        # ao invés de duplicidade.    
        if address:

            # Verifica se não tá postando o mesmo endereço já vinculado ao user.
            if address.users.filter(id=user.id).exists():
                return Response(
                    {"error": "Este endereço já está vinculado à sua conta."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            address.users.add(user)
            serializer = self.get_serializer(address)
            return Response (serializer.data, status = status.HTTP_200_OK)
        
        # Se não, será apenas mais um objeto criado.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_address = serializer.save()

        new_address.users.add(user)
    
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        user = self.request.user

        # Removendo a vinculação do endereço ao usuário, garantindo que não afete outros usuários do mesmo endereço.
        with transaction.atomic():
            address.users.remove(user)
            
            # Caso seja o último usuário a ser desvinculado, o endereço é limpo do banco de dados.
            if address.users.count() == 0:
                address.delete()
                return Response(
                    {"message": "Endereço removido e deletado permanentemente."}, 
                    status=status.HTTP_204_NO_CONTENT
                )
            # Caso contrário, apenas remove o user.
            return Response(
                {"message": "Endereço dissociado da sua conta."}, 
                status=status.HTTP_200_OK
            )
class ForgotPasswordView(APIView):

    @extend_schema(
        request = PasswordResetRequestSerializer,
        responses={200: str}
    )
    def post(self, request):
        
        serializer = PasswordResetRequestSerializer(data=request.data)
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
        request = PasswordResetConfirmSerializer,
        responses={200: dict}
    )
    def post(self, request):
        
        serializer = PasswordResetConfirmSerializer(data=request.data)
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


class ContactViewSet(viewsets.ModelViewSet): 
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]
    
    throttle_classes = [AnonRateThrottle]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):

        user_autenticado = request.user.is_authenticated

        if user_autenticado:
            if Contact.objects.filter(
                name=request.user.fullname,
                email=request.data.get('email'),
                subject=request.data.get('subject'),
                message=request.data.get('message')
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
            serializer.save(name=self.request.user.fullname)
        else:
            serializer.save()


class PaymentMethodViewSet(viewsets.ModelViewSet):

    # Apenas para o Swagger conseguir ler o formato
    queryset = PaymentMethodUser.objects.none()

    serializer_class = PaymentMethodUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return PaymentMethodUser.objects.filter(customer=user)
    
    # Garantindo que os usuários apenas deletem o seu próprio método.
    def destroy(self, request, *args, **kwargs):

        metodo_instancia = self.get_object()

        if metodo_instancia.customer != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este método.")

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        
        serializer.save(customer=request.user)

        return Response(serializer.data, status = status.HTTP_201_CREATED)