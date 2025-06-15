from packages import HTMLFormatter

link_name_aliases = {
    "ibom": "Interakiver Bestückungsplan",
    "home": "Projekt-Homepage",
    "schematics": "Schaltplan"
}

link_defaults = {
    "ibom": "ibom.html",
    "schematics": "schematics.pdf"
}

class Link:
    def __init__(self, name, target=None):
        if target is None:
            if name in link_defaults:
                target = link_defaults[name]
            else:
                raise RuntimeError("no link target specified")
        if name in link_name_aliases:
            name = link_name_aliases[name]
        
        self.name = name
        self.target = target
