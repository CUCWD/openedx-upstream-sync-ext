"""
XBlock mixins provided by the upstream synchronization extension.

The mixin is added through ``XBLOCK_EXTRA_MIXINS`` by the plugin's common
settings module.  It is separate from the method override so the XBlock fields
are available on every CMS-created course block before synchronization tries
to read or write them.
"""

from xblock.core import XBlockMixin
from xblock.fields import Boolean, Float, Integer, Scope, String


class UpstreamProblemSettingsMixin(XBlockMixin):
    """
    Store the last fetched upstream values for supported Problem settings.

    Open edX's beta synchronization logic uses hidden ``upstream_*`` fields to
    remember published Library values.  On the next sync it compares each
    remembered value with the course value, preserving a course-level override
    when they differ.

    The field types intentionally match the corresponding XBlock settings:

    * ``weight`` and ``submission_wait_seconds`` are numeric values;
    * ``max_attempts`` is an integer value;
    * ``showanswer`` is a string enum;
    * ``show_reset_button`` is a boolean value.
    """

    # These are settings-scoped fields because they belong to the course-side
    # XBlock instance, not to learner state or problem content.  ``None`` is
    # used until the first upstream value is fetched.
    upstream_weight = Float(
        help="The value of weight on the linked upstream block.",
        default=None,
        scope=Scope.settings,
        hidden=True,
        enforce_type=True,
    )

    upstream_showanswer = String(
        help="The value of showanswer on the linked upstream block.",
        default=None,
        scope=Scope.settings,
        hidden=True,
        enforce_type=True,
    )

    upstream_show_reset_button = Boolean(
        help="The value of show_reset_button on the linked upstream block.",
        default=None,
        scope=Scope.settings,
        hidden=True,
        enforce_type=True,
    )

    upstream_submission_wait_seconds = Integer(
        help="The value of submission_wait_seconds on the linked upstream block.",
        default=None,
        scope=Scope.settings,
        hidden=True,
        enforce_type=True,
    )

    upstream_max_attempts = Integer(
        help="The value of max_attempts on the linked upstream block.",
        default=None,
        scope=Scope.settings,
        hidden=True,
        enforce_type=True,
    )
