import glob
import os
from django.core.management.base import LabelCommand

class Command(LabelCommand):
    help = "Import a set of xml from reta-vortaro."
    args = "[datadir]"
    label = "data directory"
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle_label(self, data_dir, **options):
        print("Importing data from %s." % data_dir)
        for datafile in glob.glob(os.path.join(data_dir, "*.xml")):
            print("Importing %s" % datafile)
