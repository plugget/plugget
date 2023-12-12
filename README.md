<h1>
<img src="https://user-images.githubusercontent.com/3758308/231004489-25ce30d9-c534-4d10-8773-8e6f80f36dd2.png" data-canonical-src="https://user-images.githubusercontent.com/3758308/231004489-25ce30d9-c534-4d10-8773-8e6f80f36dd2.png" width="70" />
Plugget: Plugin Package Manager
</h1>

[![PyPI Downloads](https://img.shields.io/pypi/v/plugget?color=0)](https://pypi.org/project/plugget/)

Install app packages (plugins, addons, icons, ...) from a repo with a single Python command:   
(like pip, but more flexible)  
```python
import plugget
plugget.install("my_package")
```

![machinetoolsinstall](https://user-images.githubusercontent.com/3758308/227316999-adf32b7f-4232-46f5-b0db-1b3dbe26d755.gif)

also check out  
🔹 [Plugget Qt](https://github.com/plugget/plugget-qt)  
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/59059d9d1a2c092696dc66e00931cc1181a4ce1f/icons/UnrealEngine.svg" width="32" style="max-width: 100%;"> [Plugget Qt Unreal plugin](https://github.com/plugget/plugget-unreal)  
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/59059d9d1a2c092696dc66e00931cc1181a4ce1f/icons/Blender-Dark.svg" width="32" style="max-width: 100%;"> [Plugget Qt Blender addon](https://github.com/plugget/plugget-qt-addon) (more features)  
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/59059d9d1a2c092696dc66e00931cc1181a4ce1f/icons/Blender-Dark.svg" width="32" style="max-width: 100%;"> [Plugget Blender addon](https://github.com/plugget/plugget-blender-addon) (simple)  
🔹 [plugget manifest repo](https://github.com/plugget/plugget-pkgs)
- [plugget-qt-maya-plugin](https://github.com/plugget/plugget-qt-maya-plugin) A Maya plugin that launches the Plugget Qt UI window

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

## issues
If the install fails. It likely is a bad manifest, a bad install, or a bug with Plugget.
Report the issue in issues.
There's a small chance the GitHub servers are down, you can check the [github status](https://www.githubstatus.com/).


## community
- Pipeline https://discourse.techart.online/t/plugget-package-manager-for-tech-artists/16301
- Blender https://blenderartists.org/t/free-plugget-a-search-engine-installer-for-add-ons/1456558
- Maya https://forums.cgsociety.org/t/plugget-a-free-maya-tool-manager/2074249


If this tool is helpfull, you can ⭐ star it on the github page, just click the ⭐ star button in the top-right of this page.

![](https://linuxsimply.com/wp-content/uploads/2023/08/Package-manager-767x438.png)
![](https://geekflare.com/wp-content/uploads/2023/09/6-how-package-manager-works.png)
