import os
from datetime import datetime, timedelta

import jinja2
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

    tmpl_dict = {"{{ name }}": "Jane", "{{ greeting }}": "How are you?", "{{ current_date | to_isotime }}": to_isotime(current_date)}
    j = Jinja(j2tmpl, data, allow_missing=False)
    loader = jinja2.BaseLoader()
    env = j.get_set_env(loader)
    assert env.filters['replace_tmpl'](j2tmpl, tmpl_dict) == f"Hello Jane! How are you? It is: {to_isotime(current_date)}"


def test_render_file(tmp_path, create_template):

    file_path = tmp_path / 'template.j2'
    data = {"name": "John"}
    j = Jinja(str(file_path), data, allow_missing=True)
    assert j.render == "Hello John! {{ greeting }} It is: {{ current_date }}"

    data = {"name": "Jane", "greeting": "How are you?", "current_date": current_date}
    j = Jinja(str(file_path), data, allow_missing=False)
    assert j.render == f"Hello Jane! How are you? It is: {to_isotime(current_date)}"

    tmpl_dict = {"{{ name }}": "Jane", "{{ greeting }}": "How are you?", "{{ current_date | to_isotime }}": to_isotime(current_date)}
    j = Jinja(str(file_path), data, allow_missing=False)
    loader = jinja2.BaseLoader()
    env = j.get_set_env(loader)
    assert env.filters['replace_tmpl'](j2tmpl, tmpl_dict) == f"Hello Jane! How are you? It is: {to_isotime(current_date)}"


def test_include(tmp_path, create_template):

    file_path = tmp_path / 'include_template.j2'

    data = {"my_name": "Jill", "name": "Joe", "greeting": "How are you?", "current_date": current_date}
    j = Jinja(str(file_path), data, allow_missing=False)
    assert j.render == f"I am Jill. Hello Joe! How are you? It is: {to_isotime(current_date)}"


def test_jinja_filters(tmp_path, create_template):
    loader = jinja2.BaseLoader()
    jinja_instance = Jinja("", {}, allow_missing=True)
    env = jinja_instance.get_set_env(loader)

    # Test strftime filter
    dt = datetime(2025, 5, 5, 12, 30, 45)
    assert env.filters["strftime"](dt, "%Y-%m-%d %H:%M:%S") == "2025-05-05 12:30:45"

    # Test to_isotime filter
    assert env.filters["to_isotime"](dt) == "2025-05-05T12:30:45Z"

    # Test to_fv3time filter
    assert env.filters["to_fv3time"](dt) == "20250505.123045"

    # Test to_YMDH filter
    assert env.filters["to_YMDH"](dt) == "2025050512"

    # Test to_YMD filter
    assert env.filters["to_YMD"](dt) == "20250505"

    # Test to_julian filter
    assert env.filters["to_julian"](dt) == "2025125"  # Example Julian day

    # Test to_f90bool filter
    assert env.filters["to_f90bool"](True) == ".true."
    assert env.filters["to_f90bool"](False) == ".false."

    # Test getenv filter
    os.environ["TEST_ENV_VAR"] = "test_value"
    assert env.filters["getenv"]("TEST_ENV_VAR") == "test_value"
    assert env.filters["getenv"]("NON_EXISTENT_VAR") == "UNDEFINED"

    # Test relpath filter
    file_path = tmp_path / 'template.j2'
    assert env.filters["relpath"](file_path, tmp_path) == "template.j2"

    # Test add_to_datetime filter
    delta = timedelta(days=1, hours=2)
    assert env.filters["add_to_datetime"](dt, delta) == datetime(2025, 5, 6, 14, 30, 45)

    # Test to_timedelta filter
    assert env.filters["to_timedelta"]("1 day, 2:00:00") == timedelta(days=1, hours=2)

    # Test replace_tmpl filter
    tmpl = "Hello {{ name }}!"
    tmpl_dict = {"{{ name }}": "John"}
    assert env.filters["replace_tmpl"](tmpl, tmpl_dict) == "Hello John!"

    # Test path_exists filter
    file_path = tmp_path / 'template.j2'
    assert env.filters["path_exists"](file_path) is True
    assert env.filters["path_exists"]("/non/existent/path") is False
