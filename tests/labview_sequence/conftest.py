import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'labview_sequence')


@pytest.fixture
def testdata_dir():
    return TESTDATA_DIR
