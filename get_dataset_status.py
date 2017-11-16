# Get status of all datasets in all histories of a Galaxy  instance
import sys
from distutils.dir_util import mkpath

from utils.giobjects import *
from utils.loggerinitializer import *

mkpath(os.getcwd() + "/logs/")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/", logger)


def main():
    if len(sys.argv) != 2:
        print "USAGE:\n\tpython {} api_key.txt".format(sys.argv[0])
        logging.error("Bad args", exc_info=True)
        sys.exit(1)

    logger.info("############ STARTING " + sys.argv[0] + " #############")
    gi = get_galaxy_instance(sys.argv[1], logger)

    histories = get_history(gi)
    metadata = {}

    logger.info("Getting Datasets states and ids")
    for history in histories:
        dataset_id = get_dataset_id(gi, history.id)
        metadata[history.name + "_" + history.id] = dataset_id

    logger.info("Getting Datasets names")
    for hist, states in metadata.iteritems():
        print "\n", hist
        for state, id in sorted(states.iteritems(), reverse=True):
            if (state == 'ok' or state == 'discarded' or state == 'error' or state == 'running') and len(state) > 0:
                print state

                for data_id in id:
                    print "\t", data_id, "\t", get_datset_name(gi, data_id)

        print "\n"

    logger.info("DONE")


if __name__ == '__main__':
    main()
