import enum
import glob
import os
import re
import sys

from packages.Link import Link
from packages.Messages import messages
from packages.Part import Part
from packages.Photo import Photo

from . import HTMLWriter

component_pattern = r"^\s*([-.0-9]+)\s+(.*?)(€([-0-9.]+))?$"
link_pattern = r"^\s*(.*?)(:(.*))?$"
page_system_pattern =r"^\s*([^|]*)(\|(.*))?$"
photo_pattern = r"^\s*([^:]*):\s+(.*)$"
preamble_field_pattern = r"^(\S+):\s*(.*)$"

class State(enum.Enum):
    COMPONENTS = "components"
    CONTENT = "content"
    LINKS = "links"
    PHOTOS = "photos"
    PREAMBLE = "preamble"
    SYSTEMS = "systems"

class Tested(enum.Enum):
    NONE = "none"
    FUNCTION = "function"
    ORIGINAL = "original"
    ORIGINAL_MODIFIED = "original-modified"
    COSMETIC = "cosmetic"
    FIXABLE = "fixable"

tested_description = {
    Tested.NONE: "**Diese Platine ist von mir entworfen und noch nicht getestet.**",
    Tested.FUNCTION: "Ich habe die Platine aufgebaut und getestet.",
    Tested.ORIGINAL: "Die Platine wurde vom Originalautor getestet.",
    Tested.ORIGINAL_MODIFIED: "Das ürsprüngliche Design wurde vom Originalautor getest. **Meine Modifikationen sind noch ungetestet.**",
    Tested.COSMETIC: "Ich habe die Platine aufgebaut und getestet. Die Beschriftung enthält Fehler.",
    Tested.FIXABLE: "Ich habe die Platine aufgebaut und getestet. Die Schaltung enthält behebbare Fehler."
}

