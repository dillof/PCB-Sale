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
            return self.price
        return self.component.get_price()
    
    def is_pcb(self):
        return self.component.name == "Platine"
