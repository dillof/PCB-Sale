class HTMLFormatter:
    def __init__(self):
        return

    def tag(self, tag, contents=None, attributes={}):
        html = self.open(tag, attributes, contents is None)
        if contents is not None:
            html += self.escape(contents)
            html += self.close(tag)
        return html
    
    def open(self, tag, attributes={}, close=False):
        html = f"<{tag}"
        for name, value in attributes.items():
            if value is not None:
                html += f" {name}=\"{value}\""
        if close:
            html += "/"
        html += ">"
        return html
    
    def close(self, tag):
        return f"</{tag}>"
    

    def image(self, src, alt=None, css_class=None):
        return self.tag("img", attributes={
            "src": src,
            "alt": alt,
            "class": css_class
        })
    
    def link(self, href, content=None, css_class=None):
        html = self.open("a", {
            "href": href,
            "class": css_class
        }, close=content is None)
        if content is not None:
            html += self.escape(content) + self.close("a")
        return html

    def escape(self, content):
        # TODO
        return content
