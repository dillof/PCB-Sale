import md2typst
import re

from .Page import Page
from .Systems import Systems


class HandoutPage:
    def __init__(self, page: Page):
        self.page = page

    def write(self, file):
        print("#pagebreak(weak: true)", file=file)
        print("#block(breakable: false)[", file=file)
        print(f"== {self.page.title}", file=file)

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

        pcb_price = self.page.pcb_price()
        if pcb_price is not None:
            if pcb_price != int(pcb_price):
                pcb_price = f"{pcb_price:.2f}"
            else:
                pcb_price = f"{int(pcb_price)}"
            print(f"Preis: *€{pcb_price}*\n", file=file)

        print("]", file=file)

        if len(self.page.components_names) > 0:
            print("#columns(2, gutter: 8pt)[", file=file)
            for components_name in self.page.components_names:
                #print("#block(breakable: false)[", file=file)
                components = self.page.components[components_name]
                if components_name:
                    print(f"=== {components_name}", file=file)
                print("#{set text(size: 8pt)\ntable(\nalign: (left, center),\nstroke: none,\nfill: (col, row) => if type(row) == int and row > 0 and calc.rem(row, 2) == 1 {luma(240)} else {none},\ncolumns: (auto, auto),\ntable.header([*Komponente*], [*Anzahl*]),\n", file=file)

                for component in sorted(components):
                    print(f"[{component.name()}], [{component.amount}],", file=file)

                print(")}", file=file)
                #print("]", file=file)
            print("]", file=file)

        print("\n", file=file)

    def sort_keys(self, sorted_systems):
        for system_index, system in enumerate(sorted_systems):
            if system in self.page.systems:
                return (system_index, self.page.systems[system], self.page.directory)
        return(999, 999, self.page.directory)
