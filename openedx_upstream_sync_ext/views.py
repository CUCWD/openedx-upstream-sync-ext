"""CMS API views for openedx_upstream_sync_ext."""

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class AuthoringConfigView(APIView):
    """
    Expose whitelisted upstream-sync configuration to authoring clients.

    This endpoint intentionally returns one explicit value instead of exposing
    the complete Django ``FEATURES`` dictionary.  The frontend uses the value
    to align its authoring UI with the CMS behavior, while the CMS remains the
    authority that performs synchronization.
    """

    # Configuration can affect authoring behavior and should be visible only
    # to authenticated CMS users, just like the other contentstore APIs.
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return configuration needed by frontend-app-authoring.

        ``FEATURES`` may be absent in the standalone test settings used by
        this package, so use ``get`` with a false default for portability.
        """
        return Response({
            'enable_upstream_sync_for_customizable_fields': settings.FEATURES.get(
                'ENABLE_UPSTREAM_SYNC_FOR_CUSTOMIZABLE_FIELDS',
                False,
            ),
        })
