from collections import namedtuple
from jinja2 import Environment, FileSystemLoader
from json import dumps
from os import mkdir, listdir
from os.path import join
from sys import argv

from uchicagoldrtoolsuite.bit_level.lib.readers.filesystemarchivereader import FileSystemArchiveReader
from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

LONGTERM_ROOT = "/data/repository/longTermStorage"

URL_BASE = "https://y2.lib.uchicago.edu/processor/"


def main(longterm, url_base, arkid):
    env = Environment(loader=FileSystemLoader("./templates"))
    n = 2
    arkid_split =[arkid[i:i+n] for i in range(0, len(arkid), n)]
    reader = FileSystemArchiveReader(longterm, arkid)
    archive = reader.read()
    files = []
    segments = []
    landing_page = namedtuple("landing_page", "accession_id collection_title description segments accession_record")
    for segment in archive.segment_list:
        for ms in segment.materialsuite_list:
            iName_content = ms.content.item_name
            arkid = str(ms.content.path).split('arf')[0].split('longTermStorage')[1].split('/')
            premisid = str(ms.content.path).split('pairtree_root')[1].split('arf')[0].split('/')
            arkid = ''.join(arkid)
            premisid = ''.join(premisid)
            x = namedtuple("an_item",
                           "name contenturl premisurl fitsurl techmdsurl presformsurl presformurl")\
                           (ms.content.item_name,
                            url_base + arkid + "/" + premisid + "/content",
                            url_base + arkid + "/" + premisid + "/premis",
                            url_base + arkid + "/"  + premisid + "/techmds/0",
                            url_base + arkid + "/" + premisid + "/techmds",
                            url_base + arkid + "/" + premisid + "/presforms",
                            url_base + arkid + "/" + premisid + "/presform")
            files.append(x)
        new_files_list = sorted(files, key=lambda x: x.name)
        segment = namedtuple("segment", "id files numfiles")(segment.identifier, new_files_list, len(new_files_list))
        segments.append(segment)

    l = [x for x in archive.accessionrecord_list if x.item_name == "accession_record.json"]
    h = HierarchicalRecord()
    h.fromJSON(str(l[0].path))
    mkdir("./" + arkid)

    collection_title = h.get_field("Collection Title")
    accession_id = h.get_field("Accession Identifier")
    summary = h.get_field("Summary")
    landing_page.accession_id = accession_id
    landing_page.collection_title = collection_title
    landing_page.description = summary
    landing_page.segments = []

    for n_segment in segments:
        a_seg = namedtuple("seg", "label numfiles")(n_segment.id, len(n_segment.files))
        landing_page.segments.append(a_seg)

    landing_page.accession_record = h.toJSON()
    landing_template = ENV.get_template("accession_landing.html")
    landing_html = landing_template.render(collection_title=collection_title[0], spcl_id=accession_id[0], ark_id=arkid, description=summary[0], segment_list=segments, fullaccessionrecord=h.toJSON())

    with open(join(arkid, "index.html"), "w") as write_file:
        write_file.write(landing_html)

    for n_segment in segments:
        new_list = [segment.files[i:i+1000] for i in range(0, len(segment.files), 1000)]
        page_numbers = [x for x in range(0, len(new_list))]
        p = {}
        p["pages"] = {}
        for n_group in range(len(new_list)):
            print(n_group)
            a_dict = {"active":False, "startPoint":False}
            p["pages"][n_group] = a_dict

    for n_segment in segments:
        last_page = len(new_list) - 1
        for n_group in range(len(new_list)):
            p["pages"][n_group]['active'] = True
            p["pages"][n_group]['startPoint'] = True
            json_string = dumps(p)
            segment_template = ENV.get_template("section_list.html")
            segment_html = segment_template.render(segment=n_segment, arkid=arkid, label=n_segment.id, files=new_list[n_group], pagerecord=json_string)
            with open(join(arkid, n_segment.id + "-" + str(n_group) + ".html"), "w") as a_file_to_write:
                a_file_to_write.write(segment_html)
            p["pages"][n_group]['active'] = False
            p["pages"][n_group]['startPoint'] = False
    return 0 
