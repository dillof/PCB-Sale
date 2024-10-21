class System:
    self.category_list = []
    self.categories = {}
    self.systems = {}

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
