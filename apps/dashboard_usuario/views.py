from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from .models import Currency, MoneyDelivery, Balance
from .serializers import CurrencySerializer, MoneyDeliverySerializer, BalancesSerializer, UserSerializerWithToken, \
    UserSerializer, UserHistorySerializer
from .business import send_money_to_user, get_users_by_currencies, get_user_history_by_currency
from apps.utils.custom_exceptions import NotEnoughMoneyException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.http import JsonResponse

# Create your views here.


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows currencies to be viewed or edited.
    """
    queryset = Currency.objects.all().order_by('-name')
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]


class BalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows currencies to be viewed or edited.
    """
    queryset = Balance.objects.all()
    serializer_class = BalancesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        username_logged_user = request.user.username

        queryset = Balance.objects.filter(user__username=username_logged_user)
        serializer = BalancesSerializer(queryset, many=True)
        return Response(serializer.data)


class SendMoneyViewSet(viewsets.ViewSet):
    """
    API endpoint that allows currencies to be viewed or edited.
    """
    queryset = MoneyDelivery.objects.all()
    # serializer_class = MoneyDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]


    def list(self, request):
        username_logged_user = request.user.username

        queryset = MoneyDelivery.objects.filter(origin_user__username=username_logged_user)
        serializer = MoneyDeliverySerializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        print(request.data)
        serializer = MoneyDeliverySerializer(data=request.data)
        username_logged_user = request.user.username

        try:
            if serializer.is_valid(raise_exception=True):
                print(serializer.initial_data)
                print(dir(serializer))
                src_user = User.objects.get(username=username_logged_user)
                print(1)
                dst_user = User.objects.get(username=serializer.initial_data['destiny_user'])
                print(2)
                currency = Currency.objects.get(name=serializer.initial_data['currency'])
                print(3)
                value = serializer.initial_data['value']
                print(4)
                value = float(value)
                print(5)

                send_money_to_user(src_user, dst_user, currency, value)

                return Response({
                    'status': 'OK',
                    'message': 'Se ha mandado dinero correctamente'
                }, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
                return Response({
                    'status': 'ERROR',
                    'message': 'Ha habido un problema mandando dinero'
                }, status=status.HTTP_400_BAD_REQUEST)
        except NotEnoughMoneyException:
            return Response({
                'status': 'ERROR',
                'message': 'No se dispone de suficientes fondos para hacer esta transferencia'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: #agregar exception no tiene dinero suficiente
            return Response({
                'status': 'ERROR',
                'message': 'Ha habido un problema mandando dinero: {0}'.format(str(e))
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """
    print(request.user)
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListByCurrencies(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)

    # def get(self, request):
    #     serializer = UserSerializer(request.user)
    #     return JsonResponse(get_users_by_currencies(serializer))

    def list(self, request):
        serializer = UserSerializer(request.user)

        return JsonResponse(get_users_by_currencies(serializer))

        # queryset = MoneyDelivery.objects.filter(origin_user__username=username_logged_user)
        # serializer = MoneyDeliverySerializer(queryset, many=True)
        # return Response(serializer.data)


class UserHistoryViewset(viewsets.ViewSet):
    #permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        username_logged_user = request.user.username
        serializer = UserHistorySerializer(data=request.GET)

        try:
            print(2)
            if serializer.is_valid(raise_exception=False):
                print(3)
                transactions = get_user_history_by_currency(username_logged_user,
                                                            serializer.initial_data['currency'])
                print(4)

                return JsonResponse(transactions, safe=False)

        except Exception as e:
            return JsonResponse({'err': str(e)})






