import pytest
from zalo_bot._utils.default_value import DefaultValue
import sys
sys.modules[__name__].__file__ = __file__  # For pytest to recognize the module

def test_default_value_bool():
    dv_true = DefaultValue(True)
    dv_false = DefaultValue(False)
    assert bool(dv_true) is True
    assert bool(dv_false) is False

def test_default_value_str_repr():
    dv = DefaultValue(42)
    assert str(dv) == "DefaultValue(42)"
    assert repr(dv) == "42"

def test_default_value_get_value():
    dv = DefaultValue(99)
    assert DefaultValue.get_value(dv) == 99
    assert DefaultValue.get_value(100) == 100 