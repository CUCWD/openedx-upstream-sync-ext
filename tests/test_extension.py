"""Tests for the upstream synchronization extension."""

import sys
from types import ModuleType, SimpleNamespace

import pytest
from django.test import override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from openedx_upstream_sync_ext.apps import OpenedxUpstreamSyncExtConfig
from openedx_upstream_sync_ext.settings.common import plugin_settings
from openedx_upstream_sync_ext.urls import urlpatterns
from openedx_upstream_sync_ext.views import AuthoringConfigView
from openedx_upstream_sync_ext.xblock_mixins import UpstreamProblemSettingsMixin


def test_plugin_settings_registers_the_problem_mixin():
    """The plugin appends its mixin without removing existing mixins."""
    settings = SimpleNamespace(XBLOCK_EXTRA_MIXINS=('existing.Mixin',))

    plugin_settings(settings)

    assert settings.XBLOCK_EXTRA_MIXINS == (
        'existing.Mixin',
        'openedx_upstream_sync_ext.xblock_mixins.UpstreamProblemSettingsMixin',
    )


def test_plugin_settings_handles_missing_existing_mixins():
    """The settings hook supplies the mixin when no prior value exists."""
    settings = SimpleNamespace()

    plugin_settings(settings)

    assert settings.XBLOCK_EXTRA_MIXINS == (
        'openedx_upstream_sync_ext.xblock_mixins.UpstreamProblemSettingsMixin',
    )


@pytest.mark.parametrize('feature_value', (True, False))
def test_authoring_config_view_returns_feature_flag(feature_value):
    """The API exposes only the supported authoring feature flag."""
    request = APIRequestFactory().get('/api/contentstore/v2/config/')
    force_authenticate(request, user=SimpleNamespace(is_authenticated=True))

    with override_settings(FEATURES={
        'ENABLE_UPSTREAM_SYNC_FOR_CUSTOMIZABLE_FIELDS': feature_value,
        'UNEXPOSED_FEATURE': True,
    }):
        response = AuthoringConfigView.as_view()(request)

    assert response.status_code == 200
    assert response.data == {
        'enable_upstream_sync_for_customizable_fields': feature_value,
    }


def test_authoring_config_view_defaults_when_features_are_missing():
    """The standalone app remains usable without a FEATURES setting."""
    request = APIRequestFactory().get('/api/contentstore/v2/config/')
    force_authenticate(request, user=SimpleNamespace(is_authenticated=True))

    response = AuthoringConfigView.as_view()(request)

    assert response.status_code == 200
    assert response.data == {'enable_upstream_sync_for_customizable_fields': False}


def test_authoring_config_view_requires_authentication():
    """Unauthenticated clients cannot read CMS configuration."""
    request = APIRequestFactory().get('/api/contentstore/v2/config/')

    response = AuthoringConfigView.as_view()(request)

    assert response.status_code == 403


def test_config_url_is_registered():
    """The plugin exposes the config route below its contentstore prefix."""
    assert len(urlpatterns) == 1
    assert urlpatterns[0].name == 'authoring-config'


def test_problem_mixin_defines_upstream_fields():
    """Problem settings have hidden settings-scoped upstream fields."""
    expected_fields = {
        'upstream_weight',
        'upstream_showanswer',
        'upstream_show_reset_button',
        'upstream_submission_wait_seconds',
        'upstream_max_attempts',
    }

    fields = dict(UpstreamProblemSettingsMixin.fields)
    assert expected_fields == set(fields)
    assert all(field.runtime_options['hidden'] for field in fields.values())


def test_ready_leaves_platform_unchanged_when_feature_is_disabled():
    """Installing the plugin does not enable synchronization by itself."""
    config = OpenedxUpstreamSyncExtConfig('openedx_upstream_sync_ext', sys.modules[__name__])

    with override_settings(FEATURES={}):
        config.ready()


def test_ready_adds_problem_fields_and_is_idempotent(monkeypatch):
    """The enabled patch extends the platform mapping only once."""
    cms = ModuleType('cms')
    lib = ModuleType('cms.lib')
    xblock = ModuleType('cms.lib.xblock')
    upstream_sync = ModuleType('cms.lib.xblock.upstream_sync')

    class FakeUpstreamSyncMixin:
        """Minimal stand-in for edx-platform's synchronization mixin."""

        @classmethod
        def get_customizable_fields(cls):
            return {'display_name': 'upstream_display_name', 'weight': None}

    upstream_sync.UpstreamSyncMixin = FakeUpstreamSyncMixin
    cms.lib = lib
    lib.xblock = xblock
    xblock.upstream_sync = upstream_sync
    monkeypatch.setitem(sys.modules, 'cms', cms)
    monkeypatch.setitem(sys.modules, 'cms.lib', lib)
    monkeypatch.setitem(sys.modules, 'cms.lib.xblock', xblock)
    monkeypatch.setitem(sys.modules, 'cms.lib.xblock.upstream_sync', upstream_sync)

    config = OpenedxUpstreamSyncExtConfig('openedx_upstream_sync_ext', sys.modules[__name__])
    with override_settings(FEATURES={'ENABLE_UPSTREAM_SYNC_FOR_CUSTOMIZABLE_FIELDS': True}):
        config.ready()
        patched_fields = FakeUpstreamSyncMixin.get_customizable_fields()
        config.ready()

    assert patched_fields == {
        'display_name': 'upstream_display_name',
        'weight': 'upstream_weight',
        'showanswer': 'upstream_showanswer',
        'show_reset_button': 'upstream_show_reset_button',
        'submission_wait_seconds': 'upstream_submission_wait_seconds',
        'max_attempts': 'upstream_max_attempts',
    }
