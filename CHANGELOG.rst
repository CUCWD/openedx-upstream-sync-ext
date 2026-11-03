Change Log
##########

..
   All enhancements and patches to openedx_upstream_sync_ext will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

0.1.2 – 2026-11-03
******************

Changed
========

* Defer runtime dependency versions to the host Ulmo edx-platform installation
  and move openedx-atlas to development tooling.
* Replace runtime and test lockfiles with references to their input files,
  preserving those references during requirement compilation and upgrades.
* Replace remote common constraints with a local Ulmo snapshot and regenerate
  development, quality, documentation, and installer dependency locks.
* Use Django 5.2.11 and XBlock 5.2.0 for Ulmo checks, retaining Django 4.2
  compatibility coverage and Python 3.12-compatible style checks.
* Install committed dependency locks in CI instead of recompiling them on each
  run, report every matrix result, and upload coverage from the Ulmo test job.

0.1.0 – 2026-08-05
**********************************************

Added
=====

* First release on PyPI.
