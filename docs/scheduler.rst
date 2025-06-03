Scheduler
=========

The scheduler module provides a flexible framework for generating batch job submission scripts for different High Performance Computing (HPC) schedulers. It supports both PBS and Slurm schedulers through a factory pattern design.

Overview
--------

The scheduler module consists of three main components:

* **Scheduler**: Base class that provides common functionality and factory pattern support
* **PBS**: Implementation for PBS Pro scheduler systems
* **Slurm**: Implementation for Slurm scheduler systems

Quick Start
-----------

Basic usage example:

.. code-block:: python

    from wxflow import Scheduler

    # Configuration for a PBS job
    pbs_config = {
        'scheduler': 'PBS',
        'jobname': 'my_job',
        'account': 'my_account',
        'queue': 'batch',
        'nodes': 2,
        'tasks_per_node': 4,
        'memory': '8G',
        'walltime': '02:00:00',
        'stdout': 'job.out',
        'stderr': 'job.err'
    }

    # Create scheduler instance
    scheduler = Scheduler(pbs_config)
    job_card = scheduler.scheduler_factory.create(pbs_config['scheduler'], pbs_config)

    # Generate batch card
    print(job_card.get_batch_card)

    # Save to file
    job_card.dump('submit_job.pbs')

Configuration Options
---------------------

The scheduler configuration accepts the following keys:

Required Keys
~~~~~~~~~~~~~

* **scheduler**: Scheduler type ('PBS' or 'Slurm')
* **jobname**: Name of the job

Optional Keys for Both Schedulers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **account**: Account to charge for resources
* **queue**: Queue or partition name (maps to 'qos' in Slurm)
* **partition**: Partition name (Slurm only)
* **nodes**: Number of nodes to request
* **tasks**: Total number of tasks
* **tasks_per_node**: Tasks per node
* **tasks_per_core**: Tasks per core
* **memory**: Memory requirement (e.g., '8G', '2048M')
* **walltime**: Time limit (e.g., '02:00:00')
* **stdout**: Standard output file path
* **stderr**: Standard error file path
* **env**: Environment variables to export
* **native**: Additional scheduler-specific options
* **exclusive**: Request exclusive node access
* **debug**: Enable debug mode

PBS-Specific Options
~~~~~~~~~~~~~~~~~~~

* **shell**: Shell to use (e.g., '/bin/bash')
* **join**: Join stdout and stderr
* **ppn**: Processors per node
* **threads**: Number of threads (OpenMP)
* **chunk**: Placement strategy ('free', 'pack', 'scatter', 'vscatter')

Classes and Methods
-------------------

Scheduler
~~~~~~~~~

.. autoclass:: wxflow.Scheduler
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

   **Properties:**

   .. autoattribute:: get_batch_card
      :annotation: -> str

      Returns the complete batch card as a string with newlines.

   .. autoattribute:: get_native
      :annotation: -> List[str]

      Returns native scheduler directives.

   **Class Methods:**

   .. automethod:: memory_in_bytes
      :classmethod:

   .. automethod:: memory_in_megabytes
      :classmethod:

   .. automethod:: walltime_in_string
      :classmethod:

   **Instance Methods:**

   .. automethod:: dump

PBS
~~~

.. autoclass:: wxflow.PBS
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

   **Properties:**

   .. autoattribute:: get_accounting
      :annotation: -> List[str]

      Generate accounting-specific PBS directives (job name, account, queue, etc.).

   .. autoattribute:: get_resources
      :annotation: -> List[str]

      Generate resource-specific PBS directives (walltime, select, place, etc.).

   .. autoattribute:: get_env
      :annotation: -> List[str]

      Generate environment variable export directives.

   .. autoattribute:: get_select
      :annotation: -> str

      Construct the "select" resource request string.

   .. autoattribute:: get_place
      :annotation: -> str

      Construct the "place" placement request string.

   .. autoattribute:: get_native
      :annotation: -> List[str]

      Generate PBS-specific native directives.

Slurm
~~~~~

