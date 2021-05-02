#!/usr/bin/env python3
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
    r'(?P<type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\((?P<scope>[\.\-\w]*)\))?: (?P<message>.*)'
)


# TODO: remove unwanted commits e.g. 'apply succeded'
# TODO: Pull updates
# TODO: create report branch and commit changelog
# TODO: selcet tiemframe / tags
# TODO: select branch

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
        commits.append(parse_commit_summary(commit.summary))
    return commits


def sort_commit(commit_dict_list):
    # Sort by typo priority
    commit_dict_list.sort(key=lambda a: str(a.get('scope')))
    commit_dict_list.sort(key=lambda a: a.get('type'))


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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository",
        help='directory of the repository',
    )
    args = parser.parse_args()

    check_args(args)

    commits = collect_changelog_from_repo(args.repository)
    sort_commit(commits)
    print(create_markdown_output(commits))


if __name__ == '__main__':
    main()
