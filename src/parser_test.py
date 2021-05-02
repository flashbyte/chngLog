import pytest
from main import parse_commit_summary



class TestCommitHandler:

    def test_parse_commit_summary(self):
        test_commits = {
            'chore(k8s-1.19-prep): bump kube2iam versions': {
                'type': 'chore',
                'scope': 'k8s-1.19-prep',
                'message': 'bump kube2iam versions'
            },
            'fix: Something broken': {
                'type': 'fix',
                'scope': None,
                'message': 'Something broken'
            },
            'refactor(*): It was all ugly': {
                'type': 'refactor',
                'scope': '*',
                'message': 'It was all ugly'
            },
            'This commit is not conform': {
                'type': 'ugly',
                'scope': None,
                'message': 'This commit is not conform',
            }

        }

        for summary, result in test_commits.items():
            assert parse_commit_summary(summary) == result

