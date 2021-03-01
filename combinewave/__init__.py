import sys

version = sys.version_info[0:2]
#print(version)
if version < (3,6):
    raise RuntimeError(
        'Python 3.6 or above is needed, this is {0}.{1}'.format(
            version[0], version[1]))
