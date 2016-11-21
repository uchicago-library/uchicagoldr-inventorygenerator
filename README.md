# Setup Instructions

The inventory generator can be run with the following command:

python generate_inventory.py /home/test/longTermStorage foo https://example.com/

This will create inventory files describing the contents of the accession identified "foo" in longTermStorage with permanent URLS starting with http://example.com/ for every PREMIS object in that accession.
