from .models import Balance, MoneyDelivery, MoneyDeliveryLock
from apps.utils.custom_exceptions import NotEnoughMoneyException
from .serializers import UserSerializer
from django.db.models import Q
import datetime


def get_user_balance(user, currency):
    balance = Balance.objects.get(user=user, currency=currency)
    return balance.value


def substract_money_from_account(user, currency, value):
    balance = Balance.objects.get(user=user, currency=currency)
    balance.value -= value
    balance.save()


def add_money_to_account(user, currency, value):
    balance = Balance.objects.get(user=user, currency=currency)
    balance.value += value
    balance.save()


def send_money_to_user(src_user, dst_user, currency, value):
    try:
        lock = MoneyDeliveryLock.objects.get(origin_user=src_user)
    except:
        lock = MoneyDeliveryLock(origin_user=src_user, locked=False)
        lock.save()
        lock = MoneyDeliveryLock.objects.get(origin_user=src_user)

    if lock.locked:
        raise Exception()

    else:
        lock.locked = True
        lock.save()

        amount_money_account = get_user_balance(src_user, currency)

        if amount_money_account >= value:
            money_delivery = MoneyDelivery(
                origin_user=src_user,
                destiny_user=dst_user,
                value=value,
                currency=currency
            )
            money_delivery.save()

            add_money_to_account(dst_user, currency, value)
            substract_money_from_account(src_user, currency, value)

            lock.locked = False

            lock.save()
        else:
            raise NotEnoughMoneyException()


def my_jwt_response_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


def get_users_by_currencies(serializer):
    to_return = {}
    balances = Balance.objects.all()

    for balance in balances:
        if not to_return.get(balance.currency.name):
            to_return[balance.currency.name] = []

        if serializer.data['username'] != balance.user.username:
            to_return[balance.currency.name].append(balance.user.username)


    return to_return


def get_user_history_by_currency(user, currency):
    print(user)
    print(currency)
    to_return = []
    transactions = MoneyDelivery.objects.filter(Q(origin_user__username=user, currency__name=currency) |
                                                Q(destiny_user__username=user, currency__name=currency)).order_by('timestamp')
    print(5)

    for transaction in transactions:
        to_return.append({
            'type': 'Transferencia a: ' + str(transaction.destiny_user.get_username()) if transaction.origin_user.get_username() == user
             else 'Recibido de: ' + str(transaction.origin_user.get_username()),
            'value': transaction.value,
            'timestamp': datetime.datetime.strftime(transaction.timestamp, "%d/%m/%Y")
        })

    return to_return
