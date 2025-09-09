import unittest
import numpy as np
from src.advanced_quantum_simulation import construct_qft_hamiltonian

class TestQFTSimulation(unittest.TestCase):
    """
    Tests the construction of the Quantum Field Theory Hamiltonian.
    """

    def setUp(self):
        """Set up common parameters for the tests."""
        self.N = 5  # Use a small Fock space for testing
        self.epsilon = 1.5
        self.g = 0.5

    def test_hamiltonian_is_hermitian(self):
        """
        Test that the constructed Hamiltonian is Hermitian (H = H†).
        This is a fundamental requirement for any physical Hamiltonian.
        """
        H = construct_qft_hamiltonian(self.N, self.epsilon, self.g)
        # H.conj().T is the Hermitian conjugate (adjoint)
        np.testing.assert_array_almost_equal(H, H.conj().T)

    def test_hamiltonian_spectrum_for_g_equals_zero(self):
        """
        Test the energy spectrum for the non-interacting case (g=0).
        When g=0, H = ε(a†a), and the eigenvalues should be ε*n for n=0,1,2...
        """
        # Construct the Hamiltonian with no interaction term
        H_simple = construct_qft_hamiltonian(self.N, self.epsilon, g=0.0)

        # Calculate the eigenvalues. Use eigvalsh since we know it's Hermitian.
        eigenvalues = np.linalg.eigvalsh(H_simple)

        # The eigenvalues should be [0*ε, 1*ε, 2*ε, ...]
        expected_eigenvalues = self.epsilon * np.arange(self.N)

        # The calculated eigenvalues are not guaranteed to be sorted.
        eigenvalues.sort()

        np.testing.assert_array_almost_equal(eigenvalues, expected_eigenvalues)

if __name__ == '__main__':
    unittest.main()
