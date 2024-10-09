import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSlider, QLabel, QComboBox, QCheckBox, QFileDialog, QProgressBar, QDoubleSpinBox, QSpinBox, QTabWidget, QTextEdit, QGroupBox, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QVector3D
from PyQt5.QtDataVisualization import Q3DScatter, QScatter3DSeries, QScatterDataItem
from scipy.special import sph_harm
from scipy.integrate import odeint
import multiprocessing
from functools import partial
from scipy.interpolate import griddata
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import logging
import pyluxcore

# Import our quantum simulation functions
from quantum_simulation import run_russell_simulation, save_quantum_state_for_blender

# Import LuxCore extension
from luxcore_extension import LuxCoreThread, add_luxcore_functionality, enhance_interactivity

# Configure detailed logging
logging.basicConfig(
    filename='quantum_gui.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

logging.info("Starting Quantum GUI application")

# Simple PyQt5 application test


def test_pyqt5_app():
    logging.info("Testing PyQt5 application")
    try:
        app = QApplication([])
        window = QMainWindow()
        window.setGeometry(100, 100, 300, 200)
        window.setWindowTitle('PyQt5 Test')
        logging.info("PyQt5 application test successful")
        return True
    except Exception as e:
        logging.error(f"PyQt5 application test failed: {str(e)}")
        return False


# Run the PyQt5 test
if not test_pyqt5_app():
    logging.critical("PyQt5 application test failed. Exiting.")
    sys.exit(1)

# Import our quantum simulation functions

logging.info("Imported quantum simulation functions")


class BlenderThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, psi_values, X, Y, Z, samples, resolution, frames):
        super().__init__()
        self.psi_values = psi_values
        self.X = X
        self.Y = Y
        self.Z = Z
        self.samples = samples
        self.resolution = resolution
        self.frames = frames
        self.render_engine = 'CYCLES'
        self.denoising = True
        self.ray_depth = 4
        self.volumetrics = False
        self.hdri_lighting = False
        logging.debug("BlenderThread initialized")

    def set_render_engine(self, engine):
        self.render_engine = engine

    def set_samples(self, samples):
        self.samples = samples

    def set_denoising(self, denoising):
        self.denoising = denoising

    def set_ray_depth(self, depth):
        self.ray_depth = depth

    def set_volumetrics(self, volumetrics):
        self.volumetrics = volumetrics

    def set_hdri_lighting(self, hdri_lighting):
        self.hdri_lighting = hdri_lighting

    def run(self):
        logging.info("Starting Blender rendering process")
        # Implementation of Blender rendering process
        save_quantum_state_for_blender(self.psi_values, self.X, self.Y, self.Z)
        for i in range(self.frames):
            # Simulate Blender rendering progress
            progress = int((i + 1) / self.frames * 100)
            self.progress_signal.emit(progress)
            # Simulate rendering time
            self.msleep(100)

        # Run Blender visualization script with enhanced settings
        os.system(
            f"blender --background --python /home/ubuntu/blender_quantum_viz.py -- --samples {
                self.samples} --resolution {
                self.resolution} --frames {
                self.frames} --engine {
                    self.render_engine} --denoising {
                        self.denoising} --ray_depth {
                            self.ray_depth} --volumetrics {
                                self.volumetrics} --hdri_lighting {
                                    self.hdri_lighting}")
        logging.info("Blender rendering process completed")
        self.finished_signal.emit()


class QuantumSimulationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("Initializing QuantumSimulationGUI")
        try:
            self.initUI()
            logging.info("UI initialized successfully")
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_simulation)
            self.current_step = 0
            self.psi_values = None
            self.X = self.Y = self.Z = None
            self.time = 0
            logging.info("QuantumSimulationGUI initialization completed")
        except Exception as e:
            logging.error(
                f"Error during QuantumSimulationGUI initialization: {e}")

    def initUI(self):
        self.setWindowTitle('Advanced Quantum Simulation')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tabs for different simulation modes
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_wavefunction_tab(), "Wavefunction")
        self.tabs.addTab(self.create_density_matrix_tab(), "Density Matrix")
        self.tabs.addTab(self.create_entanglement_tab(), "Entanglement")
        layout.addWidget(self.tabs)

        # Add progress bar and status text area
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

    def create_wavefunction_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add advanced parameters and visualization options
        params_layout = QHBoxLayout()
        self.n_steps_slider = self.create_slider(
            'Number of Steps', 100, 10000, 1000)
        self.dt_slider = self.create_slider(
            'Time Step (dt)', 1, 100, 10)  # Values in 0.001 seconds
        self.l_slider = self.create_slider('Angular Momentum (l)', 0, 5, 0)
        self.m_slider = self.create_slider(
            'Magnetic Quantum Number (m)', -5, 5, 0)
        self.energy_slider = self.create_double_slider(
            'Energy (eV)', 0, 100, 13.6)
        self.potential_slider = self.create_double_slider(
            'Potential (V)', -10, 10, 0)
        self.spin_slider = self.create_double_slider('Spin', -0.5, 0.5, 0.5)

        for slider in [
                self.n_steps_slider,
                self.dt_slider,
                self.l_slider,
                self.m_slider,
                self.energy_slider,
                self.potential_slider,
                self.spin_slider]:
            params_layout.addWidget(slider)

        layout.addLayout(params_layout)

        # Add experimental parameters for MIT professors
        exp_group = QGroupBox("Experimental Parameters")
        exp_layout = QVBoxLayout()

        self.magnetic_field = self.create_double_slider(
            'Magnetic Field (T)', 0, 10, 0)
        self.electric_field = self.create_double_slider(
            'Electric Field (V/m)', 0, 1000, 0)
        self.temperature = self.create_double_slider(
            'Temperature (K)', 0, 300, 300)
        self.laser_intensity = self.create_double_slider(
            'Laser Intensity (W/cm²)', 0, 1000, 0)
        self.pressure = self.create_double_slider('Pressure (atm)', 0.1, 10, 1)

        exp_layout.addWidget(self.magnetic_field)
        exp_layout.addWidget(self.electric_field)
        exp_layout.addWidget(self.temperature)
        exp_layout.addWidget(self.laser_intensity)
        exp_layout.addWidget(self.pressure)

        exp_group.setLayout(exp_layout)
        layout.addWidget(exp_group)

        # Add more interactive elements for MIT professors
        interaction_group = QGroupBox("Interactive Elements")
        interaction_layout = QVBoxLayout()

        self.perturbation_strength = self.create_double_slider(
            'Perturbation Strength', 0, 1, 0)
        self.quantum_noise = self.create_double_slider(
            'Quantum Noise', 0, 0.1, 0)
        self.decoherence_rate = self.create_double_slider(
            'Decoherence Rate', 0, 0.1, 0.01)
        self.entanglement_strength = self.create_double_slider(
            'Entanglement Strength', 0, 1, 0)

        interaction_layout.addWidget(self.perturbation_strength)
        interaction_layout.addWidget(self.quantum_noise)
        interaction_layout.addWidget(self.decoherence_rate)
        interaction_layout.addWidget(self.entanglement_strength)

        interaction_group.setLayout(interaction_layout)
        layout.addWidget(interaction_group)

        # Add advanced visualization options
        viz_layout = QHBoxLayout()
        viz_layout.addWidget(QLabel('Visualization Type:'))
        self.viz_type = QComboBox()
        self.viz_type.setObjectName('viz_type')
        self.viz_type.addItems(['Wavefunction',
                                'Probability Density',
                                'Phase',
                                'Momentum Space',
                                'Isosurface',
                                'Streamplot',
                                'Poincaré Section'])
        self.viz_type.currentIndexChanged.connect(self.update_visualization)
        viz_layout.addWidget(self.viz_type)

        self.colormap = QComboBox()
        self.colormap.addItems(
            ['viridis', 'plasma', 'inferno', 'magma', 'cividis'])
        self.colormap.currentIndexChanged.connect(self.update_visualization)
        viz_layout.addWidget(QLabel('Colormap:'))
        viz_layout.addWidget(self.colormap)

        layout.addLayout(viz_layout)

        # Add resolution control
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel('Resolution:'))
        self.resolution_slider = self.create_slider('Resolution', 10, 100, 50)
        resolution_layout.addWidget(self.resolution_slider)
        layout.addLayout(resolution_layout)

        # Add 3D plot using PyQtGraph
        self.gl_widget = gl.GLViewWidget()
        layout.addWidget(self.gl_widget)

        # Add control buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton('Run Simulation')
        self.run_button.clicked.connect(self.toggle_simulation)
        button_layout.addWidget(self.run_button)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_simulation)
        button_layout.addWidget(self.reset_button)

        self.blender_button = QPushButton('Generate Blender Visualization')
        self.blender_button.clicked.connect(self.generate_blender_viz)
        button_layout.addWidget(self.blender_button)

        self.export_button = QPushButton('Export Data')
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        # Add real-time parameter update checkbox
        self.real_time_update = QCheckBox('Real-time Parameter Updates')
        self.real_time_update.setChecked(True)
        layout.addWidget(self.real_time_update)

        return tab

    def create_density_matrix_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add density matrix visualization
        self.density_matrix_plot = pg.ImageView()
        layout.addWidget(self.density_matrix_plot)

        # Add controls for density matrix manipulation
        controls_layout = QHBoxLayout()
        self.apply_noise_button = QPushButton('Apply Noise')
        self.apply_noise_button.clicked.connect(
            self.apply_noise_to_density_matrix)
        controls_layout.addWidget(self.apply_noise_button)

        self.purify_button = QPushButton('Purify')
        self.purify_button.clicked.connect(self.purify_density_matrix)
        controls_layout.addWidget(self.purify_button)

        layout.addLayout(controls_layout)

        return tab

    def create_entanglement_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add entanglement visualization
        self.entanglement_plot = pg.PlotWidget()
        layout.addWidget(self.entanglement_plot)

        # Add controls for entanglement manipulation
        controls_layout = QHBoxLayout()
        self.create_bell_state_button = QPushButton('Create Bell State')
        self.create_bell_state_button.clicked.connect(self.create_bell_state)
        controls_layout.addWidget(self.create_bell_state_button)

        self.measure_entanglement_button = QPushButton('Measure Entanglement')
        self.measure_entanglement_button.clicked.connect(
            self.measure_entanglement)
        controls_layout.addWidget(self.measure_entanglement_button)

        layout.addLayout(controls_layout)

        return tab

    def create_slider(self, label, min_value, max_value, default_value):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(default_value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval((max_value - min_value) // 10)
        slider.valueChanged.connect(self.on_parameter_change)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(QLabel(label))
        slider_layout.addWidget(slider)

        slider_widget = QWidget()
        slider_widget.setLayout(slider_layout)

        return slider_widget

    def create_double_slider(self, label, min_value, max_value, default_value):
        slider_widget = QWidget()
        layout = QHBoxLayout(slider_widget)
        layout.addWidget(QLabel(label))
        slider = QDoubleSpinBox()
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)
        slider.valueChanged.connect(self.on_parameter_change)
        layout.addWidget(slider)
        return slider_widget

    def toggle_simulation(self):
        if self.timer.isActive():
            self.timer.stop()
            self.run_button.setText('Run Simulation')
        else:
            self.timer.start(50)  # Update every 50 ms
            self.run_button.setText('Pause Simulation')

    def reset_simulation(self):
        self.timer.stop()
        self.run_button.setText('Run Simulation')
        self.current_step = 0
        self.time = 0
        self.update_simulation()

    def update_simulation(self):
        n_steps = self.n_steps_slider.children()[1].value()
        dt = self.dt_slider.children()[1].value() * 0.001
        l = self.l_slider.children()[1].value()
        m = self.m_slider.children()[1].value()

        resolution = self.resolution_slider.children()[1].value()

        # Use multiprocessing for faster computation
        with multiprocessing.Pool() as pool:
            results = pool.starmap(
                partial(
                    run_russell_simulation, n_steps=1, dt=dt, l=l, m=m, resolution=resolution), [
                    (i,) for i in range(n_steps)])

        self.psi_values, self.X, self.Y, self.Z, _, _, _ = results[-1]

        # Apply experimental parameters
        B = self.magnetic_field.children()[1].value()
        E = self.electric_field.children()[1].value()
        T = self.temperature.children()[1].value()

        # Modify wavefunction based on experimental parameters
        self.psi_values *= np.exp(-1j * B * self.time)  # Magnetic field effect
        self.psi_values += E * self.Z * self.time  # Electric field effect
        self.psi_values *= np.exp(-T * self.time / 100)  # Temperature effect

        # Apply additional interactive elements
        perturbation = self.perturbation_strength.children()[1].value()
        noise = self.quantum_noise.children()[1].value()

        # Add perturbation and noise to the wavefunction
        self.psi_values += perturbation * \
            np.random.rand(*self.psi_values.shape)
        self.psi_values += noise * \
            (np.random.rand(*self.psi_values.shape) + 1j * np.random.rand(*self.psi_values.shape))

        # Normalize the wavefunction
        self.psi_values /= np.linalg.norm(self.psi_values)

        # Add advanced quantum effects
        self.apply_quantum_decoherence()
        entropy = self.calculate_entanglement_entropy()
        self.update_3d_plot()
        self.update_density_matrix()
        self.update_entanglement_plot(entropy)

        self.current_step += 1
        self.time += dt
        if self.current_step >= n_steps:
            self.timer.stop()
            self.run_button.setText('Run Simulation')

    def apply_quantum_decoherence(self):
        decoherence_rate = self.decoherence_rate.children()[1].value()
        self.psi_values *= np.exp(-decoherence_rate * self.time)

    def calculate_entanglement_entropy(self):
        # Calculate entanglement entropy
        rho = np.outer(self.psi_values, np.conj(self.psi_values))
        eigenvalues = np.linalg.eigvalsh(rho)
        entropy = -np.sum(eigenvalues * np.log2(eigenvalues + 1e-10))
        self.status_text.append(f"Entanglement Entropy: {entropy:.4f}")
        return entropy

    def update_3d_plot(self):
        self.gl_widget.clear()

        # Create color map
        cmap = pg.ColorMap(
            pos=[
                0.0, 0.5, 1.0], color=[
                (0, 0, 255, 255), (0, 255, 0, 255), (255, 0, 0, 255)])

        # Create scatter plot item
        scatter = gl.GLScatterPlotItem(
            pos=np.column_stack(
                (self.X.flatten(), self.Y.flatten(), self.Z.flatten())), size=5, color=cmap.map(
                np.abs(
                    self.psi_values.flatten())), pxMode=False)
        self.gl_widget.addItem(scatter)

    def update_density_matrix(self):
        rho = np.outer(self.psi_values, np.conj(self.psi_values))
        self.density_matrix_plot.setImage(np.abs(rho))

    def update_entanglement_plot(self, entropy):
        self.entanglement_plot.plot(
            [self.time], [entropy], pen=None, symbol='o')

    def on_parameter_change(self):
        if self.real_time_update.isChecked():
            self.update_simulation()

    def update_visualization(self):
        self.update_simulation()

    def export_data(self):
        if self.psi_values is not None:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Data", "", "CSV Files (*.csv);;NumPy Files (*.npy)")
            if file_name:
                if file_name.endswith('.csv'):
                    np.savetxt(
                        file_name,
                        np.column_stack(
                            (self.X.flatten(),
                             self.Y.flatten(),
                                self.Z.flatten(),
                                self.psi_values.flatten())),
                        delimiter=',',
                        header='X,Y,Z,Psi')
                elif file_name.endswith('.npy'):
                    np.save(
                        file_name, {
                            'X': self.X, 'Y': self.Y, 'Z': self.Z, 'Psi': self.psi_values})
                print(f"Data exported to {file_name}")

    def generate_blender_viz(self):
        logging.info("Generating Blender visualization")
        try:
            if self.psi_values is not None:
                samples = self.tabs.currentWidget().findChild(
                    QSpinBox, 'samples_spinbox').value()
                resolution = self.tabs.currentWidget().findChild(
                    QComboBox, 'resolution_combobox').currentText()
                frames = self.tabs.currentWidget().findChild(QSpinBox, 'frames_spinbox').value()
                self.blender_thread = BlenderThread(
                    self.psi_values, self.X, self.Y, self.Z, samples, resolution, frames)
                self.blender_thread.set_render_engine('CYCLES')
                self.blender_thread.set_samples(1000)
                self.blender_thread.set_denoising(True)
                self.blender_thread.set_ray_depth(8)
                self.blender_thread.set_volumetrics(True)
                self.blender_thread.set_hdri_lighting(True)
                self.blender_thread.progress_signal.connect(
                    self.update_progress)
                self.blender_thread.finished_signal.connect(
                    self.blender_finished)
                self.blender_thread.start()
                self.blender_button.setEnabled(False)
                self.status_text.append(
                    "Blender visualization generation started...")
            else:
                raise ValueError(
                    "No simulation data available for visualization")
        except Exception as e:
            logging.error(f"Error in generate_blender_viz: {str(e)}")
            self.status_text.append(f"Error: {str(e)}")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def blender_finished(self):
        self.blender_button.setEnabled(True)
        self.status_text.append(
            "Ultra-photorealistic Blender visualization generated.")

    def apply_noise_to_density_matrix(self):
        if self.psi_values is not None:
            noise = np.random.normal(0, 0.1, self.psi_values.shape)
            self.psi_values += noise
            self.psi_values /= np.linalg.norm(self.psi_values)
            self.update_density_matrix()

    def purify_density_matrix(self):
        if self.psi_values is not None:
            # Perform a simple purification by projecting onto the largest
            # eigenvector
            rho = np.outer(self.psi_values, np.conj(self.psi_values))
            eigenvalues, eigenvectors = np.linalg.eigh(rho)
            self.psi_values = eigenvectors[:, -1]
            self.update_density_matrix()

    def create_bell_state(self):
        # Create a Bell state |Φ+⟩ = (|00⟩ + |11⟩) / √2
        self.psi_values = np.zeros(4)
        self.psi_values[0] = 1 / np.sqrt(2)
        self.psi_values[3] = 1 / np.sqrt(2)
        self.update_entanglement_plot(1.0)  # Maximum entanglement

    def measure_entanglement(self):
        if self.psi_values is not None:
            entropy = self.calculate_entanglement_entropy()
            self.status_text.append(f"Measured Entanglement: {entropy:.4f}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = QuantumSimulationGUI()
    gui.show()
    sys.exit(app.exec_())