class Page:
    def __init__(self, directory, site):
        self.directory = directory
        self.title = ""
        self.index_page = "index"
        self.tested = None
        self.tested_comment = None
        self.systems = {}
        self.components = {}
        self.components_names = []
        self.photos = []
        self.content = []
        self.links = []
        self.parse(site)
    
    def parse(self, site):
        filename = f"{self.directory}/index.md"
        if not os.path.exists(filename):
            messages.error(f"no index.md file in '{self.directory}'")
            return

        images = {}
        for extension in ["jpeg", "jpg", "png"]:
            for file in glob.glob(f"*.{extension}", root_dir=self.directory):
                images[file] = False

        current_components_name = ""
        with open(filename, "r") as file:
            state = State.PREAMBLE

            for (line_number, line) in enumerate(file):
                line = line.rstrip()
                if state != State.CONTENT:
                    if not line or line[0] == "#":
                        continue
                    if line[0] != " ":
                        state = State.PREAMBLE
                
                if state == State.PREAMBLE:
                    if line == "---":
                        state = State.CONTENT
                    else:
                        match = re.search(preamble_field_pattern, line)
                        if match:
                            field = match.group(1)
                            value = match.group(2)
                            if field == "title":
                                self.title = value
                            elif field == "page":
                                self.index_page = value
                            elif field == "tested":
                                try:
                                    values = value.split(maxsplit=1)
                                    self.tested = Tested(values[0])
                                    if len(values) > 1:
                                        self.tested_comment = values[1]
                                except:
                                    messages.error(f"Invalid tested '{value}'", filename, line_number)
                            else:
                                try:
                                    state = State(field)
                                    if field == "components":
                                        current_components_name = value
                                        self.components_names.append(current_components_name)
                                except:
                                    messages.error(f"Invalid preamble field '{field}'", filename, line_number)
                        else:
                            messages.error(f"Invalid line in preamble: '{line}'", filename, line_number)

                elif state == State.COMPONENTS:
                    match = re.search(component_pattern, line)
                    if match:
                        try:
                            amount = float(match.group(1))
                        except:
                            messages.error("Invalid amount '{match.group(4)}'", filename, line_number)
                            continue

                        name = match.group(2).rstrip()
                        price = None
                        explicit_price = False
                        if match.group(4):
                            try:
                                explicit_price = True
                                if match.group(4) != "-":
                                    price = float(match.group(4))
                            except:
                                messages.error(f"Invalid price '{match.group(4)}'", filename, line_number)
                        component = site.components.get(name)
                        if not explicit_price and component.index is None:
                            messages.warning(f"Unknown component '{name}'", filename, line_number)
                        if current_components_name not in self.components:
                            self.components[current_components_name] = []
                        self.components[current_components_name].append(Part(component, amount, price))
                    else:
                        messages.error(f"Invalid component line '{line}'", filename, line_number)
                
                elif state == State.PHOTOS:
                    match = re.search(photo_pattern, line)
                    if match:
                        image_file = match.group(1)
                        title = match.group(2)
                        if image_file not in images:
                            messages.error(f"Photo '{image_file}' does not exist", filename, line_number)
                        else:
                            self.photos.append(Photo(image_file, title))
                            images[image_file] = True
                    else:
                        messages.error(f"Invalid photo line '{line}'", filename, line_number)

                elif state == State.LINKS:
                    match = re.search(link_pattern, line)
                    if match:
                        name = match.group(1).strip()
                        link = match.group(3)
                        try:
                            self.links.append(Link(name, link))
                        except Exception as ex:
                            messages.error(ex, filename, line_number)
                    else:
                        messages.error(f"Invalid system line '{line}'", filename, line_number)


                elif state == State.SYSTEMS:
                    match = re.search(page_system_pattern, line)
                    if match:
                        system = match.group(1).strip()
                        index = match.group(3)
                        if not index:
                            index = 999
                        else:
                            try:
                                index = float(index)
                            except:
                                messages.error(f"Invalid system index '{index}'", filename, line_number)
                                continue
                        if site.systems.has_system(system):
                            self.systems[system] = index
                        else:
                            messages.error(f"Unknown system '{system}'", filename, line_number)
                    else:
                        messages.error(f"Invalid system line '{line}'", filename, line_number)

                elif state == State.CONTENT:
                    self.content.append(line)
            
            if len(self.systems) == 0:
                messages.error("No systems specified.", filename)
            
            for file, used in images.items():
                if not used:
                    messages.warning(f"Photo '{file}' not used", filename)
            
            if self.directory != "order" and False: # TODO: add command line argument for additional checks
                if self.tested is None:
                    messages.warning(f"No testing state specified.", filename)
                if not self.content:
                    messages.warning(f"No description provided.", filename)

            if self.index_page not in site.index_pages:
                messages.error(f"Unknown index page '{self.index_page}'")
            else:
                site.index_pages[self.index_page].add_page(self)


    def write(self):
        writer = HTMLWriter.HTMLWriter(f"{self.directory}/index.html", self.title)

        if self.tested is not None:
            tested = [tested_description[self.tested]]
            if self.tested_comment is not None:
                tested.append(self.tested_comment)
            writer.markdown(tested)

        if len(self.links) > 0:
            writer.open("p", {"class": "links"})
            first = True
            for link in self.links:
                if first:
                    first = False
                else:
                    writer.text(" • ")
                writer.link(link.target, link.name)
            writer.close()

        if len(self.photos) > 0:
            writer.open("p", {"class": "photos"})
            for photo in self.photos:
                writer.image(photo.file, photo.title)
            writer.close()

        if len(self.content) > 0:
            writer.markdown(self.content)

        for components_name in self.components_names:
            components = self.components[components_name]
            if components_name:
                writer.tag("h3", components_name, {"class":"components"})
            writer.table("components list", ["Komponente", "Anzahl", "Preis", "Anbieter"])

            total_pcb = 0
            total_kit = 0
            have_pcb = False
            have_kit = False
            unknown_kit_price = False
            unknown_pcb_price = False
            for component in sorted(components):
                price = component.cost()
                if price is not None:
                    if component.is_pcb():
                        total_pcb += price
                        have_pcb = True
                    else: 
                        have_kit = True
                    total_kit += price
                else:
                    if component.is_pcb():
                        unknown_pcb_price = True
                    unknown_kit_price = True
                if price is None:
                    price_string = "—"
                else:
                    price_string = f"€{price:.2f}"
                writer.table_row([component.name(), component.amount, price_string, component.component.suppliers.html()], "component")
                if component.is_pcb():
                    have_pcb = True
            if have_pcb:
                if unknown_pcb_price:
                    total_pcb_string = "—"
                else:
                    total_pcb_string = f"€{total_pcb:.2f}"
                writer.table_row(["nur Platine", "", total_pcb_string, ""], "total")
            if have_kit:
                if unknown_kit_price:
                    kit_name = "Teilbausatz"
                else:
                    kit_name = "Bausatz"
                total_kit_string = f"€{total_kit:.2f}"
                writer.table_row([kit_name, "", total_kit_string, ""], "total")
            writer.close()
    
    def compare_system_list(self, other, system):
        if system in self.systems and system in other.systems:
            index = self.systems[system]
            other_index = other.systems[system]
            if index != other_index:
                return index - other_index
            else:
                link_title = self.link_title(system)
                other_link_title = other.link_title(system)
                if link_title < other_link_title:
                    return -1
                elif link_title > other_link_title:
                    return 1
                else:
                    return 0
        else:
            return 0
    
    def link_title(self, system):
        if self.title.startswith(system):
            return self.title[len(system):].strip()
        else:
            return self.title
