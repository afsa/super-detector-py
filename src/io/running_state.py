from typing import Union, Sequence, Dict

import numpy as np


class RunningState:
    """
    Storage class for saving data that should be saved each time step. Used
    for IV curves or simular.
    """

    def __init__(self, names: Sequence[str], buffer: int):
        """
        Create the running state.

        :param names: Names of the parameters to be saved.
        :param buffer: Size of the buffer.
        """

        self.step = 0
        self.buffer = buffer
        self.values = dict((name, np.zeros(buffer)) for name in names)

    def next(self):
        """
        Go to the next step.
        """

        self.step += 1

    def set_step(self, step: int):
        """
        Set the current step.

        :param step: Step to go to.
        """

        self.step = step

    def clear(self):
        """
        Clear the buffer.
        """

        self.step = 0
        for key in self.values.keys():
            self.values[key] = np.zeros(self.buffer)

    def append(self, name: str, value: Union[float, int]):
        """
        Append data to the buffer.

        :param name: Data to append.
        :param value: Value of the data.
        """

        self.values[name][self.step] = value

    def export(self) -> Dict[str, np.ndarray]:
        """
        Export data to save to disk.

        :return: A dict with the data.
        """

        return self.values
