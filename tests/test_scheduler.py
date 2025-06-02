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
