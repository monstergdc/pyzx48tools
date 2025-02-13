
import pdoc
import pdoc.render
from pathlib import Path

#pdoc pyzx48tools --output-dir docs

here = Path(__file__).parent

pdoc.pdoc(
        "pyzx48tools",
        output_directory = here / "docs"
)

