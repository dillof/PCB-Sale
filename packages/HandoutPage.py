import md2typst
import re

from .Page import Page
from .Systems import Systems


class HandoutPage:
    def __init__(self, page: Page):
        self.page = page

    def write(self, file):
        print("#block(breakable: false)[", file=file)
        print(f"== {self.page.directory}", file=file)

        if self.page.description is not None:
            print(f"=== {self.page.description}", file=file)

        print("", file=file)
        if self.page.tested_description is not None:
            print(md2typst.convert(self.page.tested_description), file=file)
            print("", file=file)

        if len(self.page.photos) > 0:
            for photo in self.page.photos:
                print("#box(\nheight: 100pt,", file=file)
                print(f"image(\"{self.page.directory}/{photo.file}\"),", file=file)
                print(")", file=file)
            print("", file=file)

        if len(self.page.content) > 0:
            for line in self.page.content:
                text = md2typst.convert(line)
                print(f"{text}\n", file=file)
            print("", file=file)

        print("]", file=file)

        for components_name in self.page.components_names:
            #print("#block(breakable: false)[", file=file)
            components = self.page.components[components_name]
            if components_name:
                print(f"=== {components_name}", file=file)
            print("#{show table.cell: set text(size: 9pt)\ntable(\ncolumns: (auto, auto),\ntable.header([*Komponente*], [*Anzahl*]),\n", file=file)

            for component in sorted(components):
                print(f"[{component.name()}], [{component.amount}],", file=file)

            print(")}", file=file)
            #print("]", file=file)

        print("\n", file=file)