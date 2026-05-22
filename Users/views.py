from Users.models import Users, Address
from Users.serializers import UsersSerializer, AddressSerializer
from rest_framework import viewsets

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

