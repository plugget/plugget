# PlugGet
Install app packages (plugins, addons, icons, ...) from a repo with a single Python command: 
```python
import plugget
plugget.install("my_package")
```

![machinetoolsinstall](https://user-images.githubusercontent.com/3758308/227316999-adf32b7f-4232-46f5-b0db-1b3dbe26d755.gif)


## requirements
- pip installed
- git installed
(aim to auto handle requirements in future)

## not to confuse with 
- [PluGeth](https://github.com/openrelayxyz/plugeth) The extensible Geth fork, ethereum, golang
- [pluGET](https://github.com/Neocky/pluGET) A package manager to update minecraft server plugin & software


## package manager comparison
PyPi installs only packaged python modules. 
Plugget supports other languages, e.g. Maxscript, and links to unpackaged repos.

WinGet, chocolatey, etc. install apps, Plugget installs plugins for apps.

## manifest repo
- package manifests live in the [manifest repo](https://github.com/hannesdelbeke/plugget-pkgs)
