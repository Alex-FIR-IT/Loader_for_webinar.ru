import os.path
import unittest


def run_tests() -> unittest.TestResult:
    """

    :return: unittest.TestResult
    """
    loader = unittest.TestLoader()

    test_directory_name = "test_package"

    start_dir = os.path.join(os.getcwd(), test_directory_name)

    suite = loader.discover(start_dir=start_dir,
                            pattern=r'*_test.py',
                            top_level_dir='./'
                            )

    runner = unittest.TextTestRunner()

    return runner.run(test=suite)


if __name__ == '__main__':
    run_tests()
