from django.test.runner import DiscoverRunner


class TesttickDiscoverRunner(DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = ["testtick"]
        return super().run_tests(test_labels, extra_tests=extra_tests, **kwargs)
