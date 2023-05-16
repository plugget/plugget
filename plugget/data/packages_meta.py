

class PackagesMeta():

    def __init__(self):
        self.packages = []

    @property
    def latest(self):
        # todo get latest package


        return

    def __getattr__(self, attr):
        """__getattr__ is called when the attr is not found on the instance
        try get the attr from the latest package, e.g. package_meta.install() == package_meta.latest.install()"""
        result = getattr(self.latest, attr)
        setattr(self.caller, attr, result)

    # inherit the commands from package
    # e.g. install: installs the latest version of the collection

    # also add extra versions, return all versions
