"""
Common CMS settings for openedx_upstream_sync_ext.

Open edX imports plugin settings modules independently and calls their
``plugin_settings`` function with the partially built settings module.  The
callback must therefore extend the existing setting rather than referencing
``XBLOCK_EXTRA_MIXINS`` as a module-level variable.
"""


def plugin_settings(settings):
    """Register the hidden upstream-weight XBlock mixin with CMS."""

    # Preserve any mixins supplied by the deployment or another plugin.  The
    # platform later combines this list with its standard XBlock mixins.
    settings.XBLOCK_EXTRA_MIXINS = tuple(getattr(settings, 'XBLOCK_EXTRA_MIXINS', ())) + (
        'openedx_upstream_sync_ext.xblock_mixins.UpstreamProblemSettingsMixin',
    )
