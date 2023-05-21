import logging


class PackagesMeta():
    """
    A collection of different versions of the same package.
    Any command run on a PackagesMeta instance will attempt to run on the latest package. see self.__getattr__
    A PackagesMeta instance is returned by plugget.search()
    """

    def __init__(self):
        self.packages = []

    def __repr__(self):
        return f"PackagesMeta({self.latest.package_name} latest version:'{self.latest.version}')"

    @property
    def latest(self):
        # get latest package
        latest = [p for p in self.packages if p.version == "latest"]
        if latest:
            return latest[0]

        # sort by version
        return sorted(self.packages, key=lambda x: x.version)[0]  # todo semver sort, todo test

    @property
    def versions(self):
        return [x.version for x in self.packages]

    def __getattr__(self, attr):
        """__getattr__ is called when the attr is not found on the instance
        try get the attr from the latest package, e.g. package_meta.install() == package_meta.latest.install()"""
        return getattr(self.latest, attr)

    def get_version(self, version:str) -> "plugget.data.package.Package | None":
        """get package with matching version from self.packages"""
        match = [x for x in self.packages if version == x.version]
        if match:
            return match[0]