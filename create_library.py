# This script create a Galaxy Library with subfolders
# and uploads datasets to them


import sys
from collections import namedtuple
from bioblend import galaxy
import os
import logging
from utils.giobjects import *
from utils.loggerinitializer import *
from distutils.dir_util import mkpath


mkpath(os.getcwd() + "/logs/")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/", logger)



def create_libary(gi, name, description):
    '''

    :param gi: Galaxy instance object
    :param name: Library name
    :param description: description of the library
    :return: a namedtuple library(id, name)
    '''

    # Check if library already exists
    logger.info("Check if library already exists")
    lib_obj = gi.libraries.get_libraries(name=name, deleted=False)

    # because bioblend is returning deleted libs, check if the object is empty and if not
    # check if the status deleted of each lib is True or False
    # If there is one False pass this dict to lob_obj and leave the loop
    # Otherwise create the lib, (note the else belongs to the for)

    if len(lib_obj) > 0:
        for lib in lib_obj:
            if lib['deleted']==False and lib['name']==name:
                logger.info("Library already exists")
                lib_obj = lib
                break

        else:
            logger.info("Creating Library")
            lib_obj = gi.libraries.create_library(name=name, description=description)


    l = namedtuple('library', 'id name')
    library = l(lib_obj['id'], lib_obj['name'])

    return library


def create_folder(gi, lib_id, name):
    '''
    :param gi: Galaxy instance object
    :param lib_id: library id
    :param name: Library folder name
    :return: a namedtuple folder(id, name)
    '''

    dir_struc = name.split(os.sep)
    base_folder_id = None
    folder = ''
    base_dir_name = '/'

    for dir_name in dir_struc:

        base_dir_name = os.path.join(base_dir_name, dir_name)

        logger.info("Cheking if folder " + dir_name +  " exists")
        folder_obj = gi.libraries.get_folders(lib_id, name=base_dir_name)

        if len(folder_obj) == 0:

            logger.info("Creating folder " + base_dir_name )

            folder_obj = gi.libraries.create_folder(library_id=lib_id,
                                                    folder_name=dir_name,
                                                    base_folder_id=base_folder_id)

        else:
            logger.info("Folder " + base_dir_name +  " already exists")

        f = namedtuple('folder', 'id name')
        folder = f(folder_obj[0]['id'], folder_obj[0]['name'])
        base_folder_id = folder.id

    return folder


def upload_from_local(gi, lib_id, path, datasets, folder_id):
    '''

    :param gi: Galaxy instance object
    :param lib_id: library id
    :param path: path to files
    :param datasets: List of datasets to be uploaded
    :param folder_id: Library folder id
    :return:
    '''

    logger.info("Uploading Files")

    for dataset in datasets:
        up_obj = gi.libraries.upload_file_from_local_path(library_id=lib_id,
                                                          file_local_path=path + '/' + dataset,
                                                          folder_id=folder_id)
        logger.info("Uploaded File:" + dataset)


def upload_from_url(gi, lib_id, urls, folder_id):
    '''

    :param gi: Galaxy instance object
    :param lib_id: library id
    :param urls: list of urls with the files to be uploaded
    :param folder_id: Folder id
    :return:
    '''

    logger.info("Uploading Files")

    for url in urls:
        up_obj = gi.libraries.upload_file_from_url(library_id=lib_id,
                                                   file_url=url,
                                                   folder_id=folder_id)

        logger.info("Uploaded File:" + url)


def upload_from_server(gi, lib_id, server_dir, folder_id):
    '''
    :param gi: Galaxy instance object
    :param lib_id: library id
    :param server_dir: full path on the server to where the datasets are
    :param folder_id: Folder id
    :return:
    '''


    logger.info("Linking files on the server")

    up_obj = gi.libraries.upload_file_from_server(library_id=lib_id,
                                                  server_dir=server_dir,
                                                  folder_id=folder_id,
                                                  link_data_only='link_to_files')

    logger.info("Files have been linked to:" + server_dir)



def main():

    if len(sys.argv) != 3:
        print "USAGE:\n\tpython {} api_key.txt yaml_file".format(sys.argv[0])
        logging.error("Bad args", exc_info=True)
        sys.exit(1)

    logger.info("############ STARTING " + sys.argv[0] + '#############')

    api_key = sys.argv[1]
    yaml_file_name = sys.argv[2]

    gi = get_galaxy_instance(api_key,logger)
    yaml_file = read_workflow(yaml_file_name,logger)


    for item in yaml_file:

        library = create_libary(gi, item.name, item.description)

        folder = create_folder(gi, library.id, item.folder)

        if item.server_dir:
            upload_from_server(gi, library.id, item.server_dir, folder.id)

        elif len(item.inputs) > 0:
            upload_from_local(gi, library.id, item.input_path, item.inputs, folder.id)

        else:
            upload_from_url(gi, library.id, item.urls, folder.id)

    logger.info("Done")

if __name__ =="__main__":
    main()

