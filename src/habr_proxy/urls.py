from django.urls import re_path

from habr_proxy.views import ProxyView, AssetsProxyView, ApiCallsProxyView, EffectProxyView

urlpatterns = [
    re_path(r'^assets/.*$', AssetsProxyView.as_view()),
    re_path(r'^kek/.*$', ApiCallsProxyView.as_view()),
    re_path(r'^js/.*$', ApiCallsProxyView.as_view()),
    re_path(r'^effect/.*$', EffectProxyView.as_view()),
    re_path(r'^.*$', ProxyView.as_view()),
]
