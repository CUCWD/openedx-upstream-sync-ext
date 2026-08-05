"""
Extends Open edX upstream synchronization to support configurable customizable fields, including synchronizing Library component values such as problem scores.

The package is installed as a CMS Django plugin.  It intentionally keeps the
feature behind a Django ``FEATURES`` flag so deployments can install the
package without changing synchronization behavior until they explicitly opt
in.
"""

__version__ = '0.1.0'
