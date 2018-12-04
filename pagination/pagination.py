from collections import OrderedDict

from django.db.models import Max
from django.template import loader
from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.utils.urls import replace_query_param


class WholeTableIdReversePagination(object):
    """全表id倒序分页"""
    display_page_controls = False
    page_size = 20

    page_query_param = 'page_seek_id'
    page_query_description = _('A page query seek id.')

    invalid_page_seek_message = _('Invalid page seek id')

    template = 'rest_framework/pagination/previous_and_next.html'

    def get_page_seek_id(self, request, max_id):
        page_seek_id = request.query_params.get(self.page_query_param)

        if page_seek_id is None:
            page_seek_id = max_id
        elif page_seek_id.isdigit() is False:
            raise NotFound('Invalid page seek id, the parameter page_seek_id must be a numeric type')
        else:
            page_seek_id = int(page_seek_id)
            if page_seek_id <= 0:
                raise NotFound('Invalid page seek id, the parameter page_seek_id must be greater than 0')

        return page_seek_id

    def paginate_queryset(self, queryset, request, view=None):
        #assert hasattr(queryset.model, 'id'), 'The model must contain a primary key with a name `id`'
        # 最大id（伪数据量）
        self.max_id = queryset.aggregate(max_id=Max('id')).get('max_id')
        if self.max_id is None:
            return list(queryset)

        page_seek_id = self.get_page_seek_id(request, self.max_id)

        page_size = self.page_size

        if page_seek_id <= self.page_size:
            query_start_id = 0
            page_size = page_seek_id
        else:
            query_start_id = page_seek_id - self.page_size

        result = queryset.filter(id__gt=query_start_id).order_by('id')[0: page_size]
        result = list(result)
        result.reverse()

        self.request = request
        self.page_seek_id = page_seek_id

        return result

    def get_paginated_response(self, data):
        self.set_next_and_previous_link(data)

        return Response(OrderedDict([
            ('count', len(data)),
            ('next', self.next_link),
            ('previous', self.previous_link),
            ('results', data)
        ]))

    def set_next_and_previous_link(self, data):
        # 无上下页：数据为空或总数据量小于1页的情况
        if not data or self.max_id <= self.page_size:
            self.next_link = None
            self.previous_link = None
        else:
            if self.max_id == data[0]['id']:
                self.previous_link = None
            else:
                self.previous_link = self.get_previous_link(data)

            if self.page_seek_id <= self.page_size:
                self.next_link = None
            else:
                self.next_link = self.get_next_link(data)

    def get_next_link(self, data):
        url = self.request.build_absolute_uri()
        page_seek_id = data[-1]['id'] - 1
        return replace_query_param(url, self.page_query_param, page_seek_id)

    def get_previous_link(self, data):
        url = self.request.build_absolute_uri()
        page_seek_id = data[0]['id'] + self.page_size
        return replace_query_param(url, self.page_query_param, page_seek_id)

    def get_html_context(self):
        return {
            'previous_url': self.previous_link,
            'next_url': self.next_link
        }

    def to_html(self):
        template = loader.get_template(self.template)
        context = self.get_html_context()
        return template.render(context)

    def get_results(self, data):
        return data['results']

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        fields = [
            coreapi.Field(
                name=self.page_query_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title='Whole table id reverse pagination',
                    description=force_text(self.page_query_description)
                )
            )
        ]

        return fields
