import unittest
import numpy as np
from scipy.linalg import expm

# Import the corrected functions from the simulation
from src.advanced_quantum_simulation import (
    cosmic_duality_operator,
    enhanced_hamiltonian,
)

class TestQuantumPhysics(unittest.TestCase):

    def setUp(self):
        """Initialize a standard test environment."""
        # Use a non-diagonal Hamiltonian for a more robust test.
        self.H0 = np.array([[1.0, 0.5], [0.5, -1.0]], dtype=complex)
        self.chi = 0.1
        self.omega = 1.0
        self.alpha = 0.5

    def test_cosmic_duality_operator_unitarity(self):
        """Test 1: C must be unitary (C†C = I)."""
        C = cosmic_duality_operator(self.chi, self.H0)
        identity = np.eye(self.H0.shape[0])
        product = C.conj().T @ C
        np.testing.assert_array_almost_equal(product, identity)

    def test_spectrum_invariance_under_dressing(self):
        """Test 2: The spectrum of H0 must be invariant under dressing."""
        C = cosmic_duality_operator(self.chi, self.H0)
        H_dressed = C @ self.H0 @ C.conj().T

        eigs_original = np.linalg.eigvals(self.H0)
        eigs_dressed = np.linalg.eigvals(H_dressed)

        # Eigenvalues can be returned in different order, so we sort them.
        eigs_original.sort()
        eigs_dressed.sort()

        np.testing.assert_array_almost_equal(eigs_original, eigs_dressed)

    def test_probability_conservation(self):
        """Test 3: The norm of the state vector must be conserved under time evolution."""
        # Initial state vector (normalized)
        psi_0 = np.array([1.0, 0.0], dtype=complex)

        # Time evolution for a small time step dt
        dt = 0.01
        H_enh_t0 = enhanced_hamiltonian(self.H0, t=0, chi=self.chi, omega=self.omega, alpha=self.alpha)

        # Time evolution operator U = exp(-i H dt / ħ), with ħ=1
        U = expm(-1j * H_enh_t0 * dt)

        psi_t = U @ psi_0

        # Check if norm is still 1
        norm_t = np.linalg.norm(psi_t)
        self.assertAlmostEqual(norm_t, 1.0)

    # Note: As per the audit, further tests are required for a complete validation.
    # - A regression test against a known analytical solution (e.g., Rabi flopping).
    # - A test for energy conservation (or lack thereof in the driven case).
    # - Validation of the LSTM model's physical constraints.
    # These are noted as pending future work.

if __name__ == "__main__":
    unittest.main()
