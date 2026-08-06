# openedx-upstream-sync-ext

An Open edX CMS Django plugin that extends Library upstream synchronization
for customizable Problem settings.

When enabled, the plugin lets course authors pull selected Problem settings
from a Library component while preserving course-level customizations. It also
exposes the feature state to `frontend-app-authoring` so the corresponding
Library editing controls can be shown only when the CMS supports them.

## Supported settings

The plugin tracks these upstream values on downstream Problem blocks:

- `weight`
- `showanswer`
- `show_reset_button`
- `submission_wait_seconds`
- `max_attempts`

Each setting is backed by a hidden `upstream_*` XBlock field. These fields
record the last fetched Library value so upstream synchronization can tell
whether a downstream value was changed locally.

## Installation

Install the package into the Open edX environment used by the CMS:

```bash
pip install openedx-upstream-sync-ext
```

The plugin is CMS-only. It registers through the `cms.djangoapp` entry point
and does not need to be installed in LMS.

## Configuration

Enable the feature in the CMS Django settings:

```python
FEATURES['ENABLE_UPSTREAM_SYNC_FOR_CUSTOMIZABLE_FIELDS'] = True
```

The default is `False`, so installing the plugin alone does not change
upstream synchronization behavior.

## Frontend configuration endpoint

The plugin provides an authenticated CMS endpoint:

```text
GET /api/contentstore/v2/config/
```

Example response:

```json
{
  "enable_upstream_sync_for_customizable_fields": true
}
```

`frontend-app-authoring` uses this value to show the scoring, show-answer,
reset, and timer settings for Library Problems. Course Problems retain their
normal editing behavior.

## Development

Run the test suite and quality checks with:

```bash
pytest
make quality
```

The package supports Python 3.11 and newer, Django 4.2, and Django 5.2.
