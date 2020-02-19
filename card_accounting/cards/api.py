# -*- coding: utf-8 -*-

"""API module for interaction with cards."""

import json
import socket

from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from cards.models import Card, CardHolder

SUCCESS_RESPONSE_CODE = 200
BAD_REQUEST_RESPONSE_CODE = 400


# TODO: refactor to snippets
@csrf_exempt
def release_card(request):
    """Create new card for customer.

    Args:
        request: HTTP request.

    Returns:
        JSON http response.

    """
    card_info = request.POST
    try:
        holder = CardHolder.objects.get(pk=card_info['customer_id'])
    except models.Model.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': "Customer doesn't exist"},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    new_card = Card.release_card(holder)

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Card released successful',
        'created_card_number': new_card.card_number,
        'created': new_card.creation_date,
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)


def get_balance(request, **kwargs):
    """Get given card balance.

    Args:
        request: HTTP request.
        kwargs: request parameters.

    Returns:
        JSON response.

    """
    card_info = kwargs

    try:
        card = Card.objects.get(card_number=card_info['card_number'])
    except Card.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid card number'},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Balance got successful',
        'balance': card.balance,
        'time': timezone.now(),
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)


@csrf_exempt
def enroll_money(request, **kwargs):
    """Enroll money on given card number.

    Args:
        request: HTTP request.
        kwargs: request parameters.

    Returns:
        JSON response.

    """
    card_number = kwargs['card_number']
    transaction_info = json.loads(request.body)

    try:
        card = Card.objects.get(card_number=card_number)
    except Card.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid card number'},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    transaction = card.update_balance(int(transaction_info['amount']))

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Money enrolled successful',
        'time': transaction.creation_date,
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)


@csrf_exempt
def write_off_money(request, **kwargs):
    """Write off money on given card number.

    Args:
        request: HTTP request.
        kwargs: request parameters.

    Returns:
        JSON response.

    """
    card_number = kwargs['card_number']
    transaction_info = json.loads(request.body)

    try:
        card = Card.objects.get(card_number=card_number)
    except models.Model.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid card number'},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    transaction = card.update_balance(
        int(transaction_info['amount']),
        update_type='WRITE_OFF',
    )

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Money written off successful',
        'time': transaction.creation_date,
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)


def get_transactions(request, **kwargs):
    """Get given card transactions.

    Args:
        request: HTTP request.
        kwargs: request parameters.

    Returns:
        JSON response.

    """
    card_info = kwargs

    try:
        card = Card.objects.get(card_number=card_info['card_number'])
    except models.Model.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid card number'},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    transactions = card.transaction_set.all()
    if card_info.get('list_size'):
        transactions = transactions[:card_info['list_size']]

    transactions_data = {}
    for num, transaction in enumerate(transactions):
        transactions_data[num] = {
            'type': transaction.transaction_type,
            'amount': transaction.amount,
            'date': transaction.creation_date,
        }

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Transactions got successful',
        'transactions': transactions_data,
        'time': timezone.now(),
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)
