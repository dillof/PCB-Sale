import markdown

from . import HTMLFormatter

class HTMLWriter:
    def __init__(self, filename, title):
        if "/" in filename:
            top_directory = "../"
        else:
            top_directory = ""
        self.filename = filename
        self.file = open(self.filename, mode="w")
        self.open_elements = []
        self.formatter = HTMLFormatter.HTMLFormatter()
        self.open("html", newline=True)
        self.open("head", newline=True)
        self.tag("meta", attributes={"charset": "utf-8"}, newline=True)
        self.tag("title", title, newline=True)
        self.tag("link", attributes={"rel": "stylesheet", "href": f"{top_directory}style.css"}, newline=True)
        self.close(newline=True)
        self.open("body", newline=True)
        self.tag("h1", title, newline=True)

    def __del__(self):
        while self.open_elements:
            self.close()
        self.newline()

    def html(self, text):
        print(text, file=self.file, end="")

    def text(self, text):
        print(self.formatter.escape(text), file=self.file, end="")

    def markdown(self, text):
        print(markdown.markdown("\n".join(text), extensions=['tables']), file=self.file)


    def tag(self, tag, contents=None, attributes={}, newline=False):
        self.open(tag, attributes, contents is None)
        if contents is not None:
            self.text(contents)
            self.close()
        self.newline(newline)
    
    def open(self, tag, attributes={}, close=False, newline=False):
        print(self.formatter.open(tag, attributes, close), file=self.file, end="")
        if not close:
            self.push_open(tag)
        self.newline(newline)
    
    def close(self, tag=None, newline=False):
        real_tag = self.pop_open()
        if tag is not None and tag != real_tag:
            raise RuntimeError(f"trying to close {real_tag} with {tag}")
        print(self.formatter.close(real_tag), file=self.file, end="")
        self.newline(newline)

    def image(self, src, alt=None, css_class=None, newline=False):
        print(self.formatter.image(src, alt, css_class), file=self.file, end="")
        self.newline(newline)
    
    def link(self, href, contents=None, css_class=None, newline=False):
        print(self.formatter.link(href, contents, css_class), file=self.file, end="")
        if contents is None:
            self.push_open("a")
        self.newline(newline)

    def table(self, css_class=None, header=None):
        self.open("table", {"class": css_class}, newline=True)
        if header is not None:
            self.open("tr", {"class": "header"})
            for field in header:
                self.tag("td", field)
            self.close(newline=True)
    
    def table_row(self, contents, css_class=None):
        self.open("tr", {"class": css_class})
        for field in contents:
            self.tag("td", field)
        self.close(newline=True)
  
    def table_close(self):
        self.close("table", True)
  
    def newline(self, newline=True):
        if newline:
            print("", file=self.file)

    def push_open(self, tag):
        self.open_elements.append(tag)

    def pop_open(self):
        if not self.open_elements:
            raise RuntimeError("no open tag")
        return self.open_elements.pop()
