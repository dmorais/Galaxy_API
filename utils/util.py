import random
import sys
import string
import pickle

# num = range(0,10)
# num = map(str, num)
char = list(string.ascii_letters) + map(str, range(0,9))


def create_random_email():
    """
    :return: a random string that can be used and email to create new users
    """
    email = ''.join([random.choice(char) for i in range(9)])
    return email + '@galaxy.genap.ca'


def create_random_password():
    password = ''.join([random.choice(char) for i in range(15)])
    return password

def read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except IOError:
        print 'Error: could not read file:', file_path
        sys.exit(1)

def parse_samples(content):
    return [line.strip() for line in content.split('\n')]


def get_file_id_from_pickle(lib_name, lib_dir, sample_names, logger):

    ditc_ids = ''
    file_id = list()

    try:
        dict_ids = pickle.load(open(lib_dir + '/' + lib_name + '.pickle', 'rb'))

        for sample in sample_names:
            if len(sample) > 1 and dict_ids.get(sample) is not None:
                file_id.append(dict_ids[sample])

    except IOError:
        logger.error('No Library with the specified name.')
        sys.exit(2)

    if len(file_id) < 1:
        logger.error('Sample name do not match Libary sample names.')
        sys.exit(2)

    return file_id

