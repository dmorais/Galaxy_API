from collections import namedtuple
from bioblend import galaxy
import yaml
import pprint
import sys

def get_history(gi, name=None):
    '''
    :param gi: Galaxy instance object
    :param name: (optional) history name
    :return: a list of namedtuples (name, id)
    '''

    histories = []
    history_obj = gi.histories.get_histories()
    h = namedtuple('history', 'name id')

    for item in history_obj:

        if item['name'] == name:
            hist = h(item['name'], item['id'])
            histories.append(hist)
            break
        else:
            hist = h(item['name'], item['id'])
            histories.append(hist)

    return histories


def get_dataset_id(gi, hist_id):
    '''

    :param gi: galaxy instance object
    :param hist_id: history id
    :return: a dictionary of lists dict[state] = [ list of ids]
    '''

    dataset_obj = gi.histories.show_history(history_id=hist_id)
    return dataset_obj['state_ids']


def get_datset_name(gi, d_id):
    '''

    :param gi: galaxy instance object
    :param d_id: dataset id
    :return: string dataset name
    '''

    data_name_obj = gi.datasets.show_dataset(dataset_id=d_id)
    return data_name_obj['name']


def get_galaxy_instance(api_key, logger):
    '''
    :param api_key:
    :return: a galaxy instance object
    '''
    with open(api_key, 'r') as api:
        try:
            for line in api:
                if line.startswith('#'):
                    continue
                else:
                    url, key = line.strip().split(',')
                    gi = galaxy.GalaxyInstance(url=url, key=key)
                    return gi

        except IOError:
            logger.error('Failed to open file api_key', exc_info=True)
            print "cannot open", api_key


def read_workflow(yaml_file, logger):
    '''
    :param yaml_file:
    :return: workflow_exp: a list of named tuples (can be accessed as objects)
    '''

    workflows = ''
    workflow_exp = []
    with open(yaml_file, 'r') as stream:
        try:
            workflows = yaml.load(stream)

        except yaml.YAMLError as exc:
            logger.error('Failed to open file yaml file', exc_info=True)
            print exc

    # Create namedtuple from dictionary
    for work in workflows:
        workflow_nametup = namedtuple("workflow", work.keys())(*work.values())
        workflow_exp.append(workflow_nametup)

    return workflow_exp



def get_workflow_id(gi, workflow_name, logger, workflow_path=None):
    '''
    :param gi: a galaxy instance object
    :param workflow_name: workflow name (str)
    :param workflow_path: workflow path (str)
    :return: a namedtuples with workflow name, id
    '''
    logger.info("Getting workflow Id")
    work_obj = gi.workflows.get_workflows()

    w = namedtuple('workflow', 'name id')

    if len(work_obj) == 0:
        name, w_id = _upload_workflow(gi, workflow_name, workflow_path)
        work = w(name, w_id)
        return work

    else:
        for item in work_obj:

            if item['name'] == workflow_name or item['name'] == workflow_name + ' (imported from API)':
                work = w(item['name'], item['id'])
                logger.info("Ready to prepare workflow: " + item['name'])
                return work

        # call upload method in and return the workflow name and id
        else:
            name, w_id = _upload_workflow(gi, workflow_name, workflow_path)
            work = w(name, w_id)
            return work


def _upload_workflow(gi, workflow_name, workflow_path, logger):

    logger.info("Uploading new Workflow")
    work_obj = gi.workflows.import_workflow_from_local_path(file_local_path=workflow_path + workflow_name + ".ga")
    return work_obj['name'], work_obj['id']



def workflow_inputs(gi, workflow_id, logger):
    '''
    :param gi:
    :param workflow_id:
    :return: a list of namedtuples of inputs (index, label)
    '''
    logger.info("Getting workflow inputs")
    workflow_input = []
    w = namedtuple('inputs', 'index label')

    work_obj = gi.workflows.show_workflow(workflow_id=workflow_id)

    for k, v in work_obj['inputs'].iteritems():
        w_input = w(k, v['label'])
        workflow_input.append(w_input)

    return workflow_input


def create_wf_input_dict(gi, datasets, inputs, data, labels, src, logger):
    '''
    :param gi: galaxy instance object
    :param datasets: a list of namedtuples with dataset name, id
    :param inputs: a list of namedtuples with workflow inputs index, label
    :param data: a list with the inputs from the yaml file
    :param labels: a list with labels for each input (must be in the same order as the data list)
    :return: a dictionary of dictionary to be used as input in the workflow invocation
    '''

    logger.info("Creating input dictionary")
    input_dict = dict()
    label_dict = dict(zip(data, labels))


    # Map each dataset name to a label
    for item in datasets:
        if item.name in label_dict:
            label_dict[label_dict[item.name]] = item.id
            #label_dict.pop(item.name)

     # Map each index to a label dictionary
    for item in inputs:
        if item.label in label_dict:
            input_dict[item.index] = {
                "id": label_dict[item.label],
                "src": src
            }
    return input_dict


def run_workflow(gi, input, workflow_id, logger, history_id=None, history_name=None):
    '''
    :param gi:
    :param input: a dictionary of dictionary with the inputs of each workflow
    :param history_id:
    :param workflow_id:
    :return: a dictionary with the pipeline invocation.
    '''

    logger.info("Invoking workflow")
    run_work_obj = gi.workflows.invoke_workflow(workflow_id=workflow_id, inputs=input,
                                                history_id=history_id, history_name=history_name)

    return run_work_obj