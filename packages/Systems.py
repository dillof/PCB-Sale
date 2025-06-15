class Systems:
    def __init__(self):
        self.category_list = []
        self.categories = {}
        self.systems = {}
        self.read_systems()

    def read_systems(self):
        with open("systems.txt", "r") as file:
            current_category = None
            for (line_number, line) in enumerate(file):
                line = line.rstrip()
                if not line:
                    continue
                if line[0] == "#":
                    if line[1] == "#":
                        continue
                    current_category = line[1:].strip()
                    self.add_category(current_category)
                    continue

                self.add_system(current_category, line)

    def add_category(self, category):
        if self.has_category(category):
            raise RuntimeError(f"duplicate category '{category}'")
        self.category_list.append(category)
        self.categories[category] = []
    
    def add_system(self, category, system):
        if not self.has_category(category):
            raise RuntimeError(f"unknown category '{category}'")
        if self.has_system(system):
            raise RuntimeError(f"duplicate system '{system}'")
        self.categories[category].append(system)
        self.systems[system] = category

    def has_category(self, category):
        return category in self.categories
    
    def has_system(self, system):
        return system in self.systems
    
    def category_of(self, system):
        return self.systems[system]
