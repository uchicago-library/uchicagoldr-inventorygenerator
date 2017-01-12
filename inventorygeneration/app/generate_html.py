"""a module to generate html inventory pages of an accession in the LDR with permanent private URLs
"""

from collections import namedtuple
from os import mkdir
from os.path import join, basename
from json import dumps
from jinja2 import Environment, FileSystemLoader

from pypremis.lib import PremisRecord
from uchicagoldrtoolsuite.bit_level.lib.readers.filesystemarchivereader import FileSystemArchiveReader

ID = "0e10565a460846f8b0a3ad9c415911c9"

ENV = Environment(loader=FileSystemLoader("./templates"))
LONGTERM_ROOT = "/data/repository/longTermStorage"
ACCESSION_URL_BASE = "https://y2.lib.uchicago.edu/ldraccession/"
URL_BASE = "https://y2.lib.uchicago.edu/processor/"

def main(longterm,arkid, num_files_per_segment=None):
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
    for msuite in msuites:
        count += 1
        precord = PremisRecord(frompath=str(msuite.premis.path))
        original_name = precord.objects_list[0].get_originalName()
        n_tuple = namedtuple("an_item",
                             "name contenturl premisurl")(original_name,
                                                          URL_BASE + arkid + "/" +\
                                                            msuite.identifier + "/content",
                                                          URL_BASE + arkid + "/" +\
                                                            msuite.identifier + "/premis")

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
    for page in pages:
        pages_dict[str(page)] = {"active":True, "startPoint":True}
    json_string = dumps(pages_dict)
    mkdir("./" + arkid)
    for n_bunch in all_bunches:
        tally_id = "{}.html".format(tally_bunch)
        total += len(n_bunch)
        tally_bunch += 1
        pages_dict[str(tally_bunch)]['active'] = True
        pages_dict[str(tally_bunch)]['startPoint'] = True
        pages_dict[str(tally_bunch)]['numfiles'] = len(n_bunch)
        segment_template = ENV.get_template("section_list.html")
        segment_html = segment_template.render(arkid=arkid,
                                               label=str(tally_bunch),
                                               files=n_bunch,
                                               pagerecord=json_string)
        with open(join(arkid, tally_id), "w") as a_file_to_write:
            a_file_to_write.write(segment_html)
    landing_template = ENV.get_template("accession_landing.html")
    pages = sorted([(x, pages_dict[x].get("numfiles"))
                    for x in pages_dict.keys() if pages_dict[x].get("numfiles")
                   ],
                   key=lambda x: x[0])
    landing_html = landing_template.render(arkid=arkid,
                                           pages=pages,
                                           accessions=[ACCESSION_URL_BASE + "/accession/" +
                                                       basename(str(x.path))
                                                       for x in archive.get_accessionrecord_list()],
                                           legalnotes=[ACCESSION_URL_BASE + "/legalnote/" +
                                                       basename(str(x.path))
                                                       for x in archive.get_legalnote_list()],
                                           adminnotes=[ACCESSION_URL_BASE + "/adminnote/" +
                                                       basename(str(x.path))
                                                       for x in archive.get_adminnote_list()])
    with open(join(arkid, "index.html"), "w") as write_file:
        write_file.write(landing_html)
    return 0
