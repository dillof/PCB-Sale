class HTMLWriter:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(self.filename, mode="w")
        self.open_elements = []

    def tag(self, tag, attributes={}):
        self.open(tag, attributes, True)
    
    def open(self, tag, attributes={}, close=False):
        print(f"<{tag}", file=self.file)
        for name, value in attributes.items():
            if vale is not None:
                print(f" {attribute}=\"{value}\"", file=self.file)
        if close:
            print("/", file=self.file)
        else:
            self.open_elements.append(tag)
        print(">", file=self.file)
    
    def close(self):
        if not self.open_elements:
            raise RuntimeError("no open tag")
        tag = self.open_elements.pop()
        print(f"</{tag}>", file=self.file)
    

    def image(self, src, alt=None, css_class=None):
        self.tag("img", {
            "src": src,
            "alt": alt
            "class": css_class
        })
    
    def a(self, href, css_class=None):
        self.open("a", {
            "href": href
            "class": css_class
        })
    
    