import os
# Defaults for paths
ROOT_DIR = os.path.abspath(os.curdir)  # Root of project
DATABASE_DIR = os.path.join(ROOT_DIR, 'databases')
TEST_DATABASE_PATH = os.path.join(DATABASE_DIR, "probo2.db")
PLOT_JSON_DEFAULTS = os.path.join(ROOT_DIR, os.path.join("src", "plotting", "defaults.json"))

STATUS_FILE_DIR = os.path.join(ROOT_DIR,"status.json")



SUPPORTED_TASKS = ["EE-ST", "EE-CO", "EE-PR", "EE-GR", "EE-SST", "EE-STG",
                      "SE-ST", "SE-SST", "SE-STG", "SE-CO", "SE-PR", "SE-GR", "SE-ID",
                      "DC-ST", "DC-SST", "DC-STG", "DC-CO", "DC-PR", "DC-ID", "DC-GR",
                      "DS-ST", "DS-SST", "DS-STG", "DS-CO", "DS-PR", "DS-GR"]