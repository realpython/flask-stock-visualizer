import os

from werckercli.tests import (
    DataSetTestCase,
    TestCase,
    VALID_GITHUB_SSH_URL,
    VALID_GITHUB_HTTPS_URL,
    VALID_BITBUCKET_SSH_URL,
    VALID_BITBUCKET_HTTPS_URL,
    VALID_HEROKU_SSH_URL,
)

from werckercli.git import (
    get_priority,
    get_remote_options,
    get_source_type_pattern,
    get_username,
    find_heroku_sources,
    convert_to_url,

    GITHUB_PATTERNS,
    BITBUCKET_PATTERNS,
    HEROKU_PATTERNS,

    SOURCE_GITHUB,
    SOURCE_BITBUCKET,
    SOURCE_HEROKU
)


class GetPriorityTests(TestCase):
    BITBUCKET_URL = VALID_BITBUCKET_SSH_URL
    GITHUB_URL = VALID_GITHUB_SSH_URL
    GITHUB_URL_HTTPS = VALID_GITHUB_HTTPS_URL
    BITBUCKET_URL_HTTPS = VALID_BITBUCKET_HTTPS_URL
    HG_SSH_URL = "ssh://hg@bitbucket.org/pypy/pypy"
    HG_HTTPS_URL = "https://bitbucket.org/pypy/pypy"

    def test_priority_two(self):

        result = get_priority(self.BITBUCKET_URL, "origin")
        self.assertEqual(result, 2)

        result = get_priority(self.GITHUB_URL, "origin")
        self.assertEqual(result, 2)

        result = get_priority(self.BITBUCKET_URL_HTTPS, "origin")
        self.assertEqual(result, 2)

        result = get_priority(self.GITHUB_URL_HTTPS, "origin")
        self.assertEqual(result, 2)

    def test_priority_one(self):
        result = get_priority(self.BITBUCKET_URL, "some_upstream")
        self.assertEqual(result, 1)

        result = get_priority(self.GITHUB_URL, "some_upstream")
        self.assertEqual(result, 1)

        result = get_priority(
            self.GITHUB_URL,
            "origin",
            prio_remote="not_origin"
        )

        self.assertEqual(result, 1)

    def test_priority_zero(self):
        result = get_priority(self.HG_SSH_URL, "origin")
        self.assertEqual(result, 0)

        result = get_priority(self.HG_HTTPS_URL, "origin")
        self.assertEqual(result, 0)


class GetRemoteOptionsTests(DataSetTestCase):
    repo_name = "multiple-remotes"

    def test_get_all_three_remotes(self):

        folder = os.path.join(
            self.folder,
            self.repo_name,
            self.get_git_folder()
        )
        options = get_remote_options(folder)

        self.assertEqual(len(options), 3)


class GetSourceTypePatternTests(TestCase):

    def test_github(self):

        result = get_source_type_pattern(
            VALID_GITHUB_SSH_URL,
            GITHUB_PATTERNS[0]
        )

        self.assertEqual(result, SOURCE_GITHUB)

        self.assertEqual(
            get_source_type_pattern(
                VALID_BITBUCKET_SSH_URL,
                GITHUB_PATTERNS[0]
            ),
            None
        )
        self.assertEqual(
            get_source_type_pattern(VALID_HEROKU_SSH_URL, GITHUB_PATTERNS[0]),
            None
        )

    def test_bitbucket(self):

        result = get_source_type_pattern(
            VALID_BITBUCKET_SSH_URL,
            BITBUCKET_PATTERNS[0]
        )

        self.assertEqual(result, SOURCE_BITBUCKET)

        self.assertEqual(
            get_source_type_pattern(
                VALID_GITHUB_SSH_URL,
                BITBUCKET_PATTERNS[0]
            ),
            None
        )
        self.assertEqual(
            get_source_type_pattern(
                VALID_HEROKU_SSH_URL,
                BITBUCKET_PATTERNS[0]
            ),
            None
        )

    def test_heroku(self):

        result = get_source_type_pattern(
            VALID_HEROKU_SSH_URL,
            HEROKU_PATTERNS[0]
        )

        self.assertEqual(result, SOURCE_HEROKU)

        self.assertEqual(
            get_source_type_pattern(
                VALID_BITBUCKET_SSH_URL,
                HEROKU_PATTERNS[0]
            ),
            None
        )
        self.assertEqual(
            get_source_type_pattern(
                VALID_GITHUB_SSH_URL,
                HEROKU_PATTERNS[0]
            ),
            None
        )


class GetUserNAmeTests(TestCase):

    def test_github(self):

        result = get_username(VALID_GITHUB_SSH_URL)
        self.assertEqual(result, "wercker")

        result = get_username(VALID_GITHUB_HTTPS_URL)
        self.assertEqual(result, "wercker")

    def test_bitbucket(self):
        result = get_username(VALID_BITBUCKET_SSH_URL)
        self.assertEqual(result, "postmodern")

        result = get_username(VALID_BITBUCKET_HTTPS_URL)
        self.assertEqual(result, "postmodern")


class FindHerokuSources(DataSetTestCase):
    repo_name = "multiple-remotes"

    def test_no_heroku_options(self):

        folder = os.path.join(
            self.folder,
            self.repo_name,
            self.get_git_folder()
        )

        result = find_heroku_sources(folder)
        self.assertEqual(len(result), 1)


class ConvertToUrlTests(TestCase):

    def test_bitbucket(self):
        result = convert_to_url(VALID_BITBUCKET_SSH_URL)
        self.assertEqual(result, VALID_BITBUCKET_SSH_URL)

        result = convert_to_url(VALID_BITBUCKET_HTTPS_URL)
        self.assertEqual(result, VALID_BITBUCKET_SSH_URL)

    def test_github(self):
        result = convert_to_url(VALID_GITHUB_SSH_URL)
        self.assertEqual(result, VALID_GITHUB_SSH_URL)

        result = convert_to_url(VALID_GITHUB_HTTPS_URL)
        self.assertEqual(result, VALID_GITHUB_SSH_URL)

    def test_custom_url(self):
        custom_url = "git@exotic-git-host.com:specialuser/secretproject"

        result = convert_to_url(custom_url)

        self.assertEqual(result, custom_url)
