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

PREFIX_DASH = '- '

PREFIX_ASTERISK = '* '

CHANGELOG_FILE_MAIN = '.changelog-main.md'

CHANGELOG_FILE_FEATURE = '.changelog-feature.md'

CHANGELOG_FILE_BUGFIX = '.changelog-bugfix.md'


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
        changeset = '# ' + self.header + '\n\n'

        for content in self.contents:
            changeset += '- ' + content + '\n'

        return changeset


@dataclass
class Release:
    version: Version
    release_date: date
    changesets: List[Changeset] = field(default_factory=list)


@dataclass
class Changelog:
    releases: List[Release] = field(default_factory=list)


def __parse_line(changelog_file: str, line_number: int, line: str) -> Line:
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
        line = line.strip('\n')
        current_line = __parse_line(changelog_file=changelog_file, line_number=(i + 1), line=line)

        if current_line.line_type != LineType.BLANK:
            __validate_line(changelog_file=changelog_file, line=current_line, previous_line=previous_line)
            previous_line = current_line
            parsed_lines.append(current_line)

    __validate_line(changelog_file=changelog_file, line=None, previous_line=previous_line)
    return parsed_lines


def __read_lines(changelog_file: str) -> List[str]:
    with open(changelog_file, mode='r', encoding='utf-8') as file:
        return file.readlines()


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


def __create_release(*changelog_files) -> Release:
    return Release(version=get_current_version(), release_date=date.today(),
                   changesets=__merge_changesets(*changelog_files))


def __parse_changelog(changelog_file: str) -> Changelog:
    lines = __read_lines(changelog_file)
    lines = __parse_lines(changelog_file=changelog_file, lines=lines)
    return Changelog()


def validate_changelog_main():
    __parse_changesets(CHANGELOG_FILE_MAIN)


def validate_changelog_feature():
    __parse_changesets(CHANGELOG_FILE_FEATURE)


def validate_changelog_bugfix():
    __parse_changesets(CHANGELOG_FILE_BUGFIX)


def update_changelog_main():
    release = __create_release(CHANGELOG_FILE_MAIN, CHANGELOG_FILE_FEATURE, CHANGELOG_FILE_BUGFIX)
    print(str(release))


def update_changelog_feature():
    release = __create_release(CHANGELOG_FILE_FEATURE, CHANGELOG_FILE_BUGFIX)
    print(str(release))


def update_changelog_bugfix():
    release = __create_release(CHANGELOG_FILE_BUGFIX)
    print(str(release))
