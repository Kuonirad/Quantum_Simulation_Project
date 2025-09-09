import numpy as np
from scipy.linalg import expm

# This file now contains only the core, numpy-based physics simulation logic.
# All visualization and ML code has been moved to other modules.

def cosmic_duality_operator(chi, H):
    """Implements the Cosmic Duality Operator C = exp(i χ H)."""
    return expm(1j * chi * H)

def rbi_operator(t, omega, alpha, H0):
    """
    Implements the Rhythmic Balanced Interchange operator as a Hamiltonian term.
    For a 2-level system, this is H_RB(t) = α ħω sin(ωt) σ̂_x.
    """
    if H0.shape != (2, 2):
        raise NotImplementedError("RBI operator is currently only implemented for 2x2 Hamiltonians.")

    sigma_x = np.array([[0, 1], [1, 0]])
    h_bar = 1
    energy_factor = alpha * h_bar * omega
    return energy_factor * np.sin(omega * t) * sigma_x

def enhanced_hamiltonian(H0, t, chi=0.1, omega=1.0, alpha=0.5):
    """
    Constructs the enhanced Hamiltonian: H_enh = Ĉ H₀ Ĉ† + Ĥ_RB(t).
    """
    C = cosmic_duality_operator(chi, H0)
    H_RB = rbi_operator(t, omega, alpha, H0)
    H_enhanced = C @ H0 @ C.conj().T + H_RB
    return H_enhanced

print("Core quantum physics module initialized.")

def construct_qft_hamiltonian(N: int, epsilon: float, g: float) -> np.ndarray:
    """
    Constructs the Hamiltonian for a driven quantum field model.

    This model describes a system where particles can be created and destroyed.
    The Hamiltonian is H = ε(a†a) + g(a + a†).

    Args:
        N: The dimension of the truncated Fock space (i.e., the maximum
           number of particles + 1).
        epsilon: The energy of a single particle/quantum.
        g: The coupling strength of the driving field that creates/destroys particles.

    Returns:
        The Hamiltonian as a complex numpy array.
    """
    # Create the annihilation operator `a`
    a = np.zeros((N, N), dtype=complex)
    for j in range(1, N):
        a[j-1, j] = np.sqrt(j)

    # The creation operator `a†` is the adjoint of `a`
    a_dag = a.conj().T

    # The number operator N = a†a
    num_op = a_dag @ a

    # The interaction term
    interaction_op = a + a_dag

    # Construct the Hamiltonian
    H = epsilon * num_op + g * interaction_op

    return H
