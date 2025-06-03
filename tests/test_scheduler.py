from datetime import timedelta

import pytest

from wxflow import PBS, Scheduler, Slurm


def test_scheduler_memory_in_bytes():
    assert Scheduler.memory_in_bytes('1024') == 1024
    assert Scheduler.memory_in_bytes('1K') == 1024
    assert Scheduler.memory_in_bytes('2M') == 2 * 1024 * 1024
    assert Scheduler.memory_in_bytes('1G') == 1024 ** 3
    assert Scheduler.memory_in_bytes('1T') == 1024 ** 4


def test_scheduler_memory_in_megabytes():
    assert Scheduler.memory_in_megabytes('1048576') == 1
    assert Scheduler.memory_in_megabytes('1M') == 1
    assert Scheduler.memory_in_megabytes('2M') == 2
    assert Scheduler.memory_in_megabytes('1G') == 1024


def test_scheduler_walltime_in_string():
    td = timedelta(days=1, hours=2, minutes=3, seconds=4)
    assert Scheduler.walltime_in_string(td) == '26:03:04'
    assert Scheduler.walltime_in_string('01:02:03') == '01:02:03'
    with pytest.raises(ValueError):
        Scheduler.walltime_in_string('not_a_time')


def test_pbs_batch_card_basic():
    config = {
        'jobname': 'testjob',
        'queue': 'batch',
        'account': 'myacct',
        'stdout': 'out.log',
        'stderr': 'err.log',
        'walltime': '01:00:00',
        'nodes': 2,
        'tasks_per_node': 4,
        'memory': '2G',
        'env': ['ALL'],
        'native': ['other=foo']
    }
    pbs = PBS(config)
    card = pbs.get_batch_card
    assert '#PBS -N testjob' in card
    assert '#PBS -q batch' in card
    assert '#PBS -A myacct' in card
    assert '#PBS -o out.log' in card or '#PBS -e err.log' in card
    assert '#PBS -l walltime=01:00:00' in card
    assert '#PBS -l select=2:mpiprocs=4:mem=2048M' in card or \
           '#PBS -l select=2:mpiprocs=4:mem=2048M:ompthreads=' in card or \
           '#PBS -l select=2:mpiprocs=4:mem=2048M:ncpus=' in card
    assert '#PBS -V' in card
    assert '#PBS -l other=foo' in card


def test_slurm_batch_card_basic():
    config = {
        'jobname': 'testjob',
        'queue': 'batch',
        'account': 'myacct',
        'stdout': 'out.log',
        'stderr': 'err.log',
        'walltime': '01:00:00',
        'nodes': 2,
        'tasks_per_node': 4,
        'memory': '2G',
        'env': ['ALL'],
        'native': ['--other=foo']
    }
    slurm = Slurm(config)
    card = slurm.get_batch_card
    assert '#SBATCH --job-name=testjob' in card
    assert '#SBATCH --qos=batch' in card
    assert '#SBATCH --account=myacct' in card
    assert '#SBATCH --output=out.log' in card or '#SBATCH --error=err.log' in card
    assert '#SBATCH --time=01:00:00' in card
    assert '#SBATCH --nodes=2' in card
    assert '#SBATCH --ntasks_per-node=4' in card
    assert '#SBATCH --mem=2048M' in card
    assert '#SBATCH --export=ALL' in card
    assert '#SBATCH --other=foo' in card


def test_config_to_specs_memory_and_walltime_and_env_and_native():
    config = {
        'memory': '2G',
        'walltime': '01:23:45',
        'env': 'FOO',
        'native': '--foo=bar'
    }
    s = Scheduler(config)
    s._config_to_specs()
    specs = s.specs
    assert specs.memory == '2048M'
    assert specs.walltime == '01:23:45'
    assert isinstance(specs.env, list)
    assert specs.env == ['FOO']
    assert isinstance(specs.native, list)
    assert specs.native == ['--foo=bar']


def test_get_native():
    config = {'native': ['--foo=bar', '--baz=qux']}
    s = Scheduler(config)
    native = s.get_native
    assert native == ['--foo=bar', '--baz=qux']


def test_dump_prints(monkeypatch):
    config = {}
    s = Scheduler(config)
    s.batch_card = ['line1', 'line2']
    printed = []
    monkeypatch.setattr('builtins.print', lambda x: printed.append(x))
    s.dump()
    assert printed[0] == 'line1\nline2'


