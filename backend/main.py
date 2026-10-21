class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

# A list of custom objects
products = [
    Product("Laptop", 1200),
    Product("Mouse", 25),
    Product("Keyboard", 75)
]

# Sort by the 'price' attribute

print(sorted(products, key=lambda p: p.price))