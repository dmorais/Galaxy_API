import random
import sys
import string

# num = range(0,10)
# num = map(str, num)
char = list(string.ascii_letters) + map(str, range(0,9))


def create_random_email():
    """
    :return: a random string that can be used and email to create new users
    """
    user_id = ''.join([random.choice(char) for i in range(9)])
    return user_id + '@galaxy.genap.ca'


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
