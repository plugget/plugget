def install(package: "plugget.data.Package", **kwargs):
    import subprocess
    proc = subprocess.Popen(package.action_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def uninstall(package: "plugget.data.Package", **kwargs):
    # this method runs on uninstall, then the manifest is removed from installed packages
    # ideally uninstall removes files from a folder,
    pass
