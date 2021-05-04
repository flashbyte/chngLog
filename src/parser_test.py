import unittest
from main import *



class TestCommitHandler(unittest.TestCase):

    def setUp(self):
        self.test_commits = {
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

    def test_parse_commit_summary(self):
        for summary, result in self.test_commits.items():
            self.assertEqual(parse_commit_summary(summary), result)



if __name__ == '__main__':
    unittest.main()
