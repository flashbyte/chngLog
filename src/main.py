#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse
import re
import os
import sys
import git

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

CONVENTIONAL_COMMIT_RE = re.compile(
    r'(?P<type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\((?P<scope>[\*\.\-\w]*)\))?: (?P<message>.*)'
)

class Repo:
    """docstring for Repo"""
    def __init__(self, path):
        super(Repo, self).__init__()
        self.path = path
        self.repo = git.Repo(path)
        self.commits = []
        self.collect_changelog_from_repo()

    def collect_changelog_from_repo(self):
        #creat branch and pull updats
        for commit in self.repo.iter_commits("master", max_count=100): # FIXME: remove max_count
            parsed = self.parse_commit_summary(commit.summary)
            parsed['datetime'] = commit.committed_datetime
            self.commits.append(parsed)

    # pylint: disable=line-too-long
    def parse_commit_summary(self, summary):

        match = CONVENTIONAL_COMMIT_RE.match(summary)
        if not match:
            return {'type': 'ugly', 'scope': None, 'message': summary}

        return CONVENTIONAL_COMMIT_RE.match(summary).groupdict()

    def sort_commit(self):
        # TODO: Sort by typo priority
        self.commits.sort(key=lambda a: str(a.get('scope')))
        self.commits.sort(key=lambda a: a.get('type'))

    def drop_commit_types(self, types):
        for commit in reversed(self.commits):
            if commit['type'] in types:
                self.commits.remove(commit)

    def drop_commits_before(self, days):
        timezone = self.commits[0]['datetime'].tzinfo
        now = datetime.now(timezone)
        before = now - timedelta(days=days)
        for commit in reversed(self.commits):
            if commit['datetime'] < before:
                self.commits.remove(commit)


def create_markdown_output(commit_dict_list):
    if not commit_dict_list:
        return None

    commit_type = commit_dict_list[0]['type']
    output = SECTION_MARKDOWN.format(c_type=commit_type)
    for commit in commit_dict_list:
        if commit["type"] != commit_type:
            commit_type = commit["type"]
            output += SECTION_MARKDOWN.format(c_type=commit_type)
        if commit['scope']:
            output += COMMIT_MARKDOWN.format(c_scope=commit['scope'], c_message=commit['message'])
        else:
            output += COMMIT_MARKDOWN.format(c_scope='', c_message=commit['message'])
    return output

# Sanity checks for cli input arguments
def check_args(args):

    # Direcorty existes?
    if not os.path.exists(args.repository):
        sys.exit('Path {} does not exist!!!'.format(args.repository))
    # Directory is a git repo?
    try:
        git.Repo(args.repository)
    except git.exc.InvalidGitRepositoryError:
        sys.exit('Path {} not a valid git repository!!!'.format(args.repository))

    # Check if days only positive
    if args.days and args.days < 0:
        sys.exit('arg days must be positive')


def handle_cli_args():
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

    r = Repo(args.repository)
    commits = r.commits
    if args.exclude_type:
        r.drop_commit_types(args.exclude_type)
    if args.days:
        r.drop_commits_before(args.days)
    r.sort_commit()
    print(create_markdown_output(commits))


if __name__ == '__main__':
    main()
