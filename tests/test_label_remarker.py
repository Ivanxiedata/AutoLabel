import pytest
from pytest_assume.plugin import assume
from AutoLabel.main import Label_Remarker

def test_contains_chinese():
    lr = Label_Remarker()
    with assume:  # Soft assertions within the context manager
        assume(lr.contains_chinese('你好') is True)
        assume(lr.contains_chinese('Hello') is False)

def test_validate_product_name():
    lr = Label_Remarker()
    with assume:  # Multiple checks in one test function
        assume(lr.validate_product_name('Wrist') == 'Wrist ball')
        assume(lr.validate_product_name('Unknown') == 'Unknown')
