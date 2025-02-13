
:: generatod docs using pdoc
:: pip install pdoc

:: usage: pdoc.exe [-o DIR] [-d {markdown,google,numpy,restructuredtext}] [--include-undocumented] [-e module=url]
::                [--favicon URL] [--footer-text TEXT] [--logo URL] [--logo-link URL] [--math] [--mermaid] [--search]
::                [--show-source] [-t DIR] [-h HOST] [-p PORT] [-n] [--help] [--version]
::                [module [module ...]]

@pdoc pyzx48tools --output-dir docs
@pause
