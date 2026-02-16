# Copyright 2024 Sergio A. Ortega, Pablo Fernandez and Miguel A. Martin-Delgado.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CQC-QHE: Classical-Quantum Circuits for Quantum Homomorphic Encryption.

This is a package based on Qiskit with utilities to simulate quantum
homomorphic encryption schemes using classical-quantum circuits.
"""

__version__ = '2.0'

try:
    from qiskit import __version__ as qiskit_version
except Exception:
    raise Exception("Qiskit version must be >= 1.0 and < 2.0.")
if qiskit_version[0] != '1':
    raise Exception('Qiskit version must be >= 1.0 and < 2.0.')

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from cqc_qhe.utils import *
from cqc_qhe.compilators import *
from cqc_qhe.circuits import *
from cqc_qhe.gridsynth import *

__all__ = [
    'count_gates',
    'compile_clifford_t_circuit',
    'compile_rz_gate',
    'compile_rotations',
    'reverse_counts',
    'run_circuit',
    'classical_swap',
    'classical_cnot',
    'classical_reset',
    'create_homomorphic_circuit',
    'create_simplified_homomorphic_circuit',
    'last_register_counts',
    'decrypt_counts',
    'counts_to_probability_distribution',
    'install_gridsynth',
    'uninstall_gridsynth',
    'check_gridsynth',
    'gridsynth']