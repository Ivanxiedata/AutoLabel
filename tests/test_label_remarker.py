import pytest
from pytest_assume.plugin import assume
import pandas as pd
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

def test_find_col_name():
    lr = Label_Remarker()
    mock_data = {
        'The title of the product': ['Product A', 'Product B'],
        'The total quantity': [10, 20]
    }
    df = pd.DataFrame(mock_data)

    with assume:
        assume(lr.find_column_name(df,'The title of the product') == 'The title of the product')
        assume(lr.find_column_name(df, 'The total') == 'The total quantity')

        try:
            lr.find_column_name(df, 'Non-Existent Column')
            assume(False)
        except KeyError:
            assume(True)

def test_g_translator(mocker):
    lr = Label_Remarker()

    # Mock the Translator's translate method to simulate translation
    # Replace the actual translation in the original function with mock data
    mock_translate = mocker.patch('AutoLabel.main.Translator.translate')
    # simulate a successful translation response
    mock_translate.return_value.text = 'Hello'

    with assume:
        assume(lr.g_translator('你好') == 'Hello')
        mock_translate.assert_called_once_with('你好', src='zh-cn', dest='en')

        assume(lr.g_translator('Car' == 'car'))
        mock_translate.reset_mock()

        mock_translate.side_effect = Exception('Translation failed')
        assume(lr.g_translator('你好') == '你好')

