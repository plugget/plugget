"""
This is a template for a plugget action.  It is not intended to be used
try writing the (un)install method in pure python, so it also runs outside the app
methods:
    install
    uninstall
    enable
    disable
"""


# todo make install uninstall optional too, when provided a target dir. e.g. plugin or icon folder for an app
def install(package: "plugget.data.Package", **kwargs):
    # ideally install moves files to a folder
    pass


def uninstall(package: "plugget.data.Package", **kwargs):
    # this method runs on uninstall, then the manifest is removed from installed packages
    # ideally uninstall removes files from a folder,
    pass


# enable and disable are optional
# enable disable might run setup/tear down methods in the app. but not if run from outside the app?
# for now ignore this and focus on install uninstall
def enable(package: "plugget.data.Package", **kwargs):
    # this method runs on enable
    # ideally enable moves files to a folder from the plugget cache
    # then refreshes the plugins in the app, to ensure the plugin is loaded
    # plugin might need ro run a setup/register/... method when enabled in app
    pass


def disable(package: "plugget.data.Package", **kwargs):
    # this method runs on disable, the manifest is kept in installed packages
    # ideally disable removes files from a folder, but keeps them in plugget cache
    # plugin might need disabling in app first, to allow moving
    # plugin might also need to run a teardown/unregister/... method when disabled in app
    pass
