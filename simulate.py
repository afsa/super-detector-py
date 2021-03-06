#!/usr/bin/env python
import argparse
import logging
from datetime import datetime
from typing import Sequence

import numpy as np
from scipy.sparse.linalg import splu

from src.io.data_handler import DataHandler
from src.matrices.matrix_builder import MatrixBuilder, MatrixType
from src.mesh.mesh import Mesh, Operator
from src.runner import Runner
from src.sparse_format import SparseFormat
from src.tdgl import get_supercurrent


class Simulate:

    def __init__(self):

        # Parse command line args
        parser = argparse.ArgumentParser(description='run TDGL simulations')

        parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            default=False,
            help='run in verbose mode'
        )

        parser.add_argument(
            '--miniters',
            type=float,
            default=None,
            help='number of steps between each update of '
                 'the progress bar'
        )

        parser.add_argument(
            'input',
            metavar='INPUT',
            help='input mesh file'
        )

        parser.add_argument(
            'output',
            metavar='OUTPUT',
            help='output file for the data'
        )

        parser.add_argument(
            '-j',
            '--current',
            type=float,
            default=0,
            help='set the initial current density'
        )

        parser.add_argument(
            '-J',
            '--current-max',
            type=float,
            default=None,
            help='set the end current density (linear interpolation between '
                 'initial and end)'
        )

        parser.add_argument(
            '--steps-per-current',
            type=float,
            default=1,
            help='number of steps per current value'
        )

        parser.add_argument(
            '-b',
            '--magnetic-field',
            type=float,
            default=0,
            help='set the external magnetic field'
        )

        parser.add_argument(
            '-t',
            '--time-step',
            type=float,
            default=1e-4,
            help='initial time step'
        )

        parser.add_argument(
            '-s',
            '--steps',
            type=float,
            default=10000,
            help='number of simulation steps to run'
        )

        parser.add_argument(
            '-e',
            '--save-every',
            type=float,
            default=100,
            help='the number of steps to wait before saving the state'
        )

        parser.add_argument(
            '--skip',
            type=float,
            default=0,
            help='number of steps to skip in the start to allow the system '
                 'to thermalize'
        )

        parser.add_argument(
            '-u',
            '--complex-time-scale',
            type=float,
            default=5.79,
            help='set value for the complex field time scale'
        )

        parser.add_argument(
            '-g',
            '--gamma',
            type=float,
            default=10.0,
            help='set value for gamma'
        )

        parser.set_defaults(func=self.run_tdgl)

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

        self.args.func()

    @classmethod
    def __get_edge_boundary(cls,
                            mesh: Mesh,
                            limits: Sequence[float]
                            ) -> np.ndarray:

        return mesh.get_edge_boundary_index_where(
            lambda xe, _: xe[:, 0] >= limits[0],
            lambda xe, _: xe[:, 1] >= limits[0],
            lambda xe, _: xe[:, 0] <= limits[1],
            lambda xe, _: xe[:, 1] <= limits[1],
            lambda _, ye: ye[:, 0] >= limits[2],
            lambda _, ye: ye[:, 1] >= limits[2],
            lambda _, ye: ye[:, 0] <= limits[3],
            lambda _, ye: ye[:, 1] <= limits[3],
            operator=Operator.AND
        )

    def run_tdgl(self):

        # Log starting time.
        start_time = datetime.now()
        self.logger.info(
            'Simulation started on {}'.format(start_time)
        )

        # Extract parameters.
        current = self.args.current
        current_max = self.args.current_max
        magnetic_field = self.args.magnetic_field
        u = self.args.complex_time_scale
        gamma = self.args.gamma
        dt = self.args.time_step
        steps = int(self.args.steps)
        save_every = int(self.args.save_every)
        skip = int(self.args.skip)
        miniters = int(self.args.miniters) \
            if self.args.miniters is not None else None

        # Plot info about the mesh.
        self.logger.info(
            'Running simulation for mesh {} with output {}'
                .format(self.args.input, self.args.output)
        )

        # Start the data handler.
        data_handler = DataHandler(
            input_file=self.args.input,
            output_file=self.args.output,
            logger=self.logger
        )

        # Plot info about simulation.
        self.logger.info(
            'Running TDGL simulation with parameters:\n'
            'j          = {}\n'.format(current) +
            'b          = {}\n'.format(magnetic_field) +
            'u          = {}\n'.format(u) +
            '??          = {}\n'.format(gamma) +
            '??t         = {}\n'.format(dt) +
            'steps      = {}\n'.format(steps) +
            'save every = {}\n'.format(save_every)
        )

        # Inform that the current is interpolated.
        if current_max is not None:
            self.logger.info(
                'Current will be interpolated between {} and {}.'
                    .format(current, current_max)
            )

        # Inform that thermalization will by used.
        if skip > 0:
            self.logger.info(
                'Skipping the first {} time steps to thermalize the system.'
                .format(skip)
            )

        # Load the mesh
        mesh = data_handler.get_mesh()

        # Load the flow edges
        input_edge, output_edge = mesh.get_flow_edges()

        # Get the metal boundary
        metal_boundary_index = np.sort(np.concatenate([
            mesh.get_boundary_index_where(
                lambda xb, _: xb >= input_edge[0],
                lambda xb, _: xb <= input_edge[1],
                lambda _, yb: yb >= input_edge[2],
                lambda _, yb: yb <= input_edge[3],
                operator=Operator.AND
            ),
            mesh.get_boundary_index_where(
                lambda xb, _: xb >= output_edge[0],
                lambda xb, _: xb <= output_edge[1],
                lambda _, yb: yb >= output_edge[2],
                lambda _, yb: yb <= output_edge[3],
                operator=Operator.AND
            ),
        ]))

        # Get the input boundary.
        input_edges_index = self.__get_edge_boundary(mesh, input_edge)

        # Get the output boundary.
        output_edges_index = self.__get_edge_boundary(mesh, output_edge)

        # Compute the vector potential.
        vector_potential = np.array([
            - magnetic_field * mesh.edge_mesh.y / 2,
            magnetic_field * mesh.edge_mesh.x / 2
        ]).transpose()

        # Create the matrix builder for fields with Neumann boundary conditions
        # and no link variables.
        builder = MatrixBuilder(mesh)

        # Build matrices for scalar potential.
        mu_laplacian = builder.build(MatrixType.LAPLACIAN,
                                     sparse_format=SparseFormat.CSC)
        mu_laplacian_lu = splu(mu_laplacian)
        mu_boundary_laplacian = builder.build(
            MatrixType.NEUMANN_BOUNDARY_LAPLACIAN
        )
        mu_gradient = builder.build(MatrixType.GRADIENT)

        # Build divergence for the supercurrent.
        divergence = builder.build(MatrixType.DIVERGENCE)

        # Update the builder and set fixed sites and link variables for
        # the complex field.
        builder.with_dirichlet_boundary(
            fixed_sites=metal_boundary_index
        ).with_link_exponents(
            link_exponents=vector_potential
        )

        # Build complex field matrices.
        psi_laplacian = builder.build(MatrixType.LAPLACIAN)
        psi_gradient = builder.build(MatrixType.GRADIENT)

        # Initialize the complex field and the scalar potential.
        psi = np.ones_like(mesh.x, dtype=np.complex128)
        psi[metal_boundary_index] = 0
        mu = np.zeros(len(mesh.x))
        mu_boundary = np.zeros_like(mesh.edge_mesh.boundary_edge_indices,
                                    dtype=np.float64)
        mu_boundary[input_edges_index] = current
        mu_boundary[output_edges_index] = -current

        # Create the alpha parameter which weakens the complex field if it
        # is less than unity.
        alpha = np.ones_like(mesh.x, dtype=np.float64)

        # Load the voltage points.
        voltage_points = data_handler.get_voltage_points()

        # Precompute values.
        sq_gamma = gamma ** 2

        # Define the update function.
        def update(state, running_state, psi_val, mu_val,
                   supercurrent_val, normal_current_val):

            # Extract data from the state
            dt_val = state['dt']
            i = state['step']

            # Update the current to allow running IV curves
            if current_max is not None:
                current_val = (current_max - current) \
                              * (i // self.args.steps_per_current) \
                              / (steps // self.args.steps_per_current) + current
                mu_boundary[input_edges_index] = current_val
                mu_boundary[output_edges_index] = -current_val
                state['current'] = current_val
                running_state.append('current', current_val)
            else:
                running_state.append('current', current)

            # Compute the next time step for psi with the discrete gauge
            # invariant discretization presented in chapter 5 in
            # http://urn.kb.se/resolve?urn=urn:nbn:se:kth:diva-312132

            # Compute the absolute square psi
            abs_sq_psi = np.abs(psi_val) ** 2

            # Compute z
            z = np.exp(-1j * mu_val * dt_val) * sq_gamma / 2 * psi_val

            # Compute w
            w = z * abs_sq_psi + np.exp(-1j * mu_val * dt_val) * (
                    psi_val + dt_val / u * np.sqrt(1 + sq_gamma * abs_sq_psi)
                    * ((alpha - abs_sq_psi) * psi_val
                       + psi_laplacian @ psi_val)
            )

            # Compute a
            a = w.real * z.real + w.imag * z.imag

            # Find the modulus squared for the next time step
            new_sq_psi = 2 * np.abs(w) ** 2 / (2 * a + 1 + np.sqrt(
                (2 * a + 1) ** 2 - 4 * np.abs(z) ** 2 * np.abs(w) ** 2))

            # Compute the new psi.
            psi_val = w - z * new_sq_psi

            # Get the supercurrent
            supercurrent_val = get_supercurrent(psi_val, psi_gradient,
                                                mesh.edge_mesh.edges)
            supercurrent_divergence = divergence @ supercurrent_val

            # Solve for mu
            lhs = supercurrent_divergence - (
                    mu_boundary_laplacian @ mu_boundary)
            mu_val = mu_laplacian_lu.solve(lhs)

            normal_current_val = - mu_gradient @ mu_val

            # Update the voltage
            state['flow'] += (mu_val[voltage_points[0]] - mu_val[
                voltage_points[1]]) * state['dt']
            running_state.append('voltage', mu_val[voltage_points[0]] - mu_val[
                voltage_points[1]])

            return psi_val, mu_val, supercurrent_val, normal_current_val

        Runner(
            function=update,
            data_handler=data_handler,
            initial_values=[psi, mu, np.zeros(len(mesh.edge_mesh.edges)),
                            np.zeros(len(mesh.edge_mesh.edges))],
            names=('psi', 'mu', 'supercurrent', 'normal_current'),
            fixed_values=[vector_potential],
            fixed_names=('a',),
            state={
                'current': current,
                'flow': 0,
                'magnetic field': magnetic_field,
                'u': u,
                'gamma': gamma
            },
            running_names=('voltage', 'current'),
            steps=steps,
            dt=dt,
            save_every=save_every,
            logger=self.logger,
            skip=skip,
            miniters=miniters
        ).run()

        data_handler.close()

        end_time = datetime.now()
        self.logger.info(
            'Simulation ended on {}'.format(end_time)
        )
        self.logger.info(
            'Simulation took {}'.format(end_time - start_time)
        )


if __name__ == '__main__':
    Simulate()
