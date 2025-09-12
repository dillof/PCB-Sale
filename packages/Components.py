# Repsitory of standard components

import re
import sys

from . import HTMLFormatter
from . import HTMLWriter

seller_links = {
    "aliexpress": "AliExpress",
    "amazon": "Amazon",
    "berrybase": "BerryBase",
    "conrad": "Conrad",
    "digikey": "DigiKey",
    "ebay": "eBay",
    "mouser": "Mouser",
    "polyplay": "Poly.Play",
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
    
    def write(self):
        writer = HTMLWriter.HTMLWriter("component-costs.html", "Komponenten")

        for category in self.categories:
            writer.tag("h2", category, newline=True)
            writer.table("components cost", ["Komponente", "Preis", "Anbieter"])
            for product in self.category_components[category]:
                price = product.get_price()
                if price is None:
                    price = "—"
                else:
                    price = f"€{price:.2f}"
                writer.table_row([product.name, price, product.suppliers.html()], css_class="component")
            writer.table_close()

class Component:
    def __init__(self, name):
        self.name = name
        self.index = None
        self.suppliers = Suppliers()
    
    def add_product(self, product):
        self.suppliers.add(product)
    
    def get_supplier(self):
        return self.suppliers.get_cheapest()
    
    def get_price(self):
        return self.suppliers.minimum

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
            return self.link
    
    def html(self):
        if self.link is None:
            return None
        return HTMLFormatter.HTMLFormatter().link(self.link, self.seller(), css_class="seller")
