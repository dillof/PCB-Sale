import md2typst
import subprocess

from .Site import Site
from .HandoutPage import HandoutPage

preamble = """
#set page(\"a5\")
#show heading: it => {
  // Clever trick to reduce spacing between consecutive headings
  // See https://github.com/typst/typst/issues/2953
  let previous_headings = query(selector(heading).before(here(), inclusive: false))
  if previous_headings.len() > 0 {
    let prev_loc = previous_headings.last().location().position()
    let it_loc = it.location().position()
    if (it_loc.page == prev_loc.page and it_loc.x == prev_loc.x and it_loc.y - prev_loc.y < 60pt) { // threshold
      v(-2.5em) // amount to reduce spacing, could make this dependent on it.level
    }
    else {}
  }
  [#v(1.5em) #it #v(.5em)]
}
"""

class Handout:
    def __init__(self, index_page: str):
        self.site = Site()
        self.index_page = self.site.index_pages[index_page]
        self.pcbs = [HandoutPage(page) for page in self.site.index_pages[index_page].all_pages()]

    def write(self):
        with open("handout.typ", "w") as file:
            print(f"{preamble}", file=file)

            print(f"= {self.index_page.title}\n", file=file)
            if len(self.index_page.content) > 0:
                for line in self.index_page.content:
                    text = md2typst.convert(line)
                    print(f"{text}\n", file=file)
                print("", file=file)

            for pcb in self.pcbs:
                pcb.write(file)

    def compile(self):
        try:
            subprocess.run(["typst", "compile", "handout.typ"], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to compile handout.typ: {e}") from e
        except FileNotFoundError:
            raise RuntimeError("typst command not found. Please ensure typst is installed and in your PATH.") from None