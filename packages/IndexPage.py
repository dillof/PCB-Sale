class IndexPage:
    def __init__(self, systems):
        self.systems = systems
        self.categories = {}
        self.pages = {}
    
    def add_page(self, page):
        for system in page.systems:
            if not self.systems.has_system:
                raise RuntimeError(f"unknown system '{system}'")
            self.pages[system].append(page)
            self.categories[self.systems.cagegory_of(system)] = True

    def write_html(self, file):
        for category in self.systems.category_list:
            if not self.has_category(category):
                continue

            print(f'<h2 class="system-category">{category}</h2>', file=file)
            for system in self.systems.categories[category]:
                if len(self.pages[system]) > 0:
                    print(f'<h3 class="system">{system}</h3>\n<div class="links">', file=file)
                    sorted_pages = sorted(self.pages[system], key=functools.cmp_to_key(lambda a, b: a.compare_system_list(b, system)))
                    for page in sorted_pages:
                        print(f'<a href="{page.directory}/"><span>', end="", file=file)
                        if len(page.photos) > 0:
                            print(f'<img src="{page.directory}/{page.photos[0].file}">', end="", file=file)
                        print(f'</span><span>{page.link_title(system)}</span></a>', file=file)
                    print("</div>", file=file)
