# Repsitory of standard components

import re

seller_links = {
    "aliexpress": "AliExpress",
    "amazon": "Amazon",
    "berrybase": "BerryBase",
    "conrad": "Conrad",
    "digikey": "DigiKey",
    "ebay": "eBay",
    "mouser": "Mouser",
    "reichelt": "Reichelt",
    "restore-store": "Restore-Store",
    "welectron": "Welectron"
}

component_cost_pattern = r"^\s*(\S+)\s+(.*?)(http.*)?$"

class Components:
    def __init__(self):
        self.categories = []
        self.categories_names = {}
        self.category_components = {}
        self.components = {}
        self.next_index = 0
        self.read_component_costs()

    def read_component_costs(self):
        with open("component-costs.txt", "r") as file:
            current_category = ''
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
                
                match = re.search(component_cost_pattern, line)
                if match:
                    price = None
                    if match.group(1) != "-":
                        try:
                            price = float(match.group(1))
                        except:
                            print(f"component-costs.txt:{line_number}: Invalid price '{match.group(1)}'", file=sys.stderr)
                            ok = False
                    name = match.group(2).strip()
                    link = match.group(3)
                    if name in self.components:
                        component = self.components[name]
                    else:
                        component = Component(name)
                        self.add_component(current_category, component)
                    component.add_product(Product(price, link))
                else:
                    print(f"component-costs.txt:{line_number}: Invalid component cost line '{line}'", file=sys.stderr)
                    ok = False


    def add_category(self, category):
        if category in self.categories_names:
            raise RuntimeError(f"duplicate category '{category}'")
        self.categories_names[category] = {}
        self.category_components[category] = []
        self.categories.append(category)
    
    def add_component(self, category, component):
        if category not in self.categories_names:
            raise RuntimeError(f"unknown category '{category}'")
        if component.name in self.components:
            return
        self.categories_names[category][component.name] = True
        component.index = self.next_index
        self.next_index += 1
        self.category_components[category].append(component)
        self.components[component.name] = component
    
    def get(self, name):
        if name in self.components:
            return self.components[name]
        else:
            return Component(name)
    
    def write_html(self, file):
        print(f'<html>\n<head>\n<meta charset="utf-8">\n<title>Komponenten</title>\n<link rel="stylesheet" href="style.css">\n</head>\n<body>\n<h1>Komponenten</h1>', file=file)

        for category in self.categories:
            print(f'<h2>{category}</h2>', file=file)
            print(f'<table class="components cost">\n<tr class="header"><td>Komponente</td><td>Preis</td><td>Anbieter</td><tr>', file=file)
            for product in self.categories_ordered[category]:
                price = product.minimum
                if price is None:
                    price = "—"
                else:
                    price = f"€{price:.2f}"
                print(f'<tr class="component"><td>{product.name}</td><td>{price}</td><td>{product.suppliers.html()}</td></tr>', file=file)
            print(f'</table>', file=file)
        print(f'</body></html>', file=file)

class Component:
    def __init__(self, name):
        self.name = name
        self.index = None
        self.suppliers = Suppliers()
    
    def add_product(self, product):
        self.suppliers.add(product)
    
    def get_supplier(self):
        return self.suppliers.get_cheapest()

    def __eq__(self, other):
        return self.index == other.index and self.name == other.name

    def __lt__(self, other):
        if self.index is None:
            if other.index is not None:
                return False
        else:
            if other.index is None:
                return True
            elif other.index != self.index:
                return self.index < other.index

        return self.name < other.name


# List of suppliers
class Suppliers:
    def __init__(self):
        self.minimum = None
        self.products = []

    def add(self, product):
        if self.minimum is None or (product.price is not None and product.price < self.minimum):
            self.minimum = product.price
        self.products.append(product)
    
    def get_cheapest(self):
        if not self.products:
            return None
        else:
            return sorted(self.products)[0].seller()

    def html(self):
        products = []
        for product in sorted(self.products):
            product_html = product.html()
            if product_html is not None:
                products.append(product_html)
        return ' • '.join(products)

# Component at one supplier
class Product:
    def __init__(self, price, link):
        self.price = price
        self.link = link
    
    def __lt__(self, other):
        if self.price is not None:
            if other.price is not None:
                return self.price < other.price
            else:
                return True
        else:
            return False
    
    def __le__(self, other):
        if self.price is not None:
            if other.price is not None:
                return self.price <= other.price
            else:
                return True
        else:
            return other.price is None
    
    def __eq__(self, other):
        if self.price is not None:
            if other.price is not None:
                return self.price == other.price
            else:
                return False
        else:
            return other.price is None
    
    def __ne__(self, other):
        return not self == other
    
    def __ge__(self, other):
        return not self < other
    
    def __gt__(self, other):
        return not self <= other
    
    def seller(self):
        if self.link is None:
            return None
        for site in seller_links:
            if site in self.link:
                return seller_links[site]
        match = re.search(r"^https?://([^/]*).*$", self.link)
        if match:
            return match.group(1)
        else:
            return None
    
    def html(self):
        if self.link is None:
            return None
        return f'<a class="seller" href="{self.link}">{self.seller()}</a>'
