"""
Plugget data container classes

- an app contains multiple packages (PackagesMeta)
- a package contains multiple manifests (Package), 1 for each version of the package
"""

from plugget.data.package import Package
from plugget.data.packages_meta import PackagesMeta
# todo rename data to types t obe more clear, see docstring above
