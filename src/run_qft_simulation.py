import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm
from advanced_quantum_simulation import construct_qft_hamiltonian

def run_simulation():
    """
    Runs and visualizes the driven quantum field simulation.
    """
    # --- Simulation Parameters ---
    N = 10              # Truncated Fock space dimension (0 to 9 particles)
    epsilon = 1.0       # Energy of a single particle
    g = 1.5             # Coupling strength to the driving field

    T = 20.0            # Total simulation time
    dt = 0.05           # Time step
    timesteps = int(T / dt)

    # --- Setup ---
    # Construct the Hamiltonian for the system
    H = construct_qft_hamiltonian(N, epsilon, g)

    # Also need the number operator to calculate expectation value
    a = np.zeros((N, N), dtype=complex)
    for j in range(1, N):
        a[j-1, j] = np.sqrt(j)
    a_dag = a.conj().T
    num_op = a_dag @ a

    # Initial state is the vacuum state |0>
    psi_0 = np.zeros(N, dtype=complex)
    psi_0[0] = 1.0

    # Time evolution operator for a single step
    U_dt = expm(-1j * H * dt)

    # --- Simulation Loop ---
    psi_t = psi_0
    particle_counts = []
    times = []

    for i in range(timesteps):
        # Calculate the expectation value of the number operator
        # <N>(t) = <psi(t)| N |psi(t)>
        n_t = np.vdot(psi_t, num_op @ psi_t).real
        particle_counts.append(n_t)
        times.append(i * dt)

        # Evolve the state by one time step
        psi_t = U_dt @ psi_t

    # --- Visualization ---
    plt.figure(figsize=(12, 6))
    plt.plot(times, particle_counts, label=f"g = {g}")
    plt.xlabel("Time")
    plt.ylabel("Expectation Value of Particle Number, <N>")
    plt.title("Particle Creation and Annihilation in a Driven Quantum Field")
    plt.grid(True)
    plt.legend()
    plt.savefig("qft_simulation_particle_number.png")
    print("Simulation complete. Plot saved to 'qft_simulation_particle_number.png'")

if __name__ == "__main__":
    run_simulation()
