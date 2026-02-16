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

Utils for homormophic encryption simulation.
"""

import numpy as np
from qiskit.compiler import transpile
from qiskit_aer import AerSimulator

def count_gates(circuit,gates,as_list=False):
    """Count the number of gates.
    Args:
        circuit: Quantum circuit.
        gates: List of gates or a single gate as string.
        as_list: If True, a list with an individual counter for each gate is provided.
    Returns:
        counter: Total number of gates or a list with the number of each gate.
    """
    
    if type(gates) == str: gates = [gates]
    
    data = circuit.data
    counter = [0]*len(gates)
    for d in data:
        name = d[0].name
        for index, gate in enumerate(gates):
            if name == gates[index]:
                counter[index] += 1
    
    if not as_list: counter = sum(counter)
    
    return counter

def reverse_counts(counts):
    """Reverse the order of the bits.
    Args:
        counts: Dictionary with the counts of the simulation.
    Returns:
        reversed_counts: Dictionary with the counts after reversing the bits order.
    """
    
    reversed_counts = {}
    for key in counts:
        reversed_counts[key[::-1]] = counts[key]
    
    return reversed_counts

def run_circuit(circuit,shots=None,reverse=True):
    """Run a quantum circuit.
    Args:
        circuit: Quantum circuit.
        shots: Number of shots.
        reverse: If True, the order of the bits is reversed.
    Returns:
        counts: Dictionary with the counts.
    """
    
    simulator = AerSimulator()
    circuit = transpile(circuit, simulator)
    job = simulator.run(circuit, shots=shots)
    counts = job.result().get_counts(0)
    if reverse == False: return counts
    else: return reverse_counts(counts)

def last_register_counts(counts):
    """Obtain the counts only for the last classical register.
    Args:
        counts: Dictionary with the counts of the simulation.
    Returns:
        last_counts: Dictionary with the counts of the last register.
    """
    
    last_counts = {}
    for key in counts:
        last_key = key.split()[-1]
        if last_counts.get(last_key) is None:
            last_counts[last_key] = counts[key]
        else:
            last_counts[last_key] += counts[key]
    
    return last_counts

def decrypt_counts(counts,measured_positions):
    """Decrypt the counts using the final key.
    Args:
        counts: Encrypted counts.
        measured_positions: Positions in the circuit of the qubits being measured.
    Returns:
        decrypted_counts: Decrypted counts.
    """
    
    decrypted_counts = {}
    for chain in counts:
        f_value = chain.split(' ')[-1]
        f_key = chain.split(' ')[2]
        f_value = [int(number) for number in f_value]
        f_key = [int(f_key[index]) for index in measured_positions]
        decrypted_chain = ''.join([str(f_key[index]^f_value[index]) for index in range(len(f_value))])
        if decrypted_counts.get(decrypted_chain) is None:
            decrypted_counts[decrypted_chain] = counts[chain]
        else:
            decrypted_counts[decrypted_chain] += counts[chain]
    
    return decrypted_counts

def counts_to_probability_distribution(counts):
    """
    Args:
        counts: Dictionary with the counts of the simulation.
    Returns:
        probability_distribution: Numpy array with the probability distribution.
    """
    
    # Take the number of elements in the computational basis.
    N = 2**(len(list(counts.keys())[0]))
    
    # Transform the counts into a probability distribution vector.
    probability_distribution = np.zeros(N)
    for bitstring in counts:
        probability_distribution[int(bitstring,2)] = counts[bitstring]
    probability_distribution = probability_distribution / sum(probability_distribution)
    
    return probability_distribution