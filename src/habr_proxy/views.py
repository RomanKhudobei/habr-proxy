import json
import logging

import requests
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, JsonResponse
from django.views import View

from habr_proxy.user_agent import get_default_user_agent_provider
from habr_proxy.utils import insert_tm_into_html, insert_tm_into_dicts

logger = logging.getLogger('default')


class BaseProxyView(View):
    origin_base_url = None

    def get(self, request, *args, **kwargs):
        origin_base_url = self.get_origin_base_url()
        path = self.get_request_full_path()

        response = requests.get(f'{origin_base_url}{path}', headers={
            'User-Agent': get_default_user_agent_provider().get_user_agent(),
        })

        return self.process_response(response)

    def request_origin(self):
        origin_base_url = self.get_origin_base_url()
        path = self.get_request_full_path()

        return requests.get(f'{origin_base_url}{path}', headers={
            'User-Agent': get_default_user_agent_provider().get_user_agent(),
        })

    def get_origin_base_url(self):
        if self.origin_base_url is None:
            raise ImproperlyConfigured('"origin_base_url" attribute must be set for proxy view')

        return self.origin_base_url

    def get_request_full_path(self):
        return self.request.get_full_path()

    def process_response(self, response: requests.Response) -> HttpResponse:
        content_type = response.headers.get('content-type')
        return HttpResponse(response.text, content_type=content_type)


class ProxyView(BaseProxyView):
    origin_base_url = 'https://habr.com'

    def process_response(self, response):
        response_text = response.text
        content_type = response.headers['content-type']

        if 'text/html' in content_type and '.svg' not in self.get_request_full_path():
            response_text = insert_tm_into_html(response_text)

        response_text = response_text.replace('https://habr.com', 'http://127.0.0.1:8000')
        response_text = response_text.replace('https://assets.habr.com', 'http://127.0.0.1:8000/assets')
        return HttpResponse(response_text, content_type=content_type)


class AssetsProxyView(BaseProxyView):
    origin_base_url = 'https://assets.habr.com'

    def process_response(self, response):
        response_text = response.text

        content_type = response.headers['content-type']
        if 'application/javascript' in content_type:
            response_text = response_text.replace('https://habr.com', 'http://127.0.0.1:8000')
            response_text = response_text.replace('https://assets.habr.com', 'http://127.0.0.1:8000/assets')
            response_text = response_text.replace('https://effect.habr.com', 'http://127.0.0.1:8000/effect')

        if 'image' in content_type:
            response_text = response.content

        return HttpResponse(response_text, content_type=content_type)

    def get_request_full_path(self):
        path = self.request.get_full_path()
        return '/' + '/'.join(path.strip('/').split('/')[1:])  # remove /assets/ part


class ApiCallsProxyView(BaseProxyView):
    origin_base_url = 'https://habr.com'

    def process_response(self, response):
        content_type = response.headers['content-type']

        if 'application/json' in content_type:
            json_data = response.json()
            json_data = insert_tm_into_dicts(json_data)
            return JsonResponse(json_data, content_type=content_type)

        return HttpResponse(response.text, content_type=content_type)


class EffectProxyView(BaseProxyView):
    origin_base_url = 'https://effect.habr.com'

    def get_request_full_path(self):
        path = self.request.get_full_path()
        return '/' + '/'.join(path.strip('/').split('/')[1:])  # remove /effect/ part

    def process_response(self, response):
        content_type = response.headers['content-type']

        if 'application/json' in content_type:
            json_data = response.json()
            json_data = insert_tm_into_dicts(json_data)
            response_text = json.dumps(json_data)
            response_text = response_text.replace('https://effect.habr.com', 'http://127.0.0.1:8000/effect')

        else:
            # for some reason received binary html
            try:
                response_text = response.content.decode()
            except:
                response_text = response.text

            if 'text/html' in content_type and '.svg' not in self.get_request_full_path():
                response_text = insert_tm_into_html(response_text)

                with open('page-modified.html', 'w') as f:
                    f.write(response_text)

                with open('page.html', 'w') as f:
                    f.write(response.content.decode())

            response_text = response_text.replace('https://habr.com', 'http://127.0.0.1:8000')
            response_text = response_text.replace('https://assets.habr.com', 'http://127.0.0.1:8000/assets')

        return HttpResponse(response_text, content_type=content_type)
