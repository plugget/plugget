

class PackagesMeta():

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

    # inherit the commands from package
    # e.g. install: installs the latest version of the collection

    # also add extra versions, return all versions
