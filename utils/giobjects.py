from collections import namedtuple
from bioblend import galaxy
import yaml
from pprint import pprint
import sys
from config import *
import os


def create_user(gi, email, logger):
    '''

    :param gi: Galaxy instance object
    :param email: user email (or string representing a email)
    :return: user_id (str)
    '''

    user_obj = gi.users.create_remote_user(user_email=email)

    msg = "USER CREATED: user_name=" + email + " id=" + user_obj['id']
    logger.info(msg)
    return user_obj['id']


def create_api_key(gi, id, logger):
    '''
    :description: Check if a user already has an api_key, if not create one
    :param gi: Galaxy instance object
    :param id: user id
    :return: api key (str)
    '''

    # Check if the user already has an api_key
    api_key = gi.users.get_user_apikey(id)

    # Create one if it does not exists
    if api_key == 'Not available.':
        api_key = gi.users.create_user_apikey(id)

    if len(api_key) <= 1:
        logger.info('api_key does not exists or could not be generated')
        print 'Error: api_key does not exists or could not be generated'
        sys.exit(2)

    return api_key


def delete_user(gi, id, logger):
    '''

    :param gi: Galaxy instance object
    :param id: user id
    :param logger: a logger object
    :return: 0
    '''

    user_obj = gi.users.delete_user(user_id=id, purge=False)
    msg = "DELETED USER: " + user_obj['username']
    logger.info(msg)

    return 0


def get_user(gi, email, logger):
    '''

    :param gi: Galaxy instance object
    :param email: user email (or string representing a email)
    :return: user id (str)
    '''

    user_obj = gi.users.get_users(deleted=False)
    for user in user_obj:
        if user['email'] == email:
            msg = "EXISTING USER REQEUEST: user_name=" + email + " id=" + user['id']
            logger.info(msg)

            return user['id']

    else:
        msg = "User " + email + " is not on the data base. Please check credentials."
        logger.error(msg)
        sys.exit(1)


def get_library_id(gi, name, logger):
    '''

    :param gi: Galaxy instance object
    :param name: library name
    :return: library id (str)
    '''
    lib_obj = gi.libraries.get_libraries(name=name, deleted=False)

    if len(lib_obj) > 0:
        for lib in lib_obj:
            if lib['deleted'] == False and lib['name'] == name:
                lib_obj = lib
                break

    if len(lib_obj['id']) <= 1:
        print 'Error: Library id could not be retrieved'
        logger.error('Library id could not be retrieved')
        sys.exit(2)

    return lib_obj['id']


def get_files_id(gi, lib_id, list_file_names, logger):
    '''
    traverse all the libary tree and get the ids of all datasets that are included in the list of file names
    :param gi: Galaxy instance object
    :param lib_id: library Id
    :param list_file_names: a list containing all the files that will be imported to the history
    :return: a list of library files ids.
    '''

    lib_obj = gi.libraries.show_library(library_id=lib_id, contents=True)

    file_ids = list()

    for item in lib_obj:
        if item['type'] == 'file' and item['name'] in list_file_names:
            file_ids.append(item['id'])
            # print 'name:', item['name'], 'id: ', item['id']

    if len(file_ids) == 0:
        print 'Error: No file found matching file list name'
        logger.error('No file found matching file list name')
        sys.exit(2)

    return file_ids


def upload_from_lib(gi, hist_id, file_id, logger):
    '''

    :param gi: Galaxy instance object
    :param hist_id: history ID
    :param file_id: a list of ids corresponding to the files that will be uploaded to the user's history
    :return:
    '''
    for id in file_id:
        gi.histories.upload_dataset_from_library(history_id=hist_id, lib_dataset_id=id)

    msg = "Files have been uploaded to history"
    logger.info(msg)


def create_history(gi, name=None, logger):
    '''

    :param gi: Galaxy instance object
    :param name: history name
    :return:
    '''

    hist_obj = gi.histories.create_history(name=name)

    if len(hist_obj['id']) <= 1:
        print 'Error: History could not be created'
        logger.error('History could not be created')
        sys.exit(2)

    return hist_obj['id']


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


def safe_galaxy_instance(logger, api_key=None):
    '''
    Safer version of 'get_galaxy_instance'. Credentials are imported as env variables, or passed during run time.
    :param api_key: A galaxy api key to be passed during execution or via env variable (export API_KEY='')
    :return:a galaxy instance object
    '''

    if api_key is None:
        api_key = os.environ['API_KEY']

    gi = galaxy.GalaxyInstance(url=config['g_url'], key=api_key)

    return gi


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
            print "Error: cannot open", api_key


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
            print "Error: " + exc

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
            # label_dict.pop(item.name)

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
