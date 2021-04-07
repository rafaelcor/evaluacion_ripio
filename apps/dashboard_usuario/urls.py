from django.urls import include, path
from rest_framework import routers
from .views import CurrencyViewSet, SendMoneyViewSet, BalanceViewSet, current_user, UserListByCurrencies, \
    UserHistoryViewset

router = routers.DefaultRouter()
router.register(r'currencies', CurrencyViewSet)
router.register(r'send_money', SendMoneyViewSet)
router.register(r'balances', BalanceViewSet)
router.register(r'user_by_currencies', UserListByCurrencies, basename="User")
router.register(r'user_history', UserHistoryViewset, basename="MoneyDelivery")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('current_user/', current_user),

]