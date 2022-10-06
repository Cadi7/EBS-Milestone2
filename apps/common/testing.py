from django.test.runner import DiscoverRunner


class NoDbTestRunner(DiscoverRunner):
    """A test runner to test without database creation/deletion"""

    def setup_databases(self, **kwargs):
        raise NotImplementedError()

    def teardown_databases(self, old_config, **kwargs):
        raise NotImplementedError()
