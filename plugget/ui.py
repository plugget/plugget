import os
import subprocess
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from functools import partial
from pathlib import Path
import shutil


class GitCloneWidget(QWidget):
    def __init__(self, repo_list):
        super().__init__()
        self.repo_list = repo_list
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Git Clone Widget")
        self.layout = QVBoxLayout()

        for repo_url in self.repo_list:
            # Create a new button for each repo
            button = QPushButton(f"Clone {repo_url}")
            button.clicked.connect(partial(self.clone_repo, repo_url=repo_url))
            self.layout.addWidget(button)

        self.setLayout(self.layout)

    def clone_repo(self, repo_url):
        temp_folder = str( Path(os.getenv("TEMP")) / "pluginmanager")
        # delete folder on windows
        if os.path.exists(temp_folder):
            # remove fodler and all content
            os.system(f"rmdir /s /q {temp_folder}")
        subprocess.run(["git", "clone", "--depth", "1", "--single-branch", "--progress", "--recursive", repo_url, temp_folder])
        print(f"Cloned {repo_url} to {temp_folder}")

        # todo , get path / subdirectory from url and sparse checkout see https://medium.com/@marcoscannabrava/git-download-a-repositorys-specific-subfolder-ceeabc6023e2


if __name__ == "__main__":
    app = QApplication([])
    repo_list = ["https://github.com/techartorg/bqt",
                 "https://github.com/user/repo2.git",
                 "https://github.com/user/repo3.git",
                 ]
    widget = GitCloneWidget(repo_list)
    widget.show()
    app.exec_()