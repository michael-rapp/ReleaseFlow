from typing import Tuple, Optional

VERSION_FILE = 'VERSION'


def __read_version_file() -> str:
    with open(VERSION_FILE, mode='r') as version_file:
        lines = version_file.readlines()
        
        if len(lines) != 1:
            print('File "' + VERSION_FILE + '" must contain exactly one line')
            exit(-1)

        return lines[0]


def __parse_version(version: str) -> Tuple[str]:
    error_message = 'Version must be given in format MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH.devN, but got: ' + version
    parts = version.split('.')

    if len(parts) < 3 or len(parts) > 4:
        print(error_message)
        exit(-1)

    if len(parts) > 3 and not parts[3].startswith('dev'):
        print(error_message)
        exit(-1)
    
    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])
        dev = int(parts[3][len('dev'):]) if len(parts) > 3 else None
        return major, minor, patch, dev
    except ValueError:
        print(error_message)
        exit(-1)


def __format_version(major: int, minor: int, patch: int, dev: Optional[int]) -> str:
    version = str(major) + '.' + str(minor) + '.' + str(patch)

    if dev:
        version += '.dev' + str(dev)
    
    return version


def __write_version_file(version: str):
    with open(VERSION_FILE, mode='w') as version_file:
        version_file.write(version)


def __get_current_version() -> Tuple[int]:
    current_version = __read_version_file()
    print('Current version is "' + current_version + '"')
    return __parse_version(current_version)


def __update_version(major: int, minor: int, patch: int, dev: Optional[int]):
    updated_version = __format_version(major, minor, patch, dev)
    print('Updated version to "' + updated_version + '"')
    __write_version_file(updated_version)


def drop_development_version():
    major, minor, patch, dev = __get_current_version()
    dev = None
    __update_version(major, minor, patch, dev)


def increment_development_version():
    major, minor, patch, dev = __get_current_version()
    dev = 1 if dev is None else dev + 1
    __update_version(major, minor, patch, dev)


def increment_patch_version():
    major, minor, patch, dev = __get_current_version()
    patch += 1
    dev = None
    __update_version(major, minor, patch, dev)


def increment_minor_version():
    major, minor, patch, dev = __get_current_version()
    minor += 1
    patch = 0
    dev = None
    __update_version(major, minor, patch, dev)


def increment_major_version():
    major, minor, patch, dev = __get_current_version()
    major += 1
    minor = 0
    patch = 0
    dev = None
    __update_version(major, minor, patch, dev)
