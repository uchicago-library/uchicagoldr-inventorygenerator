from argparse import ArgumentParser
from os import _exit

from ldrinventorycreator.app.generate_html import main

if __name__ == "__main__":
    arguments = ArgumentParser(description="a command-line tool to generate inventory html files for accessions in longTermStorage in the LDR",
                               epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("longterm_root", action='store', help="The root directory for longterm storage on-disk")
    arguments.add_argument("arkid", action='store', help="The arkid that you want to generate inventory files for")
    arguments.add_argument("url_base", action='store', help="The url host and base path to locate to return all files in the LDR to authenticated users")
    parsed_args = arguments.parse_args()
    _exit(main(longterm_root, url_Base, arkid))
