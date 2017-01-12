from argparse import ArgumentParser
from os import _exit

from inventorygeneration.app.generate_html import main

path = "0e10565a460846f8b0a3ad9c415911c9"

if __name__ == "__main__":
    ARGUMENTS = ArgumentParser(description="a command-line tool to generate inventory html files " +
                               "for accessions in longTermStorage in the LDR",
                               epilog="Copyright University of Chicago, 2016; authored by Tyler " +
                               "Danstrom <tdanstrom@uchicago.edu>")
    ARGUMENTS.add_argument("longterm_root", action='store',
                           help="The root directory for longterm storage on-disk")
    ARGUMENTS.add_argument("arkid", action='store',
                           help="The arkid that you want to generate inventory files for")
    ARGUMENTS.add_argument("-n", "--maximum_files_per_list", action="store", type=int,
                           help="The number of files that should be presented in a particular " +
                           "file list")
    PARSED_ARGS = ARGUMENTS.parse_args()
    if PARSED_ARGS.maximum_files_per_list:
        _exit(main(PARSED_ARGS.longterm_root,
                   PARSED_ARGS.arkid,
                   num_files_per_segment=PARSED_ARGS.maximum_files_per_list))
    else:
        _exit(main(PARSED_ARGS.longterm_root,
                   PARSED_ARGS.arkid))