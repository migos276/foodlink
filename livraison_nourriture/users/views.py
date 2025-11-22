from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets,filters,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import Restaurant, Livreur, CustomUser, Boutique, HoraireHebdomadaire, Horaire
from users.serializer import RestaurantSerializer, LivreurSerializer, CustomUserSerializer, BoutiqueSerializer, \
    HoraireHebdoSerializer, HoraireSerializer, TypePlatSerializer, MyTokenObtainPairSerializer, CreateLivreurSerializer, \
    TypeBoutiqueSerializer
from users.utils import get_unique_code_for_model


# Create your views here.
def get_tokens_for_user(user):
    refresh=RefreshToken.for_user(user)
    access=refresh.access_token
    access['profile']=user.profile
    access['username'] = user.username
    return {
        'refresh':str(refresh),
        'access':str(access),
    }
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profile', 'email',"code"]

    @action(detail=False, methods=['post'], url_path='new_entreprise')
    def create_entreprise(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            code = get_unique_code_for_model(CustomUser)
            entreprise = serializer.save(profile="entreprise", password=code, code=code)
            return Response(CustomUserSerializer(entreprise).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='new_livreur')
    def create_livreur(self, request):

        serializer = CreateLivreurSerializer(data=request.data)
        data=serializer.data
        return Response(data,status=status.HTTP_201_CREATED)
    def get_serializer_class(self):
        if self.action=="create_livreur":
            return CreateLivreurSerializer
        else:
            return CustomUserSerializer

class RestaurantViewset(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    search_fields = ['user__username','user__email',"user__quartier"]
    filterset_fields = ['type_plat',"rate","est_ouvert","user"]



    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        restaurant=serializer.instance
        user=restaurant.user
        tokens=get_tokens_for_user(user)
        data=serializer.data
        data.update({
            'access':tokens['access'],
            'refresh': tokens["refresh"],
        })
        headers=self.get_success_headers(serializer.data)
        return Response(data,status=status.HTTP_201_CREATED,headers=headers)
class BoutiqueViewset(viewsets.ModelViewSet):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    search_fields = ['user__username',"user__quartier",'user__email']
    filterset_fields = ["est_ouvert","user","type","user__quartier"]

class LivreurViewset(viewsets.ModelViewSet):
    queryset = Livreur.objects.all()
    serializer_class = LivreurSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entreprise',"user"]



from rest_framework.decorators import api_view, action

class CreateEntrepriseView(APIView):
    def get(self, request):
        # Pour afficher les champs dans l'interface DRF
        serializer = CustomUserSerializer()
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            code = get_unique_code_for_model(CustomUser)

            entreprise = CustomUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                tel=data['tel'],
                quartier=data['quartier'],
                profile="entreprise",
                password=code,
                code=code
            )
            return Response(CustomUserSerializer(entreprise).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HoraireHebdoViewset(viewsets.ModelViewSet):
    queryset = HoraireHebdomadaire.objects.all()
    serializer_class = HoraireHebdoSerializer

class HoraireViewset(viewsets.ModelViewSet):
    queryset = Horaire.objects.all()
    serializer_class = HoraireSerializer

class TypePlatListView(APIView):
    """
    Vue pour retourner tous les types de plats uniques
    """

    def get(self, request, *args, **kwargs):
        # On récupère tous les types de plats distincts
        types = Restaurant.objects.values_list('type_plat', flat=True).distinct()

        # On transforme en liste de dictionnaires pour serializer
        data = [{'type_plat': t} for t in types]

        serializer = TypePlatSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TypeBoutiqueListView(APIView):
    """
    Vue pour retourner tous les types de plats uniques
    """

    def get(self, request, *args, **kwargs):
        # On récupère tous les types de plats distincts
        types = Boutique.objects.values_list('type', flat=True).distinct()

        # On transforme en liste de dictionnaires pour serializer
        data = [{'type': t} for t in types]

        serializer = TypeBoutiqueSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
