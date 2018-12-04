import pytest

from unittest import TestCase

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework import exceptions


from django_mock_queries.query import MockSet, MockModel
from pagination.pagination import WholeTableIdReversePagination


factory = APIRequestFactory()


class TestPagination(TestCase):
    def setUp(self):
        self.pagination = WholeTableIdReversePagination()
        self.queryset  = MockSet()
        for i in range(1, 101):
            self.queryset.add(MockModel(id=i, name='test_object_%s' % i))

    def tearDown(self):
        self.queryset.clear()

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_queryset(self.queryset, request))

    def get_paginated_content(self, queryset):
        response = self.pagination.get_paginated_response(queryset)
        return response.data

    def get_html_context(self):
        return self.pagination.get_html_context()

    def get_page(self, url):
        request = Request(factory.get(url))
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        context = self.get_html_context()
        return queryset, content, context

    def test_invalid_page(self):
        request = Request(factory.get('/', {'page_seek_id': 'xxx'}))
        with pytest.raises(exceptions.NotFound):
            self.paginate_queryset(request)

        request = Request(factory.get('/', {'page_seek_id': '-3'}))
        with pytest.raises(exceptions.NotFound):
            self.paginate_queryset(request)

    def test_first_and_last_page(self):
        # first page
        queryset, content, context = self.get_page('/')

        assert len(queryset) == 20
        assert content['count'] == 20
        assert content['previous'] is None
        assert content['next'] == 'http://testserver/?page_seek_id=80'

        # last page
        queryset, content, context = self.get_page('/?page_seek_id=20')

        assert len(queryset) == 20
        assert content['count'] == 20
        assert content['next'] is None
        assert content['previous'] == 'http://testserver/?page_seek_id=40'

    def test_all_page(self):
        id_list = []
        page_url = '/'
        while(page_url):
            queryset, content, context = self.get_page(page_url)
            for item in content['results']:
                id_list.append(item['id'])

            page_url = content['next']

        id_list = set(id_list)
        assert len(id_list) == 100
