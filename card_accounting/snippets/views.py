# -*- coding: utf-8 -*-

"""Class based api views."""

import json
import socket

from django.http import JsonResponse

SUCCESS_RESPONSE_CODE = 200

METHOD_NOT_ALLOWED_RESPONSE_CODE = 405


class BaseAPIView:
    """API base view class."""

    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
    response_message = 'Everything OK.'

    @classmethod
    def as_view(cls):
        def view(request, *args, **kwargs):
            return cls.validate_request(cls(), request, *args, **kwargs)
        return view

    def validate_request(self, request, *args, **kwargs):
        if request.method not in self.allowed_methods:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            return JsonResponse(
                {'status': 'ERROR',
                 'message': 'Method not allowed',
                 'server_ip': host_ip,
                 },
                status=METHOD_NOT_ALLOWED_RESPONSE_CODE,
            )

        # TODO: refactor
        if request.method == 'PUT':
            request.PUT = json.loads(request.body)

        if request.method == 'DELETE':
            request.DELETE = json.loads(request.body)

        return self.render_to_response(request, *args, **kwargs)

    def render_to_response(self, request, *args, **kwargs):
        data = self.get_data(request)
        return JsonResponse(data, status=SUCCESS_RESPONSE_CODE)

    def get_data(self, request):
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return {
            'status': 'OK',
            'message': self.response_message,
            'server_ip': host_ip,
        }


class CreateAPIView(BaseAPIView):
    """Class view, that create new object."""
    pass  # Add later, steal from django create view


class DetailAPIView(BaseAPIView):
    """Class view, that give information about single object."""

    allowed_methods = ['GET']

    model = None
    queryset = None
    slug = None
    return_fields = '__all__'

    def __init__(self):
        self.object = self.get_object()

    def get_object(self, *args, **kwargs):
        if self.slug is None:
            self.slug = 'pk'
        search_parameter = {self.slug: kwargs[self.slug]}
        if self.model is not None:
            self.queryset = self.model.objects.all()
        return self.queryset.get(**search_parameter)

    def get_data(self, request):
        data = super().get_data(request)
        if self.return_fields == '__all__':
            for key, value in self.object.__dict__.items():  # TODO: watch later
                data[key] = value
        else:
            for object_key, response_key in self.return_fields:
                if response_key == '.':
                    response_key = object_key
                data[response_key] = getattr(self.object, object_key)
        return data


class ListAPIView(BaseAPIView):
    """Class view, that give information about multiple objects."""

    allowed_methods = ['GET']

    model = None
    queryset = None
    model_return_fields = '__all__'
    query_return_name = 'items'

    def __init__(self):
        if self.queryset is None:
            self.queryset = self.get_queryset()

    def get_queryset(self):
        return self.model.objects.all()

    def get_data(self, request):
        data = super().get_data(request)
        items = {}
        if self.model_return_fields == '__all__':
            for instance in self.queryset.values():
                    pk = instance.pop('id')
                    items[pk] = instance
        else:
            # TODO: FIX THIS SHIT
            for instance in self.queryset.values():
                a = {}
                for object_key, response_key in self.model_return_fields:
                    if response_key == '.':
                        response_key = object_key
                    a[response_key] = getattr(instance, object_key)
                items[instance.pk] = a

        data[self.query_return_name] = items
        return data


