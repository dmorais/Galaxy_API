import sys
from collections import namedtuple
from bioblend import galaxy
import os
from utils.giobjects import *
from utils.loggerinitializer import *
import logging
from distutils.dir_util import mkpath


mkpath(os.getcwd() + "/logs/download")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/download", logger)


def prepare_download(gi, histories):
    '''
    :param gi: Galaxy instance object
    :param histories: a list of namedtuples history (name, id)
    :return: a list of namedtuple jeha (id, name, jeha). The id and name are from the history.
    '''

    jeha_id = []
    j = namedtuple("jeha", "id name jeha")

    logger.info("Preparing Download Link")

    for item in histories:
        expo_hist_obj = gi.histories.export_history(history_id=item.id, gzip=True, include_deleted=False, include_hidden= False,
                                                wait=True)
        jeha = j(item.id, item.name, expo_hist_obj)
        jeha_id.append(jeha)

    return jeha_id


def downlad_history(gi, history_id, jeha_id, outf):
    '''
    :param gi:  Galaxy instance object
    :param history_id: history id
    :param jeha_id:  jeha id
    :param outf: output file object open on wb mode
    :return: a string
    '''

    logger.info("Downlaoding history")
    gi.histories.download_history(history_id=history_id, jeha_id=jeha_id, outf=outf, chunk_size=4096)

    return "DONE"


def main():
    if len(sys.argv) < 2:
        print "USAGE:\n\tpython {} api_key.txt <history name (optional) >\n\n\tNOTE: if not history name is given" \
              " all histories will be downloaded".format(sys.argv[0])
        sys.exit(1)

    logger.info("############")
    apiFile = open(sys.argv[1])
    url, key = apiFile.read().strip().split(',')

    gi = galaxy.GalaxyInstance(url=url, key=key)

    logger.info("Getting history IDs")
    hist_name = None if len(sys.argv) < 3 else sys.argv[2]
    histories = get_history(gi, hist_name)

    logger.info("Creating the Download dir (if necessary)")
    down_dir = os.getcwd() + "/download"
    mkpath(os.getcwd() + "/download")

    jehas = prepare_download(gi, histories)

    for item in jehas:
        dfile = open(down_dir + "/" + item.name + ".tar.gz", "wb")
        dhist = downlad_history(gi, item.id, item.jeha, dfile)

        logger.info("The Download of {} is {}".format(item.name, dhist))
        dfile.close()


if __name__ == "__main__":
    main()
