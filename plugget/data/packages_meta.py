import logging


class PackagesMeta():
    """
    A collection of different versions of the same package.
    Any command run on a PackagesMeta instance will attempt to run on the latest package. see self.__getattr__
    A PackagesMeta instance is returned by plugget.search()
    """

    def __init__(self):
        self.packages: "list(plugget.data.package.Package)" = []

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
        # todo remove this method later, will break lots of things though
        return getattr(self.latest, attr)

    def get_version(self, version: str) -> "plugget.data.package.Package | None":
        """get package with matching version from self.packages"""
        match = [x for x in self.packages if version == x.version]
        if match:
            return match[0]

    @property
    def installed_package(self) -> "plugget.data.package.Package | None":
        """get installed package from self.packages"""
        # todo how does this handle multiple versions of the same package?
        # todo how does it handle same package installed in diff versions of blender?
        match = [x for x in self.packages if x.is_installed]

        if len(match) > 1:
            logging.warning(f"multiple versions of {self.package_name} installed: {match}")

        if match:
            return match[0]

    # is installed. any(x.is_installed for x in meta_packages.packages)
    # but think of UX, if dev thinks its installed and then gets an attr, through __getattr__
    # it ll return attrs from the latest version, which might not be the one installed