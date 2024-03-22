import pytest

from wxflow import AttrDict

TEST_VAL = [1, 2, 3]
TEST_DICT = {'a': {'b': {'c': TEST_VAL}}}


def test_set_one_level_item():
    some_dict = {'a': TEST_VAL}
    prop = AttrDict()
    prop['a'] = TEST_VAL
    assert prop == some_dict


def test_missing():
    prop = AttrDict(TEST_DICT)
    with pytest.raises(KeyError):
        prop['b']
