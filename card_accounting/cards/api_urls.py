# -*- coding: utf-8 -*-

"""URLs path list for api."""

from django.urls import path

from cards import api

urlpatterns = [
    path('release/', api.release_card),
    path('get/balance/<int:card_number>/', api.get_balance),
    path('get/transactions/<int:card_number>/', api.get_transactions),
    path('enroll/<int:card_number>/', api.enroll_money),
    path('write-off/<int:card_number>/', api.write_off_money),
]
