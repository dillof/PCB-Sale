import glob
from pathlib import Path

from .Components import Components
from .IndexPage import IndexPage
from .Page import Page
from .Systems import Systems

ignored_directories = [
    "django",
    "orders",
    "packages"
]

class Site:
    def __init__(self):
        self.components = Components()
        self.systems = Systems()
        self.index_pages = {}

        self.parse()

    def parse(self):
        for file in glob.glob("*.md"):
            name = file.replace(".md", "")
            self.index_pages[name] = IndexPage(name, self.systems)

        for directory in [d.name for d in Path(".").iterdir() if d.is_dir()]:
            if directory.startswith(".") or directory in ignored_directories:
                continue

            Page(directory, self)

    def write(self):
        self.components.write()

        for index_page in self.index_pages.values():
            index_page.write()
            for page in index_page.all_pages():
                page.write()
