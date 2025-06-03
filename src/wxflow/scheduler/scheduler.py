from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

from ..attrdict import AttrDict
from ..factory import Factory
from ..timetools import timedelta_to_HMS, to_timedelta


class Scheduler:

    scheduler_factory = Factory('Scheduler')

    def __init__(self, config: Dict[str, Any], *args: Any, **kwargs: Any) -> None:
        """
        Initializes the scheduler with the provided configuration.

        Parameters
        ----------
        config : Dict
            Configuration dictionary for the scheduler. The expected keys and their usage are:
                - 'scheduler_type' (str, required): Specifies the type of scheduler to use.
                    Accepted values are 'slurm' or 'pbs'.
                - 'job_name' (str, required): Name of the job. Used in both Slurm and PBS.
                - 'partition' (str, optional): Partition or queue to submit the job to.
                    Used in Slurm as 'partition', in PBS as 'queue'.
                - 'nodes' (int, optional): Number of nodes to request. Used in both Slurm and PBS.
                - 'ntasks' (int, optional): Number of tasks. Used in Slurm.
                - 'ppn' (int, optional): Processors per node. Used in PBS.
                - 'time' (str, optional): Walltime limit for the job (e.g., '01:00:00'). Used in both.
                - 'output' (str, optional): Path for standard output file. Used in both.
                - 'error' (str, optional): Path for standard error file. Used in both.
                - 'account' (str, optional): Account to charge for resources. Used in both.
                - 'mail_user' (str, optional): Email address for notifications. Used in both.
                - 'mail_type' (str, optional): Type of email notifications. Used in both.
                - 'native' (str, optional): Any additional scheduler-specific options can be included as needed.
        Notes
        -----
        - Required keys: 'scheduler_type', 'job_name'
        - Optional keys: All others listed above.
        - The dictionary may contain other scheduler-specific options as needed.

        *args : Any
            Additional positional arguments.
        **kwargs : Any
            Additional keyword arguments.

        """

        # Cache incoming config
        self._config = AttrDict(config)

        self._config_to_specs()
        self.batch_card = []

        # Set attributes from the user provided information
        for arg in args:
            setattr(self, str(arg), arg)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _config_to_specs(self) -> None:
        """
        Deep copies and converts the internal configuration dictionary to a standardized specification format.
        This method processes the internal `_config` attribute and assigns the self.specs attribute with the following transformations:
          - Converts the 'memory' field to a string in megabytes (e.g., '1024M').
          - Converts the 'walltime' field to a string in HH:MM:SS format.
          - Ensures the 'env' field (environment variables) is a list.
          - Ensures the 'native' field (native scheduler directives) is a list.
        """
        self.specs = self._config.deepcopy()

        # Convert 'memory' to MB
        if 'memory' in self._config:
            self.specs.memory = str(self.memory_in_megabytes(self._config.memory)) + 'M'

        # Convert 'walltime' to HH:MM:SS format
        if 'walltime' in self._config:
            self.specs.walltime = self.walltime_in_string(self._config.walltime)

        # Ensure environment variables are a list
        if 'env' in self._config:
            if not isinstance(self._config.env, (list, tuple)):
                self.specs.env = [self._config.env]

        # Ensure native scheduler directives are a list
        if 'native' in self._config:
            if not isinstance(self._config.native, (list, tuple)):
                self.specs.native = [self._config.native]

        return

    def dump(self, filename: Optional[str] = None) -> None:
        """
        Dumps the batch card to a file or prints it to stdout.

        If a filename is provided, writes the contents of `self.batch_card` to the specified file.
        Otherwise, prints the batch card to standard output.

        Parameters
        ----------
        filename : Optional[str], default=None
            The path to the file where the batch card should be written. If None, the batch card is printed to stdout.

        Returns
        -------
        None

        Raises
        ------
        Exception
            If an error occurs while writing to the specified file.
        """
        if filename is not None:
            try:
                with open(filename, 'w') as fh:
                    for item in self.batch_card:
                        fh.write(f"{item}\n")
            except Exception as e:
                raise f"Unknown exception in writing scheduler directives to {filename} from {e}"
        else:
            print(self.get_batch_card)

    @property
    def get_batch_card(self) -> str:
        return '\n'.join(self.batch_card)

    @property
    def get_accounting(self) -> None:
        """
        Generate the accounting specific items of the job card.
        E.g. jobname, queuing, partitions, accounts etc.
        """

        pass

    @property
    def get_resources(self) -> None:
        """
        Generate the resource specific items of the job card.
        E.g. nodes, memory, walltime, exclusive, etc.
        """

        pass

    @property
    def get_env(self) -> None:
        """
        Export environment variables
        """

        pass

    @property
    def get_native(self) -> List[str]:
        #    """
        #    Generate the scheduler specific native directives verbatim from the user input.
        #    """

        strings = []
        if 'native' in self.specs:
            for item in self.specs.native:
                strings.append(f"{item}")

        return strings

    @staticmethod
    def memory_in_bytes(memory: str) -> float:
        """
        Converts bytes, k, M, G, T (case-insensitive) to number of bytes
        Default units of input memory string is bytes
        Uses powers of 1024 for scaling (kilobytes, megabytes, etc.)
        1024 Bytes = 1 KB

        Parameters
        ----------
        memory: str
            Memory string to convert, e.g., '1024', '1K', '512M', '2G', '1T'

        Returns
        -------
        int: memory in bytes
        """
        scale = {'B': 0, 'K': 1, 'M': 2, 'G': 3, 'T': 4}
        multiplier = 1
        if memory[-1].upper() in scale:
            multiplier = 1024 ** scale[memory[-1]]
            memory = memory[:-1]

        return int(memory) * multiplier

    @staticmethod
    def memory_in_megabytes(memory: str) -> int:
        """
        Converts input memory in bytes into Megabytes
        1 MB = 1048576 Bytes
        """

        return int(Scheduler.memory_in_bytes(memory) / 1048576.0)

    @staticmethod
    def walltime_in_string(walltime: Union[str, timedelta]) -> str:

        if isinstance(walltime, timedelta):
            return timedelta_to_HMS(walltime)
        elif isinstance(walltime, str):
            return timedelta_to_HMS(to_timedelta(walltime))
        else:
            raise ValueError(f"Invalid walltime format: {walltime}. Expected a string or timedelta.")
