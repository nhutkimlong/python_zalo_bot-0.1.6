from zalo_bot._utils.strings import to_camel_case

def test_to_camel_case_basic():
    assert to_camel_case('snake_case') == 'snakeCase'
    assert to_camel_case('test_string_example') == 'testStringExample'

def test_to_camel_case_single_word():
    assert to_camel_case('word') == 'word'

def test_to_camel_case_empty():
    assert to_camel_case('') == '' 