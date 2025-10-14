import pytest
from zalo_bot._zalo_object import ZaloObject

class DummyZaloObject(ZaloObject):
    def __init__(self, id_value=None):
        super().__init__()
        self._id_attrs = (id_value,) if id_value is not None else ()
        self._freeze()

def test_zalo_object_equality():
    obj1 = DummyZaloObject("abc")
    obj2 = DummyZaloObject("abc")
    obj3 = DummyZaloObject("def")
    assert obj1 == obj2
    assert obj1 != obj3

def test_zalo_object_hash():
    obj1 = DummyZaloObject("abc")
    obj2 = DummyZaloObject("abc")
    assert hash(obj1) == hash(obj2)

def test_zalo_object_setattr_protection():
    obj = DummyZaloObject("abc")
    with pytest.raises(AttributeError):
        obj.id = "new_id" 