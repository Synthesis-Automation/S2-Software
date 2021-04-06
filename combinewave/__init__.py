import sys
from combinewave.parameters import VERSION, SYSTEM_NAME

print(SYSTEM_NAME, VERSION)

version = sys.version_info[0:2]
if version < (3,6):
    raise RuntimeError(
        'Python 3.6 or above is needed, this is {0}.{1}'.format(
            version[0], version[1]))

