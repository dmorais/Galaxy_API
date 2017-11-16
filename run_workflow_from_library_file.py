# This script reads from a yml file a name of
# a workflow, inputs, labels and library
# creates fetchs all meta-data and launches the pipeline

import sys
from collections import namedtuple
from bioblend import galaxy
import os
import logging
import pprint
from utils.giobjects import *
from utils.loggerinitializer import *
from distutils.dir_util import mkpath

mkpath(os.getcwd() + "/logs/")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/", logger)


def get_lib_datasets(gi, lib_name, inputs):
    '''

    :param gi: galaxy instance object
    :param lib_name: library name
    :param inputs: list of inputs
    :return: a list of namedtuples file(name id)
    '''

    logger.info("Getting Library id")
    lib_obj = gi.libraries.get_libraries(name=lib_name)

    lib_ids = []

    for item in lib_obj:
        if item['name'] == lib_name and item['deleted'] == False:
            # Put id inside of a list in case there are more than one library with the same name
            lib_ids.append(item['id'])

    logger.info("Getting Library Content")

    f = namedtuple('file', 'name id')
    files = []

    for l_id in lib_ids:
        lib_content_obj = gi.libraries.show_library(library_id=l_id, contents=True)

        logger.info("Getting Files name and Id")
        for item in lib_content_obj:
            if item['type'] == "file" and os.path.basename(item['name']) in inputs:
                logger.info("File(s) in this workflow: " + item['name'])
                lib = f(os.path.basename(item['name']), item['id'])
                files.append(lib)

    return files


def main():
    if len(sys.argv) != 3:
        print "USAGE:\n\tpython {} api_key.txt yaml_file".format(sys.argv[0])
        logging.error("Bad args", exc_info=True)
        sys.exit(1)

    logger.info("############ STARTTING " + sys.argv[0] + " ########")
    api_key = sys.argv[1]
    yaml_file_name = sys.argv[2]

    gi = get_galaxy_instance(api_key, logger)
    yaml_file = read_workflow(yaml_file_name, logger)

    for item in yaml_file:
        datasets = get_lib_datasets(gi, item.lib_name, item.inputs)
        g_workflow = get_workflow_id(gi, item.name, logger)
        g_inputs = workflow_inputs(gi, g_workflow.id, logger)
        input_dict = create_wf_input_dict(gi, datasets, g_inputs, item.inputs, item.input_label, 'ld', logger)

        run_workflow(gi=gi, input=input_dict, history_id=None, history_name=item.name,
                                      workflow_id=g_workflow.id, logger=logger)

    logger.info("Done. Your pipeline must be running on Galaxy")


if __name__ == "__main__":
    main()
