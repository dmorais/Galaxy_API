import argparse
import logging
import os
import pickle
import sys
from distutils.dir_util import mkpath

from bioblend import galaxy
from utils.giobjects import *
from utils.loggerinitializer import *

mkpath(os.getcwd() + "/logs/")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/", logger)


def main():
    parser = argparse.ArgumentParser(
        description="A tool to create binary dictionary of a Galaxy library where the keys are file names"
                    "and the values are file ids")

    parser.add_argument("-l", "--library", action="store",
                        help="Name of the library holding the files.",
                        required=True)

    parser.add_argument("-d", "--dump", default='lib_dump', action="store",
                        help="A path to the directory where de library will be dumped. Default lib_dump",
                        required=False)

    args = parser.parse_args()

    # Admin connection
    gi = safe_galaxy_instance(logger)

    # Get Library id
    logger.info("Getting Lib ID ")
    lib_id = get_library_id(gi, args.library, logger)

    # Get list of file ids
    logger.info("Getting File dictionary")
    file_ids = get_files_id(gi, lib_id, '', logger, 1)

    # Pickling the dictionary
    logger.info("Pickling the dictionary")
    pickle.dump(file_ids, open(args.dump + '/' + args.library + '.pickle', 'wb'))

    logger.info("Done")


if __name__ == '__main__':
    main()
