class Part:
    def __init__(self, component, amount, price=None):
        self.component = component
        if amount == int(amount):
            self.amount = int(amount)
        else:
            self.amount = amount
        self.price = price

    def name(self):
        return self.component.name

    def cost(self):
        if self.price is not None:
            price = self.price
        else:
            price = self.component.get_price()
        if price is not None:
            price *= self.amount
        return price
    
    def is_pcb(self):
        return self.component.name == "Platine"

    def __eq__(self, other):
        return self.component == other.component
    
    def __lt__(self, other):
        return self.component < other.component
