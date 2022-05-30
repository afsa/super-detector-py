import datetime
import logging
from typing import Callable, Sequence, Optional, Any, List, Dict

from tqdm import tqdm

from src.io.data_handler import DataHandler
from src.io.running_state import RunningState


class Runner:
    """
    The runner is responsible for the simulation loop. It handles the state,
    runs the update function and saves the data.
    """

    def __init__(self,
                 function: Callable,
                 initial_values: List[Any],
                 names: Sequence[str],
                 steps: int,
                 save_every: int,
                 data_handler: DataHandler,
                 dt: float,
                 skip: int = 0,
                 fixed_values: Optional[List[Any]] = None,
                 fixed_names: Optional[Sequence] = None,
                 running_names: Optional[Sequence[str]] = None,
                 logger: Optional[logging.Logger] = None,
                 state: Optional[Dict[str, Any]] = None,
                 miniters: Optional[int] = None
                 ):
        """
        Create a runner before starting the simulation.

        :param function: The update function that takes the state from the
        current sate to the next.
        :param initial_values: Initial values passed as parameters to the
        update function.
        :param names: Names of the parameters.
        :param steps: The number of steps to run the simulation.
        :param save_every: How many steps to simulate before saving data.
        :param data_handler: The data handler used to save to disk.
        :param dt: The time step.
        :param skip: The number of time steps to skip to thermalize.
        :param fixed_values: Values that do not change over time, but should
        be added to saved data.
        :param fixed_names: Fixed data variable names.
        :param running_names: Names of running state variables.
        :param logger: A logger to print information about simulation.
        :param state: The current state variables.
        :param miniters: Number of steps between progress update.
        """

        # Set the initial data.
        self.time = 0
        self.dt = dt

        # Set the number of steps to take for simulation and thermalization.
        self.steps = steps
        self.skip = skip

        # Set the function to run in the loop.
        self.function = function

        # Set the initial parameter values for the function and the names.
        self.values = initial_values
        self.names = names
        self.fixed_values = fixed_values if fixed_values is not None else []
        self.fixed_names = fixed_names if fixed_names is not None else []
        self.running_names = running_names if running_names is not None else []
        self.running_state = RunningState(
            running_names if running_names is not None else [],
            save_every
        )
        self.state = state if state is not None else {}

        # Set how often to save.
        self.save_every = save_every

        # Set the logger.
        self.logger = logger if logger is not None else logging.getLogger()

        # Set the data handler.
        self.data_handler = data_handler

        # Set how often to update the progress bar.
        self.miniters = miniters

    def run(self):
        """
        Run the simulation loop.
        """

        # Set the initial data.
        self.state['step'] = 0
        self.state['time'] = self.time
        self.state['dt'] = self.dt

        # Thermalize if enabled.
        if self.skip > 0:
            self._run_stage_(0, self.skip, 'Thermalizing', False)
            self.running_state.clear()

        self.state['step'] = 0
        self.state['time'] = self.time
        self.state['dt'] = self.dt

        # Run simulation.
        self._run_stage_(0, self.steps, 'Simulating', True)

    def _run_stage_(self, start: int, end: int, stage_name: str, save: bool):
        """
        Run a stage of the simulation.
        :param start: Start step.
        :param end: End step.
        :param stage_name: Name of the stage.
        :param save: If the data should be saved.
        """

        # Check if the progress bar is disabled.
        prog_disabled = self.miniters is not None

        # Create variable to save the current time.
        now = None

        for i in tqdm(range(start, end + 1), desc=stage_name,
                      disable=prog_disabled):

            # Update the state
            self.state['step'] = i
            self.state['time'] = self.time
            self.state['dt'] = self.dt

            # Print progress if TQDM is disabled.
            if prog_disabled and i % self.miniters == 0:
                then = now
                now = datetime.datetime.now()
                it = self.miniters / (now - then).total_seconds() \
                    if then is not None else 0
                self.logger.info(
                    '{} {}/{} {:.2f} it/s'.format(stage_name, i, end + 1, it)
                )

            # Save data
            if i % self.save_every == 0:

                # Save data if it is enabled.
                if save:

                    # Create a dict containing the data.
                    data = dict(
                        (self.names[i], self.values[i])
                        for i in range(len(self.names))
                    )

                    # Add the fixed values.
                    for idx, name in enumerate(self.fixed_names):
                        data[name] = self.fixed_values[idx]

                    # Add the running state data to the dict.
                    if i != 0:
                        data.update(self.running_state.export())

                    # Save the time step.
                    self.data_handler.save_time_step(self.state, data)

                # Clear the running state.
                self.running_state.clear()

            # Run time step.
            self.values = self.function(
                self.state,
                self.running_state,
                *self.values)

            # Update the running state.
            self.running_state.next()

            # Run update time
            self.time += self.dt
