import argparse
import sys
from collections import namedtuple
from bioblend import galaxy
import os
import logging
import pprint
import json
from utils.loggerinitializer import *
from utils.giobjects import *
from utils.util import create_random_email, create_random_password, read_file, parse_samples
from distutils.dir_util import mkpath
import subprocess
from datetime import datetime

# Logs
mkpath(os.getcwd() + "/logs/")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/", logger)


def main():
    # option parser
    parser = argparse.ArgumentParser(
        description="A tool to create user on Galaxy and transfer IHEC datasets to the user history")
    parser.add_argument("-s", "--samples", action="store",
                        help="File with the sample's Library path",
                        required=False)

    parser.add_argument("-d", "--delete", action="store",
                        help="Id of the user to be deleted",
                        required=False)

    parser.add_argument("-e", "--email", action="store",
                        help="User email on Galaxy (if user is already registered)",
                        required=False)

    parser.add_argument("-his", "--history_id", action="store",
                        help="A Galaxy history id. If provided the files will be uploaded to this history.",
                        required=False)

    parser.add_argument("-l", "--library", action="store",
                        help="Name of the library holding the files.",
                        required=True)

    args = parser.parse_args()

    # Parse samples
    if args.samples is not None:
        sample_names = parse_samples(read_file(args.samples))

        if len(set(sample_names)) <= 1 and len(sample_names[0]) == 0:
            logger.error("# No samples in the sample file #")
            sys.exit(2)
    else:
        stdin = sys.stdin.read().strip()
        if stdin == '':
            logger.error('no --samples provided and empty stdin')
            sys.exit(2)
        sample_names = parse_samples(stdin)

    user_id = ''
    user_api_key = ''
    email = ''
    user_hist_id = ''

    logger.info("# NEW REQUEST #")

    # Admin connection
    gi = safe_galaxy_instance(logger)

    # Get Library id
    lib_id = get_library_id(gi, args.library, logger)

    # Get list of file ids
    file_id = get_files_id(gi, lib_id, sample_names, logger)

    if args.delete:
        delete_user(gi, args.delete, logger)
        sys.exit()

    # if user exists get his id and check for his  API key (or create one)
    if args.email:
        user_id = get_user(gi, args.email, logger)
        user_api_key = create_api_key(gi, user_id, logger)
        email = args.email

    # Create email, password, user account and API key
    else:
        email = create_random_email()
        user_id = create_user(gi, email, logger)

        # print "user id: ", user_id
        user_api_key = create_api_key(gi, user_id, logger)

    # User connection
    gi_user = safe_galaxy_instance(logger, api_key=user_api_key)

    # create history
    if args.history_id:
        user_hist_id = args.history_id
    else:
        now = datetime.now().strftime("%Y-%m-%d_%H:%M")
        user_hist_id = create_history(gi_user, logger, args.library + '_' + now)

    # Upload files to history
    upload_from_lib(gi_user, user_hist_id, file_id, logger)

    # Create random proxy password for user
    password = create_random_password()

    # create proxy pass
    command = 'sh /proxydata/adduser.sh ' + email + ' ' + password
    url = subprocess.check_output(command, shell=True)

    print json.dumps({ 'url': url, 'emai': email, 'history_id': user_hist_id, 'user_id': user_id })



if __name__ == '__main__':
    main()
