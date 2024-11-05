"""
Author: Michael Rapp (michael.rapp.ml@gmail.com)

Provides utility functions for maintaining the project's changelog.
"""
from typing import List, Optional
from enum import Enum, auto
from dataclasses import dataclass, field
from update_version import Version, get_current_version
from datetime import date

PREFIX_HEADER = '# '

PREFIX_SUB_HEADER = '## '

PREFIX_SUB_SUB_HEADER = '### '

PREFIX_DASH = '- '

PREFIX_ASTERISK = '* '

CHANGELOG_FILE_MAIN = '.changelog-main.md'

CHANGELOG_FILE_FEATURE = '.changelog-feature.md'

CHANGELOG_FILE_BUGFIX = '.changelog-bugfix.md'

CHANGELOG_ENCODING = 'utf-8'


class LineType(Enum):
    BLANK = auto()
    HEADER = auto()
    ENUMERATION = auto()

    @staticmethod
    def parse(line: str) -> Optional['LineType']:
        if not line or line.isspace():
            return LineType.BLANK
        if line.startswith(PREFIX_HEADER):
            return LineType.HEADER
        if line.startswith(PREFIX_DASH) or line.startswith(PREFIX_ASTERISK):
            return LineType.ENUMERATION
        return None


@dataclass
class Line:
    line_number: int
    line_type: LineType
    line: str
    content: str


@dataclass
class Changeset:
    header: str
    contents: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        changeset = PREFIX_SUB_SUB_HEADER + self.header + '\n\n'

        for content in self.contents:
            changeset += PREFIX_DASH + content + '\n'

        return changeset


class ReleaseType(Enum):
    MAJOR = 'major'
    MINOR = 'feature'
    PATCH = 'bugfix'


@dataclass
class Release:
    version: Version
    release_date: date
    release_type: ReleaseType
    changesets: List[Changeset] = field(default_factory=list)

    @staticmethod
    def __format_release_month(month: int) -> str:
        return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month - 1]

    @staticmethod
    def __format_release_day(day: int) -> str:
        if 11 <= (day % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(day % 10, 4)]

        return str(day) + suffix

    def __format_release_date(self) -> str:
        return self.__format_release_month(self.release_date.month) + '. ' + self.__format_release_day(
            self.release_date.day) + ', ' + str(self.release_date.year)

    def __str__(self) -> str:
        release = PREFIX_SUB_HEADER + 'Version ' + str(self.version) + ' (' + self.__format_release_date() + ')\n\n'
        release += 'A ' + self.release_type.value + ' release that comes with the following changes.\n\n'

        for i, changeset in enumerate(self.changesets):
            release += str(changeset) + ('\n' if i < len(self.changesets) else '\n\n')

        return release


def __parse_line(changelog_file: str, line_number: int, line: str) -> Line:
    line = line.strip('\n')
    line_type = LineType.parse(line)

    if not line_type:
        print(
            'Line ' + str(line_number) + ' of file "' + changelog_file
            + '" is invalid: Must be blank, a top-level header (starting with "' + PREFIX_HEADER
            + '"), or an enumeration (starting with "' + PREFIX_DASH + '" or "' + PREFIX_ASTERISK
            + '"), but is "' + line + '"')
        exit(-1)

    content = line

    if line_type != LineType.BLANK:
        content = line.lstrip(PREFIX_HEADER).lstrip(PREFIX_DASH).lstrip(PREFIX_ASTERISK)

        if not content or content.isspace():
            print(
                'Line ' + str(line_number) + ' of file "' + changelog_file
                + '" is is invalid: Content must not be blank, but is "' + line + '"')
            exit(-1)

    return Line(line_number=line_number, line_type=line_type, line=line, content=content)


