import os

from Messages import messages

preamble_field_pattern = r"^(\S+):\s*(.*)$"


class State(enum.Enum):
    COMPONENTS = "components"
    CONTENT = "content"
    LINKS = "links"
    PHOTOS = "photos"
    PREAMBLE = "preamble"
    SYSTEMS = "systems"

class Page:
    def __init__(self, directory):
        self.directory = directory
        self.title = ""
        self.index_page = "index"
        self.hidden = False
        self.systems = {}
        self.components = {}
        self.components_names = []
        self.photos = []
        self.content = []
        self.links = []
    
    def parse(self):
        filename = f"{directory}/index.md"
        if not os.path.exists(file_path):
            raise RuntimeError(f"no index.md file in '{directory}'")

        current_components_name = ""
        with open(filename, "r") as file:
            state = State.PREAMBLE

            for (line_number, line) in enumerate(file):
                line = line.rstrip()
                if state != State.PREAMBLE and state != State.CONTENT:
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
                            if field == "title":
                                page.title = match.group(2)
                            elif field == "page":
                                page.index_page = match.group(2)
                            else:
                                try:
                                    state = State(field)
                                    if field == "components":
                                        current_components_name = match.group(2)
                                        page.components_names.append(current_components_name)
                                except:
                                    print(f"{filename}:{line_number}: Invalid preamble field '{field}'", file=sys.stderr)                                
                                    ok = False
                        else:
                            print(f"{filename}:{line_number}: Invalid line in preamble: '{line}'", file=sys.stderr)
                            ok = False

                elif state == State.COMPONENTS:
                    match = re.search(component_pattern, line)
                    if match:
                        try:
                            amount = float(match.group(1))
                        except:
                            print(f"{filename}:{line_number}: Invalid amount '{match.group(4)}'", file=sys.stderr)
                            ok = False
                            continue

                        name = match.group(2).rstrip()
                        price = None
                        explicit_price = False
                        component_cost = None
                        if match.group(4):
                            try:
                                explicit_price = True
                                if match.group(4) != "-":
                                    price = float(match.group(4))
                            except:
                                print(f"{filename}:{line_number}: Invalid price '{match.group(4)}'", file=sys.stderr)
                                ok = False
                        if name in components:
                            component_cost = components[name]
                        if not explicit_price and component_cost is None:
                            print(f"{filename}:{line_number}: Unknown component '{name}'", file=sys.stderr)
                            ok = False
                        if current_components_name not in page.components:
                            page.components[current_components_name] = []
                        page.components[current_components_name].append(Component(amount, name, component_cost, price))
                    else:
                        print(f"{filename}:{line_number}: Invalid component line '{line}'", file=sys.stderr)
                        ok = False
                
                elif state == State.PHOTOS:
                    match = re.search(photo_pattern, line)
                    if match:
                        page.photos.append(Photo(match.group(1), match.group(2)))
                    else:
                        print(f"{filename}:{line_number}: Invalid photo line '{line}'", file=sys.stderr)
                        ok = False

                elif state == State.LINKS:
                    match = re.search(link_pattern, line)
                    if match:
                        name = match.group(1).strip()
                        link = match.group(3)
                        if not link:
                            if name in link_defaults:
                                link = link_defaults[name]
                            else:
                                    print(f"{filename}:{line_number}: No link given for '{name}'", file=sys.stderr)
                                    ok = False
                                    continue
                        if name in link_name_aliases:
                            name = link_name_aliases[name]
                        page.links.append(Link(name, link))
                    else:
                        print(f"{filename}:{line_number}: Invalid system line '{line}'", file=sys.stderr)
                        ok = False


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
                                print(f"{filename}:{line_number}: Invalid system index '{index}'", file=sys.stderr)
                                ok = False
                                continue
                        if systems.has_system(system):
                            page.systems[system] = index
                        else:
                            print(f"{filename}:{line_number}: Unknown system '{system}'", file=sys.stderr)
                            ok = False
                    else:
                        print(f"{filename}:{line_number}: Invalid system line '{line}'", file=sys.stderr)
                        ok = False

                elif state == State.CONTENT:
                    page.content.append(line)
            
            if len(page.systems) == 0:
                print(f"{filename}: No systems specified.")
                ok = False

    def write(self):
        with open(f"{directory}/index.html") as file:
            self.write_html(file)
    
    def write_html(self, file):
        print(f'<html>\n<head>\n<meta charset="utf-8">\n<title>{self.title}</title>\n<link rel="stylesheet" href="../style.css">\n</head>\n<body>\n<h1>{self.title}</h1>', file=file)

        if len(self.content) > 0:
            print(markdown.markdown("\n".join(self.content), extensions=['tables']), file=file)

        if len(self.links) > 0:
            print('<p class="links">', file=file)
            first = True
            for link in self.links:
                if first:
                    first = False
                else:
                    print('•', file=file)
                print(f'<a href="{link.link}">{link.name}</a>', file=file)
            print('</p>', file=file)

        if len(self.photos) > 0:
            print('<p class="photos">', file=file)
            for photo in self.photos:
                print(f'<img src="{photo.file}" alt="{photo.title}">', file=file)
            print('</p>', file=file)

        for components_name in self.components_names:
            components = self.components[components_name]
            if components_name:
                print(f'<h3 class="components">{components_name}</h3>', file=file)
            print('<table class="components list">\n<tr class="header"><td>Komponente</td><td>Anzahl</td><td>Preis</td><td>Anbieter</td></tr>', file=file)

            total_pcb = 0
            total_kit = 0
            have_pcb = False
            have_kit = False
            unknown_kit_price = False
            unknown_pcb_price = False
            for component in components:
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
                print(component.html(), file=file)
                if component.is_pcb():
                    have_pcb = True
            if have_pcb:
                if unknown_pcb_price:
                    total_pcb_string = "—"
                else:
                    total_pcb_string = f"€{total_pcb:.2f}"
                print(f'<tr class="total"><td>nur Platine</td><td></td><td>{total_pcb_string}</td><td></td></tr>', file=file)
            if have_kit:
                if unknown_kit_price:
                    kit_name = "Teilbausatz"
                else:
                    kit_name = "Bausatz"
                total_kit_string = f"€{total_kit:.2f}"
                print(f'<tr class="total"><td>{kit_name}</td><td></td><td>{total_kit_string}</td><td></td></tr>', file=file)
            print('</table>', file=file)

        print("</body>\n</html>", file=file)
    
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
