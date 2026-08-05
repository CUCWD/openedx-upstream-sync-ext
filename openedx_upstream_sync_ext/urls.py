"""CMS API URLs for openedx_upstream_sync_ext."""

from django.urls import path

from .views import AuthoringConfigView

urlpatterns = [
    # The plugin framework mounts this module below
    # ``/api/contentstore/v2/``.  The final URL is therefore
    # ``/api/contentstore/v2/config/``.
    path('config/', AuthoringConfigView.as_view(), name='authoring-config'),
]