.. autoclass:: wxflow.Slurm
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

   **Properties:**

   .. autoattribute:: get_accounting
      :annotation: -> List[str]

      Generate accounting-specific Slurm directives (job name, account, partition, etc.).

   .. autoattribute:: get_resources
      :annotation: -> List[str]

      Generate resource-specific Slurm directives (nodes, tasks, memory, etc.).

   .. autoattribute:: get_env
      :annotation: -> List[str]

      Generate environment variable export directives.

   .. autoattribute:: get_native
      :annotation: -> List[str]

      Generate Slurm-specific native directives.

Examples
--------

PBS Example
~~~~~~~~~~~

.. code-block:: python

    from wxflow import PBS

    config = {
        'jobname': 'weather_model',
        'account': 'weather_proj',
        'queue': 'batch',
        'nodes': 4,
        'tasks_per_node': 8,
        'memory': '16G',
        'walltime': '04:00:00',
        'stdout': 'model.out',
        'stderr': 'model.err',
        'shell': '/bin/bash',
        'env': ['ALL'],
        'chunk': 'pack',
        'exclusive': True
    }

    pbs_job = PBS(config)
    print(pbs_job.get_batch_card)

This generates:

.. code-block:: bash

    #PBS -S /bin/bash
    #PBS -N weather_model
    #PBS -A weather_proj
    #PBS -q batch
    #PBS -o model.out
    #PBS -e model.err
    #PBS -l walltime=04:00:00
    #PBS -l select=4:mpiprocs=8:mem=16384M
    #PBS -l place=pack:excl
    #PBS -V

Slurm Example
~~~~~~~~~~~~~

.. code-block:: python

    from wxflow import Slurm

    config = {
        'jobname': 'weather_model',
        'account': 'weather_proj',
        'partition': 'compute',
        'nodes': 4,
        'tasks_per_node': 8,
        'memory': '16G',
        'walltime': '04:00:00',
        'stdout': 'model.out',
        'stderr': 'model.err',
        'env': ['ALL'],
        'exclusive': True
    }

    slurm_job = Slurm(config)
    print(slurm_job.get_batch_card)

This generates:

.. code-block:: bash

    #SBATCH --job-name=weather_model
    #SBATCH --account=weather_proj
    #SBATCH --partition=compute
    #SBATCH --output=model.out
    #SBATCH --error=model.err
    #SBATCH --time=04:00:00
    #SBATCH --nodes=4
    #SBATCH --ntasks_per-node=8
    #SBATCH --mem=16384M
    #SBATCH --exclusive
    #SBATCH --export=ALL

Memory and Walltime Utilities
------------------------------

The scheduler provides utility methods for converting memory and walltime formats:

.. code-block:: python

    from wxflow import Scheduler

    # Memory conversions
    bytes_val = Scheduler.memory_in_bytes('8G')        # 8589934592
    mb_val = Scheduler.memory_in_megabytes('8G')       # 8192

    # Walltime conversion
    from datetime import timedelta
    td = timedelta(hours=2, minutes=30)
    time_str = Scheduler.walltime_in_string(td)        # '02:30:00'

Factory Pattern
---------------

The scheduler uses a factory pattern to create appropriate scheduler instances:

.. code-block:: python

    from wxflow import Scheduler

    # Factory automatically selects the right class
    config = {'scheduler': 'PBS', 'jobname': 'test'}
    scheduler = Scheduler(config)
    pbs_instance = scheduler.scheduler_factory.create('PBS', config)

    config = {'scheduler': 'Slurm', 'jobname': 'test'}
    slurm_instance = scheduler.scheduler_factory.create('Slurm', config)

Error Handling
--------------

The scheduler validates configuration and raises appropriate errors:

* **ValueError**: Invalid memory format, walltime format, or missing required fields
* **KeyError**: Missing required configuration keys

.. code-block:: python

    try:
        config = {'jobname': 'test'}  # Missing scheduler type
        scheduler = Scheduler(config)
    except KeyError as e:
        print(f"Missing configuration: {e}")

Best Practices
--------------

1. **Always specify required fields**: Ensure 'scheduler' and 'jobname' are provided
2. **Use appropriate memory units**: Prefer 'G' for gigabytes, 'M' for megabytes
3. **Format walltime correctly**: Use 'HH:MM:SS' format or timedelta objects
4. **Test batch cards**: Always review generated batch cards before submission
5. **Use native options sparingly**: Prefer standard configuration options over native directives

.. note::
   Different HPC systems may have varying requirements. Always consult your system's documentation for specific scheduler configurations and resource limits.