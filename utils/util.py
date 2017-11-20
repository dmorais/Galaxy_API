import random
import sys
import string

# num = range(0,10)
# num = map(str, num)
char = list(string.ascii_letters) + map(str, range(0,9))



def create_random_email():
    '''

    :return: a random string that can be used and email to create new users
    '''

    email = ''.join([random.choice(char) for i in range(9)])
    return email


def create_random_password():

    password = ''.join([random.choice(char) for i in range(15)])
    return password

def parse_samples(file_name):

    sample_names = list()
    try:
        with open(file_name, 'r') as f:
            for line in f:
                sample_names.append(line.strip())

    except IOError:
        print "Could not read file:", file_name
        sys.exit(1)

    return  sample_names