def __validate_line(changelog_file: str, line: Optional[Line], previous_line: Optional[Line]):
    if line and line.line_type == LineType.ENUMERATION and not previous_line:
        print('File "' + changelog_file + '" must start with a top-level header (starting with "'
              + PREFIX_HEADER + '")')
        exit(-1)
    if (line and line.line_type == LineType.HEADER and previous_line and previous_line.line_type == LineType.HEADER) \
            or (not line and previous_line and previous_line.line_type == LineType.HEADER):
        print('Header "' + previous_line.line + '" at line ' + str(previous_line.line_number) + ' of file "' +
              changelog_file + '" is not followed by any content')
        exit(-1)


def __parse_lines(changelog_file: str, lines: List[str]) -> List[Line]:
    previous_line = None
    parsed_lines = []

    for i, line in enumerate(lines):
        current_line = __parse_line(changelog_file=changelog_file, line_number=(i + 1), line=line)

        if current_line.line_type != LineType.BLANK:
            __validate_line(changelog_file=changelog_file, line=current_line, previous_line=previous_line)
            previous_line = current_line
            parsed_lines.append(current_line)

    __validate_line(changelog_file=changelog_file, line=None, previous_line=previous_line)
    return parsed_lines


def __read_lines(changelog_file: str) -> List[str]:
    with open(changelog_file, mode='r', encoding=CHANGELOG_ENCODING) as file:
        return file.readlines()


def __write_lines(changelog_file: str, lines: List[str]):
    with open(changelog_file, mode='w', encoding=CHANGELOG_ENCODING) as file:
        file.writelines(lines)


def __parse_changesets(changelog_file: str) -> List[Changeset]:
    changesets = []
    lines = __parse_lines(changelog_file, __read_lines(changelog_file))

    for line in lines:
        if line.line_type == LineType.HEADER:
            changesets.append(Changeset(header=line.content))
        elif line.line_type == LineType.ENUMERATION:
            current_changeset = changesets[-1]
            current_changeset.contents.append(line.content)

    return changesets


def __merge_changesets(*changelog_files) -> List[Changeset]:
    changesets_by_header = {}

    for changelog_file in changelog_files:
        for changeset in __parse_changesets(changelog_file):
            merged_changeset = changesets_by_header.setdefault(changeset.header.lower(), changeset)

            if merged_changeset != changeset:
                merged_changeset.contents.extend(changeset.contents)

    return list(changesets_by_header.values())


def __create_release(release_type: ReleaseType, *changelog_files) -> Release:
    return Release(version=get_current_version(), release_date=date.today(), release_type=release_type,
                   changesets=__merge_changesets(*changelog_files))


def __add_release_to_changelog(changelog_file: str, new_release: Release):
    original_lines = __read_lines(changelog_file)
    modified_lines = []
    offset = 0

    for offset, line in enumerate(original_lines):
        if line.startswith(PREFIX_SUB_HEADER):
            break

        modified_lines.append(line)

    modified_lines.append(str(new_release))
    modified_lines.extend(original_lines[offset:])
    __write_lines(changelog_file, modified_lines)


def __update_changelog(release_type: ReleaseType, *changelog_files):
    new_release = __create_release(release_type, *changelog_files)
    __add_release_to_changelog('CHANGELOG.md', new_release)


def validate_changelog_main():
    __parse_changesets(CHANGELOG_FILE_MAIN)


def validate_changelog_feature():
    __parse_changesets(CHANGELOG_FILE_FEATURE)


def validate_changelog_bugfix():
    __parse_changesets(CHANGELOG_FILE_BUGFIX)


def update_changelog_main():
    __update_changelog(ReleaseType.MAJOR, CHANGELOG_FILE_MAIN, CHANGELOG_FILE_FEATURE, CHANGELOG_FILE_BUGFIX)


def update_changelog_feature():
    __update_changelog(ReleaseType.MINOR, CHANGELOG_FILE_FEATURE, CHANGELOG_FILE_BUGFIX)


def update_changelog_bugfix():
    __update_changelog(ReleaseType.PATCH, CHANGELOG_FILE_BUGFIX)
