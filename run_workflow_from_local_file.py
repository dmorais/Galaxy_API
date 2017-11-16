############################################################
# This script test a workflow in a given Galaxy instance
#
#    1- It reads the api-key.txt file (a csv) with two fields
#         url (galaxy address),key ( Galaxy AI key)
#    2- It reads a yaml file with the workflow name and inputs
#    3- It creates a history
#    4- Upload the inputs
#    5- Upload the workflow
#    6- Get the workflow id and inputs
#    7- builds the input dictionary
#    8- runs the workflow
#
# UNFORTUNATELY a locally uploaded workflow will fail because
# Galaxy resets the input label (or name depending on the version) back to input dataset
# In this case open the workflow editor in Galaxy and rename the label (or name) of the inputs
# So it matches the label in the yaml file.
##############################################

import sys
from collections import namedtuple
from bioblend import galaxy
import pprint
import os
import logging
from utils.giobjects import *
from utils.loggerinitializer import *
from distutils.dir_util import mkpath

mkpath(os.getcwd() + "/logs/")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/", logger)


def create_history(gi, name):
    '''
    :param gi: a  galaxy instance object
    :param name: history name
    :return: namedtuple with a (hist_name,hist_id)
    '''
    logger.info("Creating history")
    data = namedtuple("history", 'name id')

    hist_obj = gi.histories.create_history(name=name)
    history = data(hist_obj['name'], hist_obj['id'])

    return history


def upload_file(gi, input, input_path, hist_id, dbkey=None):
    '''
    :param gi: a galaxy instance object
    :param input: a list of input files
    :param hist_id: history ID
    :param dbkey: a list of dbkey (optional)
    :return: A list of namedtuples with dataset (name,id)
    '''
    logger.info("Uploading file to Galaxy")
    dataset = []

    for i in range(len(input)):
        if len(dbkey) > i:
            file_obj = gi.tools.upload_file(path=input_path + input[i], history_id=hist_id, dbkey=dbkey[i])
        else:
            file_obj = gi.tools.upload_file(path=input_path + input[i], history_id=hist_id)

        d = namedtuple('dataset', 'name id')
        data = d(file_obj['outputs'][0]['name'], file_obj['outputs'][0]['id'])
        dataset.append(data)

    return dataset


def main():
    if len(sys.argv) != 3:
        print "USAGE:\n\tpython {} api_key.txt yaml_file".format(sys.argv[0])
        logging.error("Bad args", exc_info=True)
        sys.exit(1)

    logger.info("############")
    api_key = sys.argv[1]
    yaml_file_name = sys.argv[2]

    gi = get_galaxy_instance(api_key, logger)
    yaml_file = read_workflow(yaml_file_name, logger)

    # Loop through workflows in the yaml file
    for pipeline in yaml_file:
        history = create_history(gi, pipeline.name)
        datasets = upload_file(gi, pipeline.inputs, pipeline.inputs_path, history.id, pipeline.dbkey)
        g_workflow = get_workflow_id(gi, pipeline.name, logger, pipeline.workflow_path)
        g_inputs = workflow_inputs(gi, g_workflow.id, logger)
        input_dict = create_wf_input_dict(gi, datasets, g_inputs, pipeline.inputs, pipeline.inputs_label, 'hda', logger)
        run_workflow(gi=gi, input=input_dict, history_id=history.id, history_name=None,
                                      workflow_id=g_workflow.id, logger=logger)

    logger.info("DONE, check history when workflow completes")


if __name__ == "__main__":
    main()
