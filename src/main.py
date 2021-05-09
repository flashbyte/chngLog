#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse
import re
import os
import sys
import git
from git.exc import InvalidGitRepositoryError

SECTION_MARKDOWN = '\n## {c_type}\n'
COMMIT_MARKDOWN = '* {c_scope:18} {c_message} \n'

# Valid commit tpye in order of priority
VALID_COMMIT_TYPES = [
    'feat',
    'revert',
    'fix',
    'chore',
    'build',
    'ci',
    'perf',
    'refactor',
    'docs',
    'style',
    'test'
]

# pylint: disable=line-too-long
CONVENTIONAL_COMMIT_RE = re.compile(
    r'(?P<type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\((?P<scope>[\*\.\-\w]*)\))?: (?P<message>.*)'
)


def parse_commit_summary(summary):
    """Parses a commit summary and return a dictionary with type, scope and message.

    Args:
      summary: str

    Returns:
      parsed commit(dict) : dict with keys type,commit and message

    """
    match = CONVENTIONAL_COMMIT_RE.match(summary)
    if not match:
        return {'type': 'ugly', 'scope': None, 'message': summary}

    return CONVENTIONAL_COMMIT_RE.match(summary).groupdict()


class Repo:
    """TODO: Some usefull docs"""

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.repo = git.Repo(path)
        self.commits = []
        self.__collect_changelog_from_repo()

    def __collect_changelog_from_repo(self):
        """Collect commits and parses them"""
        # Todo: creat branch and pull updats
        # FIXME: remove max_count
        for commit in self.repo.iter_commits("master", max_count=100):
            parsed = parse_commit_summary(commit.summary)
            parsed['datetime'] = commit.committed_datetime
            self.commits.append(parsed)

    def sort_commit(self):
        """Sort commits by scope and type"""
        # TODO: Sort by typo priority
        self.commits.sort(key=lambda a: str(a.get('scope')))
        self.commits.sort(key=lambda a: a.get('type'))

    def drop_commit_types(self, types):
        """Removes commit with given types

        Args:
          types: list of types to remove

        """
        for commit in reversed(self.commits):
            if commit['type'] in types:
                self.commits.remove(commit)

    def drop_commits_before(self, days):
        """Removes commits for the last X days

        Args:
          days: int

        """
        timezone = self.commits[0]['datetime'].tzinfo
        now = datetime.now(timezone)
        before = now - timedelta(days=days)
        for commit in reversed(self.commits):
            if commit['datetime'] < before:
                self.commits.remove(commit)


def create_markdown_output(commit_dict_list):
    """

    Args:
      commit_dict_list:

    Returns:

    """
    if not commit_dict_list:
        return None

    commit_type = commit_dict_list[0]['type']
    output = SECTION_MARKDOWN.format(c_type=commit_type)
    for commit in commit_dict_list:
        if commit["type"] != commit_type:
            commit_type = commit["type"]
            output += SECTION_MARKDOWN.format(c_type=commit_type)
        if commit['scope']:
            output += COMMIT_MARKDOWN.format(
                c_scope=commit['scope'], c_message=commit['message'])
        else:
            output += COMMIT_MARKDOWN.format(c_scope='',
                                             c_message=commit['message'])
    return output

#


def check_args(args):
    """Sanity checks for cli input arguments
    Args:
      args:

    """

    # Direcorty existes?
    if not os.path.exists(args.repository):
        sys.exit('Path {} does not exist!!!'.format(args.repository))
    # Directory is a git repo?
    try:
        git.Repo(args.repository)
    except InvalidGitRepositoryError:
        sys.exit('Path {} not a valid git repository!!!'.format(args.repository))

    # Check if days only positive
    if args.days and args.days < 0:
        sys.exit('arg days must be positive')


def handle_cli_args():
    """Creates cli params"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository",
        help='directory of the repository',
    )
    parser.add_argument(
        '-et', '--exclude-type',
        action='append',
        help='excludes commit types in changelog'
    )

    parser.add_argument(
        '-d', '--days',
        help='Create changelog only for the last X days',
        type=int,
    )

    args = parser.parse_args()

    check_args(args)
    return args


def main():
    args = handle_cli_args()

    repository = Repo(args.repository)
    commits = repository.commits
    if args.exclude_type:
        repository.drop_commit_types(args.exclude_type)
    if args.days:
        repository.drop_commits_before(args.days)
    repository.sort_commit()
    print(create_markdown_output(commits))


if __name__ == '__main__':
    main()
