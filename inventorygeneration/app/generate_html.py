from collections import namedtuple
from jinja2 import Environment, FileSystemLoader
from json import dumps
from os import mkdir, listdir
from os.path import join, basename
from sys import argv

from uchicagoldrtoolsuite.bit_level.lib.readers.filesystemarchivereader import FileSystemArchiveReader

ENV = Environment(loader=FileSystemLoader("./templates"))

print(ENV.list_templates())
print(dir(ENV))
LONGTERM_ROOT = "/data/repository/longTermStorage"

ACCESSION_URL_BASE = "https://y2.lib.uchicago.edu/ldraccession/"
URL_BASE = "https://y2.lib.uchicago.edu/processor/"

def main(longterm,arkid, num_files_per_segment=None):
    print(longterm)
    n = 2
    arkid_split = [arkid[i:i+n] for i in range(0, len(arkid), n)]
    reader = FileSystemArchiveReader(longterm, arkid)
    archive = reader.read()

    landing_page = namedtuple("landing_page",
                              "accession_id collection_title description segments accession_record")
    msuites = archive.get_materialsuite_list()
    tally = 0
    current_bunch = []
    all_bunches = []
    if not num_files_per_segment:
        num_files_per_segment = 5
    total_msuites = len(msuites)
    count = 0
    for n in msuites:
        count += 1
        n_tuple = namedtuple("an_item",
                             "name contenturl premisurl")(n.content.item_name,
                                                          URL_BASE + arkid + "/" +\
                                                            n.identifier + "/content",
                                                          URL_BASE + arkid + "/" +\
                                                            n.identifier + "/premis")

        current_bunch.append(n_tuple)
        tally += 1
        if len(current_bunch) == num_files_per_segment:
            tally = 0
            all_bunches.append(current_bunch)
            current_bunch = []
        elif count == total_msuites:
            all_bunches.append(current_bunch)
    tally_bunch = 0
    total = 0
    pages = [x for x in range(0,
                              len(all_bunches) + 1)
            ]
    pages_dict = {}
    for n in pages:
        pages_dict[str(n)] = {"active":True, "startPoint":True}
    print(pages_dict)
    json_string = dumps(pages_dict)
    mkdir("./" + arkid)
    for n_bunch in all_bunches:
        tally_id = "{}.html".format(tally_bunch)
        print(tally_id)
        print(len(n_bunch))
        total += len(n_bunch)
        tally_bunch += 1
        pages_dict[str(tally_bunch)]['active'] = True
        pages_dict[str(tally_bunch)]['startPoint'] = True
        segment_template = ENV.get_template("section_list.html")
        segment_html = segment_template.render(arkid=arkid, label=str(tally_bunch),
                                               files=n_bunch,
                                               pagerecord=json_string)
        with open(join(arkid, tally_id), "w") as a_file_to_write:
            a_file_to_write.write(segment_html)
    landing_template = ENV.get_template("accession_landing.html")
    landing_html = landing_template.render(arkid=arkid,
                                           accessions=[basename(str(x.path))
                                                       for x in archive.get_accessionrecord_list()],
                                           legalnotes=[basename(str(x.path))
                                                       for x in archive.get_legalnote_list()],
                                           adminnotes=[basename(str(x.path))
                                                       for x in archive.get_adminnote_list()])
    with open(join(arkid, "index.html"), "w") as write_file:
        write_file.write(landing_html)
    return 0