def test_dump_file(tmp_path):
    config = {}
    s = Scheduler(config)
    s.batch_card = ['line1', 'line2']
    out = tmp_path / 'batch.txt'
    s.dump(str(out))
    with open(out) as f:
        lines = f.read().splitlines()
    assert lines == ['line1', 'line2']


def test_get_batch_card_property():
    config = {}
    s = Scheduler(config)
    s.batch_card = ['foo', 'bar']
    assert s.get_batch_card == 'foo\nbar'


def test_pbs_get_accounting_all_fields():
    config = {
        'shell': '/bin/bash',
        'jobname': 'job',
        'account': 'acct',
        'queue': 'q',
        'join': True,
        'stdout': 'out',
        'stderr': 'err',
    }
    pbs = PBS(config)
    acc = pbs.get_accounting
    assert '-S /bin/bash' in acc
    assert '-N job' in acc
    assert '-A acct' in acc
    assert '-q q' in acc
    assert '-j oe' in acc
    assert '-o out' in acc or '-e err' in acc


def test_pbs_get_resources_all_fields():
    config = {
        'walltime': '01:00:00',
        'debug': '1',
        'nodes': 2,
        'tasks_per_node': 4,
        'threads': 8,
        'tasks': 16,
        'memory': '2G',
        'chunk': 'pack',
        'exclusive': True
    }
    pbs = PBS(config)
    res = pbs.get_resources
    assert '-l walltime=01:00:00' in res
    assert '-l debug=1' in res
    assert any('select=2:mpiprocs=4:ompthreads=8:ncpus=16:mem=2048M' in s for s in res)
    assert any('place=pack:excl' in s for s in res)


def test_pbs_get_env_all():
    config = {'env': ['ALL']}
    pbs = PBS(config)
    envs = pbs.get_env
    assert '-V' in envs


def test_pbs_get_env_vars(monkeypatch):
    monkeypatch.setattr('os.getenv', lambda k: 'VAL')
    config = {'env': ['FOO', 'BAR']}
    pbs = PBS(config)
    envs = pbs.get_env
    assert envs[0].startswith('-v ')
    assert 'FOO=VAL' in envs[0]
    assert 'BAR=VAL' in envs[0]


def test_pbs_get_select_and_place():
    config = {
        'nodes': 1,
        'tasks_per_node': 2,
        'threads': 3,
        'tasks': 4,
        'memory': '1G',
        'chunk': 'free',
        'exclusive': True
    }
    pbs = PBS(config)
    sel = pbs.get_select
    assert '1' in sel
    assert 'mpiprocs=2' in sel
    assert 'ompthreads=3' in sel
    assert 'ncpus=4' in sel
    assert 'mem=1024M' in sel
    plc = pbs.get_place
    assert 'free' in plc
    assert 'excl' in plc


def test_pbs_get_native():
    config = {'native': ['foo', 'bar']}
    pbs = PBS(config)
    native = pbs.get_native
    assert '-l foo' in native
    assert '-l bar' in native


def test_slurm_get_accounting_all_fields():
    config = {
        'jobname': 'job',
        'account': 'acct',
        'queue': 'q',
        'partition': 'part',
        'join': True,
        'stdout': 'out',
        'stderr': 'err',
    }
    slurm = Slurm(config)
    acc = slurm.get_accounting
    assert '--job-name=job' in acc
    assert '--account=acct' in acc
    assert '--qos=q' in acc
    assert '--partition=part' in acc
    # join True, should use stderr if stdout not present
    assert '--error=out' in acc or '--error=err' in acc


def test_slurm_get_accounting_no_join():
    config = {
        'jobname': 'job',
        'stdout': 'out',
        'stderr': 'err',
    }
    slurm = Slurm(config)
    acc = slurm.get_accounting
    assert '--output=out' in acc
    assert '--error=err' in acc


def test_slurm_get_resources_all_fields():
    config = {
        'memory': '2G',
        'walltime': '01:00:00',
        'nodes': 2,
        'tasks_per_core': 3,
        'tasks_per_node': 4,
        'exclusive': True,
        'debug': True
    }
    slurm = Slurm(config)
    res = slurm.get_resources
    assert '--mem=2048M' in res
    assert '--time=01:00:00' in res
    assert '--nodes=2' in res
    assert '--ntasks_per-core=3' in res
    assert '--ntasks_per-node=4' in res
    assert '--exclusive' in res
    assert '--verbose' in res


def test_slurm_get_env():
    config = {'env': ['ALL', 'FOO']}
    slurm = Slurm(config)
    envs = slurm.get_env
    assert '--export=ALL' in envs
    assert '--export=FOO' in envs
