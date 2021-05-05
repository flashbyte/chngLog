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

# pylint: disable=line-too-long
def parse_commit_summary(summary):

    match = CONVENTIONAL_COMMIT_RE.match(summary)
    if not match:
        return {'type': 'ugly', 'scope': None, 'message': summary}

    return CONVENTIONAL_COMMIT_RE.match(summary).groupdict()


def collect_changelog_from_repo(repo_path):
    #creat branch and pull updats
    repo = git.Repo(repo_path)
    commits = []
    for commit in repo.iter_commits("master", max_count=100):
        parsed = parse_commit_summary(commit.summary)
        parsed['datetime'] = commit.committed_datetime
        commits.append(parsed)
    return commits


def sort_commit(commit_dict_list):
    # Sort by typo priority
    commit_dict_list.sort(key=lambda a: str(a.get('scope')))
    commit_dict_list.sort(key=lambda a: a.get('type'))


def drop_commit_types(commit_dict_list, types):
    for commit in reversed(commit_dict_list):
        if commit['type'] in types:
            commit_dict_list.remove(commit)

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


def drop_commits_before(commit_dict_list, days):
    timezone = commit_dict_list[0]['datetime'].tzinfo
    now = datetime.now(timezone)
    before = now - timedelta(days=days)
    for commit in reversed(commit_dict_list):
        if commit['datetime'] < before:
            commit_dict_list.remove(commit)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository",
        help='directory of the repository',
    )
    parser.add_argument(
        '--exclude-type',
        action='append',
        help='excludes commit types in changelog'
    )

    parser.add_argument(
        '--days',
        help='Create changelog only for the last X days',
        type=int,
    )

    args = parser.parse_args()

    check_args(args)

    commits = collect_changelog_from_repo(args.repository)
    if args.exclude_type:
        drop_commit_types(commits, args.exclude_type)
    if args.days:
        drop_commits_before(commits, args.days)
    sort_commit(commits)
    print(create_markdown_output(commits))


if __name__ == '__main__':
    main()
