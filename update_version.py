from dataclasses import dataclass
from typing import Optional

VERSION_FILE = 'VERSION'


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    dev: Optional[int] = None

    def __str__(self) -> str:
        version = str(self.major) + '.' + str(self.minor) + '.' + str(self.patch)

        if self.dev:
            version += '.dev' + str(self.dev)

        return version


def __read_version_file() -> str:
    with open(VERSION_FILE, mode='r') as version_file:
        lines = version_file.readlines()

        if len(lines) != 1:
            print('File "' + VERSION_FILE + '" must contain exactly one line')
            exit(-1)

        return lines[0]


def __parse_version(version: str) -> Version:
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
        return Version(major=major, minor=minor, patch=patch, dev=dev)
    except ValueError:
        print(error_message)
        exit(-1)


def __write_version_file(version: str):
    with open(VERSION_FILE, mode='w') as version_file:
        version_file.write(version)


def __get_current_version() -> Version:
    current_version = __read_version_file()
    print('Current version is "' + current_version + '"')
    return __parse_version(current_version)


def __update_version(version: Version):
    updated_version = str(version)
    print('Updated version to "' + updated_version + '"')
    __write_version_file(updated_version)


def get_current_version() -> Version:
    return __parse_version(__read_version_file())


def print_current_version():
    return print(str(get_current_version()))


def drop_development_version():
    version = __get_current_version()
    version.dev = None
    __update_version(version)


def increment_development_version():
    version = __get_current_version()
    version.dev = 1 if version.dev is None else version.dev + 1
    __update_version(version)


def increment_patch_version():
    version = __get_current_version()
    version.patch += 1
    version.dev = None
    __update_version(version)


def increment_minor_version():
    version = __get_current_version()
    version.minor += 1
    version.patch = 0
    version.dev = None
    __update_version(version)


def increment_major_version():
    version = __get_current_version()
    version.major += 1
    version.minor = 0
    version.patch = 0
    version.dev = None
    __update_version(version)
