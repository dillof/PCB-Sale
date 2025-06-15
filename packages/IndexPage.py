import functools
import os
import re

from packages.HTMLWriter import HTMLWriter
from packages.Messages import messages

preamble_field_pattern = r"^(\S+):\s*(.*)$"

class IndexPage:
    def __init__(self, name, systems):
        self.name = name
        self.title = name
        self.systems = systems
        self.categories = {}
        self.pages = {}
        self.content = []
        self.parse()
    
    def parse(self):
        filename = f"{self.name}.md"
        if not os.path.exists(filename):
            messages.error(f"no file '{filename}'")
            return

        with open(filename, "r") as file:
            in_preamble = True

            for (line_number, line) in enumerate(file):
                line = line.rstrip()

                if in_preamble:
                    if not line or line[0] == "#":
                        continue
                    if line == "---":
                        in_preamble = False
                    else:
                        match = re.search(preamble_field_pattern, line)
                        if match:
                            field = match.group(1)
                            if field == "title":
                                self.title = match.group(2)
                            else:
                                messages.error(f"Invalid preamble field '{field}'", filename, line_number)
                        else:
                            messages.error(f"Invalid line in preamble: '{line}'", filename, line_number)
                else:
                    self.content.append(line)
    
    def add_page(self, page):
        for system in page.systems:
            if not self.systems.has_system:
                raise RuntimeError(f"unknown system '{system}'")
            if system not in self.pages:
                self.pages[system] = []
            self.pages[system].append(page)
            self.categories[self.systems.category_of(system)] = True

    def has_category(self, category):
        return category in self.categories
    
    def all_pages(self):
        all_pages = []
        for pages in self.pages.values():
            all_pages += pages
        return all_pages

    def write(self):
        writer = HTMLWriter(f"{self.name}.html", self.title)
        writer.markdown(self.content)
        for category in self.systems.category_list:
            if not self.has_category(category):
                continue

            writer.tag("h2", category, {"class": "system-category"}, True)
            for system in self.systems.categories[category]:
                if system not in self.pages:
                    continue

                writer.tag("h3", system, {"class":"system"}, True)
                writer.open("div", {"class":"links"}, newline=True)
                sorted_pages = sorted(self.pages[system], key=functools.cmp_to_key(lambda a, b: a.compare_system_list(b, system)))
                for page in sorted_pages:
                    writer.link(f"{page.directory}/")
                    writer.open("span")
                    if len(page.photos) > 0:
                        writer.image(f"{page.directory}/{page.photos[0].file}")
                    writer.close()
                    writer.tag("span", page.link_title(system))
                    writer.close(newline=True)
                writer.close(newline=True)
