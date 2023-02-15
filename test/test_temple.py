import pytest


@pytest.fixture
def temple_contract(Temple, accounts):
    yield Temple.deploy("0x123gg", "Temple of Zelda", 1, 1069, {'from': accounts[0]})


def test_initial_state(temple_contract):
    assert temple_contract.TempleName() == "Temple of Zelda"
