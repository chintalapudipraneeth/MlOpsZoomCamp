import sys


class TestCheckFunctional:
    def test_version(self):
        system_major = sys.version_info.major
        required_major = 3

        assert system_major == required_major
