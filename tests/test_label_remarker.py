import pytest
from AutoLabel.main import Label_Remarker

def test_contains_chinese():
    lr = Label_Remarker()
    assert lr.contains_chinese('你好') == True
    assert lr.contains_chinese('Hello') == False

def test_validate_product_name():
    lr = Label_Remarker()
    assert lr.validate_product_name('Wrist') == 'Wrist ball'
    assert lr.validate_product_name('Unknown') == 'Unknown'

