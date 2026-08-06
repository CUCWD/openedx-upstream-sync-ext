"""
openedx_upstream_sync_ext Django application initialization.
"""

import logging

from django.apps import AppConfig
from django.conf import settings
from edx_django_utils.plugins import PluginSettings, PluginURLs

try:
    from openedx.core.djangoapps.plugins.constants import ProjectType, SettingsType
except ModuleNotFoundError:
    # The real constants are supplied by edx-platform.  The fallback keeps the
    # package's standalone Django tests usable without installing all of
    # edx-platform; the values are the same strings used by its plugin loader.
    class ProjectType:
        """Open edX project type values used by the plugin framework."""

        CMS = 'cms.djangoapp'

    class SettingsType:
        """Open edX settings type values used by the plugin framework."""

        COMMON = 'common'


LOGGER = logging.getLogger(__name__)


class OpenedxUpstreamSyncExtConfig(AppConfig):
    """
    Configuration for the openedx_upstream_sync_ext Django application.
    """

    name = 'openedx_upstream_sync_ext'
    label = 'openedx_upstream_sync_ext'
    verbose_name = 'Open edX Upstream Sync Extensions'

    # Tell edx-platform that this app contributes both URL patterns and common
    # CMS settings.  The URL prefix is deliberately scoped to contentstore so
    # the frontend can use the same authenticated CMS origin as other
    # authoring APIs.
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.CMS: {
                PluginURLs.NAMESPACE: 'openedx_upstream_sync_ext',
                PluginURLs.REGEX: r'^api/contentstore/v2/',
                PluginURLs.RELATIVE_PATH: 'urls',
            },
        },
        PluginSettings.CONFIG: {
            ProjectType.CMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: 'settings.common',
                },
            },
        },
    }

    def ready(self):
        """
        Log initialization and enable the optional upstream-sync extension.

        ``ready`` runs after Django has loaded the application registry and
        settings, which is the first safe point for importing CMS's
        ``UpstreamSyncMixin``.  The feature flag is checked here rather than
        at module import time so deployments can override it through Tutor or
        another settings layer.

        The plugin patches only the mapping returned by
        ``get_customizable_fields``.  Open edX retains responsibility for the
        synchronization algorithm itself; when enabled, the supported Problem
        settings point to hidden ``upstream_*`` fields supplied by
        ``UpstreamProblemSettingsMixin``.
        """
        LOGGER.info("openedx_upstream_sync_ext application is ready")

        # The default is false so installing the plugin alone is not enough to
        # alter existing course behavior.
        feature_flags = getattr(settings, 'FEATURES', {})
        if not feature_flags.get('ENABLE_UPSTREAM_SYNC_FOR_CUSTOMIZABLE_FIELDS', False):
            return

        # Import lazily: this package can be tested as a normal Django app,
        # while the CMS-only dependency exists only in an Open edX runtime.
        from cms.lib.xblock.upstream_sync import (  # pylint: disable=import-error,import-outside-toplevel
            UpstreamSyncMixin,
        )

        # Save the method currently installed by edx-platform.  We call this
        # saved method from the wrapper below so the platform's existing field
        # mapping is preserved.
        original_get_customizable_fields = UpstreamSyncMixin.get_customizable_fields

        # Django's development autoreloader can initialize applications more
        # than once.  The wrapper is marked below after the first patch; if we
        # encounter that marked wrapper again, stop before wrapping it a second
        # time.  Otherwise repeated initialization could produce nested
        # wrappers such as wrapper -> wrapper -> original method.
        if getattr(original_get_customizable_fields, '_openedx_upstream_sync_ext', False):
            return

        def get_customizable_fields(_cls):
            # Start with the platform's current mapping so future upstream
            # fields remain intact and this plugin only changes the fields it
            # explicitly supports.
            fields = original_get_customizable_fields()

            # A non-None value tells Open edX which hidden downstream field
            # stores the last fetched library value.  Those stored values are
            # required to distinguish untouched course values from local
            # customizations during later upstream syncs.
            fields.update({
                'weight': 'upstream_weight',
                'showanswer': 'upstream_showanswer',
                'show_reset_button': 'upstream_show_reset_button',
                'submission_wait_seconds': 'upstream_submission_wait_seconds',
                'max_attempts': 'upstream_max_attempts',
            })
            return fields

        # Mark the replacement function so a later ready() call can recognize
        # that this plugin has already patched the platform method.
        marker_name = '_openedx_upstream_sync_ext'
        setattr(get_customizable_fields, marker_name, True)
        UpstreamSyncMixin.get_customizable_fields = classmethod(get_customizable_fields)
