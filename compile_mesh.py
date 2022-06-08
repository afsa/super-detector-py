#!/usr/bin/env python
import argparse
import logging
from os import getcwd, path

import h5py
from tqdm import tqdm

from src.mesh.mesh import Mesh


class CompileMesh:

    def __init__(self):

        # Parse command line args
        parser = argparse.ArgumentParser(description='run TDGL simulations')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            default=False,
                            help='run in verbose mode'
                            )

        parser.add_argument('-s',
                            '--silent',
                            action='store_true',
                            default=False,
                            help='run in silent mode'
                            )

        parser.add_argument('input',
                            metavar='INPUT',
                            nargs='+',
                            type=str,
                            help='path to the mesh to compile'
                            )

        parser.set_defaults(func=self.compile)

        # Get arguments
        self.args = parser.parse_args()

        # Create a logger
        self.logger = logging.getLogger('simulate')
        console_stream = logging.StreamHandler()
        console_stream.setFormatter(
            logging.Formatter('%(levelname)s: %(message)s')
        )
        self.logger.addHandler(console_stream)

        # Set log level to DEBUG in verbose mode and INFO in non-verbose mode
        self.logger.setLevel(
            logging.DEBUG if self.args.verbose else logging.INFO
        )

        # Disable logging if silent mode is enabled
        self.logger.disabled = self.args.silent

        self.args.func()

    def compile(self):

        for input_file in tqdm(self.args.input):
            with h5py.File(path.join(getcwd(), input_file), 'r+') as h5file:

                # Mesh is already compiled.
                if Mesh.is_restorable(h5file):
                    continue

                mesh = Mesh.load_from_hdf5(h5file)
                h5file.clear()
                mesh.save_to_hdf5(h5file)


if __name__ == '__main__':
    CompileMesh()
