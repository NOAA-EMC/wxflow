import os
from datetime import datetime

import pytest

from wxflow import YAMLFile, parse_j2yaml, save_as_yaml
from wxflow.attrdict import AttrDict
from wxflow.yaml_file import vanilla_yaml

host_yaml = """
host:
    hostname: test_host
    host_user: !ENV ${USER}
"""

conf_yaml = """
config:
    config_file: !ENV ${TMP_PATH}/config.yaml
    user: !ENV ${USER}
    host_file: !INC ${TMP_PATH}/host.yaml
"""

j2tmpl_yaml = """
config:
    config_file: !ENV ${TMP_PATH}/config.yaml
    user: !ENV ${USER}
    host_file: !INC ${TMP_PATH}/host.yaml
tmpl:
    cdate: {{ current_cycle | to_YMD }}{{ current_cycle | strftime('%H') }}
    homedir: /home/{{ user }}
"""


@pytest.fixture
def create_template(tmpdir):
    """Create temporary templates for testing"""
    tmpdir.join('host.yaml').write(host_yaml)
    tmpdir.join('config.yaml').write(conf_yaml)
    tmpdir.join('j2tmpl.yaml').write(j2tmpl_yaml)


def test_yaml_file(tmp_path, create_template):

    # Set env. variable
    os.environ['TMP_PATH'] = str(tmp_path)
    conf = YAMLFile(path=str(tmp_path / 'config.yaml'))

    # Write out yaml file
    yaml_out = tmp_path / 'config_output.yaml'
    conf.save(yaml_out)

    # Read in the yaml file and compare w/ conf
    yaml_in = YAMLFile(path=str(yaml_out))

    assert yaml_in == conf


def test_j2template_missing_var(tmp_path, create_template):

    # Try to parse a j2yaml with an undefined variable (user)
    os.environ['TMP_PATH'] = str(tmp_path)
    with pytest.raises(NameError) as e_info:
        data = {'current_cycle': datetime.now()}
        conf = parse_j2yaml(path=str(tmp_path / 'j2tmpl.yaml'), data=data, allow_missing=False)


def test_yaml_file_with_j2templates(tmp_path, create_template):

    # Set env. variable
    os.environ['TMP_PATH'] = str(tmp_path)
    data = {'user': os.environ['USER'], 'current_cycle': datetime.now()}
    conf = parse_j2yaml(path=str(tmp_path / 'j2tmpl.yaml'), data=data)

    # Write out yaml file
    yaml_out = tmp_path / 'j2tmpl_output.yaml'
    save_as_yaml(conf, yaml_out)

    # Read in the yaml file and compare w/ conf
    yaml_in = YAMLFile(path=yaml_out)

    assert yaml_in == conf


def test_vanilla_yaml_with_regular_dict():
    """Test that vanilla_yaml processes regular dictionaries, not just AttrDict"""
    test_datetime = datetime(2024, 1, 1, 12, 0, 0)

    # Test with regular dict containing datetime
    dict_data = {'key': test_datetime}
    result = vanilla_yaml(dict_data)
    assert result == {'key': '2024-01-01T12:00:00Z'}

    # Test with nested regular dict
    nested_dict = {'outer': {'inner': test_datetime}}
    result = vanilla_yaml(nested_dict)
    assert result == {'outer': {'inner': '2024-01-01T12:00:00Z'}}

    # Test with AttrDict still works
    attrdict_data = AttrDict({'key': test_datetime})
    result = vanilla_yaml(attrdict_data)
    assert result == {'key': '2024-01-01T12:00:00Z'}

    # Test with mixed AttrDict and regular dict
    mixed = AttrDict({'attr': {'regular': test_datetime}})
    result = vanilla_yaml(mixed)
    assert result == {'attr': {'regular': '2024-01-01T12:00:00Z'}}

    # Test with list containing dicts with datetime
    list_data = [{'key': test_datetime}, {'another': test_datetime}]
    result = vanilla_yaml(list_data)
    assert result == [{'key': '2024-01-01T12:00:00Z'}, {'another': '2024-01-01T12:00:00Z'}]
