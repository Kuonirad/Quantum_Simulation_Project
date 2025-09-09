import numpy as np
from qiskit_aer.primitives import Estimator as AerEstimator
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import SPSA

# Imports verified from the official Qiskit Nature v0.7 tutorial
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import UCCSD
from qiskit_nature.second_q.algorithms import GroundStateEigensolver

class ElectronicStructureSolver:
    """
    A solver for electronic structure problems using the modern Qiskit Nature API.
    This implementation is based on the official Qiskit Nature v0.7 tutorials.
    """

    def __init__(self, atom_string: str, basis: str = "sto3g"):
        """
        Initializes the solver.

        Args:
            atom_string: A string describing the molecule's atoms and coordinates.
                         e.g., "H 0 0 0; H 0 0 0.735"
            basis: The basis set for the electronic structure calculation.
        """
        self.driver = PySCFDriver(
            atom=atom_string,
            basis=basis,
            charge=0,
            spin=0,
            unit=DistanceUnit.ANGSTROM,
        )
        self.problem = None
        self.mapper = None

    def _setup_problem_and_mapper(self):
        """Sets up the electronic structure problem and the qubit mapper."""
        self.problem = self.driver.run()
        # The ParityMapper is a good choice as it allows for 2-qubit reduction.
        self.mapper = ParityMapper(num_particles=self.problem.num_particles)

    def calculate_ground_state_energy(self) -> dict:
        """
        Calculates the ground state energy of the molecule using VQE.
        """
        if self.problem is None:
            self._setup_problem_and_mapper()

        # Use a local, noiseless simulator from Qiskit Aer
        estimator = AerEstimator()

        # Use a chemically-inspired ansatz (Unitary Coupled Cluster)
        ansatz = UCCSD(
            self.problem.num_spatial_orbitals,
            self.problem.num_particles,
            self.mapper,
            initial_state=self.problem.initial_state,
        )

        # Configure the VQE algorithm with a classical optimizer
        vqe_solver = VQE(estimator, ansatz, SPSA(maxiter=100))

        # GroundStateEigensolver is the main entry point
        gse = GroundStateEigensolver(self.mapper, vqe_solver)
        result = gse.solve(self.problem)

        return {
            "total_energy_hartree": result.total_energies[0],
            "raw_qiskit_nature_result": result
        }

if __name__ == '__main__':
    # Example usage for H2 molecule at equilibrium bond length
    solver = ElectronicStructureSolver("H 0 0 0; H 0 0 0.735")
    results = solver.calculate_ground_state_energy()

    print("--- H2 Ground State Energy Calculation ---")

    fci_energy = -1.13728  # Known exact energy for H2 at this distance/basis
    vqe_energy = results['total_energy_hartree']

    print(f"VQE Result: {vqe_energy:.6f} Hartree")
    print(f"FCI (Exact) Result: {fci_energy:.6f} Hartree")
    print(f"VQE Error: {abs(vqe_energy - fci_energy):.6f} Hartree")

    # Check if the result is reasonably close to the exact value
    assert abs(vqe_energy - fci_energy) < 0.01, "VQE energy is not close to the FCI energy."
    print("\nSolver validation successful!")
