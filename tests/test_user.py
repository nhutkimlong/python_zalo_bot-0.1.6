import pytest
from zalo_bot._user import User


def test_user_creation():
    user = User(id="123", display_name="Test User", account_name="test_account", account_type="bot", is_bot=True, can_join_groups=True)
    assert user.id == "123"
    assert user.display_name == "Test User"
    assert user.account_name == "test_account"
    assert user.account_type == "bot"
    assert user.is_bot is True
    assert user.can_join_groups is True


def test_user_equality():
    user1 = User(id="123")
    user2 = User(id="123")
    user3 = User(id="456")
    assert user1 == user2