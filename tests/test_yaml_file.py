import os
from datetime import datetime

import pytest

from wxflow import YAMLFile, parse_j2yaml, save_as_yaml

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
