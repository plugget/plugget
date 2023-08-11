import logging


class PackagesMeta:
    """
    A collection of different versions of the same package.
    Any command run on a PackagesMeta instance will attempt to run on the latest package. see self.__getattr__
    A PackagesMeta instance is returned by plugget.search()
    """
    def __init__(self, manifests_dir):
        self._packages_cache: "typing.Dict[str, plugget.data.package.Package]" = {}
        self.manifests_dir: "pathlib.Path" = manifests_dir
        # self.manifest_dirs is expected to be set externally,
        # self.manifest_dirs is not included in init so we can first build it up in a loop
        from plugget.data.package import Package

        self.manifests = list(self.manifests_dir.glob("*.json"))
        self.packages = [Package.from_json(manifest) for manifest in self.manifests]
        for package in self.packages:
            package.packages_meta = self

    def __repr__(self):
        if self.installed_package:
            msg = f"installed version:'{self.installed_package.version}'"
        else:
            msg = f"not installed"
        return f"PackagesMeta({self.latest.package_name} {msg})"

    @property
    def latest(self) -> "plugget.data.package.Package":
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
    def installed_packages(self) -> "typing.List[plugget.data.package.Package]":
        return [x for x in self.packages if x.is_installed]

    @property
    def installed_package(self) -> "plugget.data.package.Package | None":
        """get installed package from self.packages"""
        # you shouldn't have multiple package versions installed in the same app
        # if 'my_package' is installed in both Blender 3.2 & 3.3, they'll have separate PackageMeta instances
        packages = self.installed_packages
        if len(packages) > 1:
            logging.warning(f"multiple versions of {self.package_name} installed: {packages}")
        if packages:
            return packages[0]

    # is installed. any(x.is_installed for x in meta_packages.packages)
    # but think of UX, if dev thinks its installed and then gets an attr, through __getattr__
    # it ll return attrs from the latest version, which might not be the one installed
    # but e.g. requesting name, should work even if not installed
    # todo handle better, remove attr get method

    def uninstall(self, dependencies=False, **kwargs):
        """uninstall latest package"""
        for p in self.installed_packages:
            p.uninstall(dependencies=dependencies, **kwargs)