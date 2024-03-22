from datetime import datetime

import pytest

from wxflow import Jinja, to_isotime

current_date = datetime.now()
j2tmpl = """Hello {{ name }}! {{ greeting }} It is: {{ current_date | to_isotime }}"""
j2includetmpl = """I am {{ my_name }}. {% include 'template.j2' %}"""


@pytest.fixture
def create_template(tmp_path):
    file_path = tmp_path / 'template.j2'
    with open(file_path, 'w') as fh:
        fh.write(j2tmpl)

    file_path = tmp_path / 'include_template.j2'
    with open(file_path, 'w') as fh:
        fh.write(j2includetmpl)


def test_render_stream():
    data = {"name": "John"}
    j = Jinja(j2tmpl, data, allow_missing=True)
    assert j.render == "Hello John! {{ greeting }} It is: {{ current_date }}"

    data = {"name": "Jane", "greeting": "How are you?", "current_date": current_date}
    j = Jinja(j2tmpl, data, allow_missing=False)
    assert j.render == f"Hello Jane! How are you? It is: {to_isotime(current_date)}"


def test_render_file(tmp_path, create_template):

    file_path = tmp_path / 'template.j2'
    data = {"name": "John"}
    j = Jinja(str(file_path), data, allow_missing=True)
    assert j.render == "Hello John! {{ greeting }} It is: {{ current_date }}"

    data = {"name": "Jane", "greeting": "How are you?", "current_date": current_date}
    j = Jinja(str(file_path), data, allow_missing=False)
    assert j.render == f"Hello Jane! How are you? It is: {to_isotime(current_date)}"


def test_include(tmp_path, create_template):

    file_path = tmp_path / 'include_template.j2'

    data = {"my_name": "Jill", "name": "Joe", "greeting": "How are you?", "current_date": current_date}
    j = Jinja(str(file_path), data, allow_missing=False)
    assert j.render == f"I am Jill. Hello Joe! How are you? It is: {to_isotime(current_date)}"
