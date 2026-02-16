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

Compilators in Clifford+T gates.
"""

import numpy as np
import re
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from cqc_qhe.utils import count_gates
from cqc_qhe.gridsynth import gridsynth, check_gridsynth
import warnings

def toffoli(circuit,qubits):
    """Apply a toffoli gate with Clifford+T gates.
    Args:
        circuit: Quantum circuit.
        qubits: Set of qubits where the gate is applied.
    """
    
    circuit.h(qubits[2])
    circuit.cx(qubits[1],qubits[2])
    circuit.tdg(qubits[2])
    circuit.cx(qubits[0],qubits[2])
    circuit.t(qubits[2])
    circuit.cx(qubits[1],qubits[2])
    circuit.tdg(qubits[2])
    circuit.cx(qubits[0],qubits[2])
    circuit.t(qubits[1])
    circuit.t(qubits[2])
    circuit.cx(qubits[0],qubits[1])
    circuit.h(qubits[2])
    circuit.t(qubits[0])
    circuit.tdg(qubits[1])
    circuit.cx(qubits[0],qubits[1])

def control_h(circuit,qubits):
    """Apply a control-H gate with Clifford+T gates.
    Args:
        circuit: Quantum circuit.
        qubits: Set of qubits where the gate is applied.
    """
    
    # H = S @ H @ T @ H @ Sdg @ H @ X @ H @ S @ H @ Tdg @ H @ Sdg
    circuit.sdg(qubits[1])
    circuit.h(qubits[1])
    circuit.tdg(qubits[1])
    circuit.h(qubits[1])
    circuit.s(qubits[1])
    circuit.h(qubits[1])
    circuit.cx(qubits[0],qubits[1])
    circuit.h(qubits[1])
    circuit.sdg(qubits[1])
    circuit.h(qubits[1])
    circuit.t(qubits[1])
    circuit.h(qubits[1])
    circuit.s(qubits[1])

def control_rx(theta,circuit,qubits):
    """Apply a control-Rx gate with Clifford+T gates.
    Args:
        circuit: Quantum circuit.
        qubits: Set of qubits where the gate is applied.
    """
    
    circuit.h(qubits[1])
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(-theta/2,qubits[1])
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(theta/2,qubits[1])
    circuit.h(qubits[1])

def control_ry(theta,circuit,qubits):
    """Apply a control-Ry gate with Clifford+T gates.
    Args:
        circuit: Quantum circuit.
        qubits: Set of qubits where the gate is applied.
    """
    
    circuit.sdg(qubits[1])
    circuit.h(qubits[1])
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(-theta/2,qubits[1])
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(theta/2,qubits[1])
    circuit.h(qubits[1])
    circuit.s(qubits[1])

def control_rz(theta,circuit,qubits):
    """Apply a control-Rz gate with Clifford+T gates.
    Args:
        circuit: Quantum circuit.
        qubits: Set of qubits where the gate is applied.
    """
    
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(-theta/2,qubits[1])
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(theta/2,qubits[1])

def control_p(theta,circuit,qubits):
    """Apply a control-P gate with Clifford+T gates.
    Args:
        circuit: Quantum circuit.
        qubits: Set of qubits where the gate is applied.
    """
    
    circuit.p(theta/2,qubits[0])
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(-theta/2,qubits[1])
    circuit.cx(qubits[0],qubits[1])
    circuit.rz(theta/2,qubits[1])

def compile_rz_gate(theta,error=None,pauli=True,seed=32):
    """Compile an Rz or phase gate in Clifford+T gates.
    Args:
        theta: Angle of the gate.
        error: Error of the decomposition. Default: 1e-10.
        pauli: If True, double S gates are turned into Z gates.
        seed: Random seed for the gridsynth algorithm. Default: 32.
    Returns:
        chain: String with the sequence of Clifford+T gates.
    """
    
    while theta < 0: theta += 2*np.pi
    while theta > 2*np.pi: theta -= 2*np.pi
    
    chain = gridsynth(theta,error,seed)
    
    if chain == '':
        chain = 'I'
    
    if pauli:
        chain = re.sub(r"SSS", "SZ", chain)
        chain = re.sub(r"SS", "Z", chain)
    
    return chain

def empty_circuit(circuit):
    
    # Obtain the quantum and classical registers of the original circuit.
    quantum_registers = []
    for index in range(len(circuit.qubits)):
        r = circuit.find_bit(circuit.qubits[index]).registers[0][0]
        if r not in quantum_registers:
            quantum_registers.append(r)
    classical_registers = []
    for index in range(len(circuit.clbits)):
        r = circuit.find_bit(circuit.clbits[index]).registers[0][0]
        if r not in classical_registers:
            classical_registers.append(r)
    
    # Instantiate the empty circuit.
    empty_circuit = QuantumCircuit()
    for index in range(len(quantum_registers)):
        empty_circuit.add_register(quantum_registers[index])
    for index in range(len(classical_registers)):
        empty_circuit.add_register(classical_registers[index])
    
    return empty_circuit

def compile_clifford_t_circuit(circuit,error_circuit=None,ancilla_top=False,error_gate=None,compile_rz=True,seed=32):
    """Compile a quantum circuit in Clifford+T gates.
    Args:
        circuit: Quantum circuit to compile.
        error_circuit: Error of approximating the circuit.
        ancilla_top: If True, the ancilla register is at the top of the circuit.
        error_gate: Error of each individual Rz and phase gate.
        compile_rz: If False, Rz and phase gates are not compiled.
        seed: Random seed for the gridsynth algorithm. Default: 32.
    Returns:
        compiled_circuit: Compiled circuit in Clifford+T gates.
    Raises:
        Exception: If the set of gates is not correct.
        Exception: If values are provided for both error_circuit and error_gate.
    """
    
    if error_circuit is not None and error_gate is not None:
        raise Exception("The declaration of both error_circuit and error_gate is ambiguous. Use only one.")
    
    data = circuit.data
    
    # Calculate the number of qubit ancilla necessary.
    max_dots = 0
    for d in data:
        name = d[0].name
        if name == 'mcx' or name == 'mcx_gray':
            dots = d[0].num_qubits-1
            if dots > max_dots:
                max_dots = dots
    n_ancilla = max_dots-2
    if n_ancilla < 0: n_ancilla = 0
    
    # Create a quantum register with the ancillas.
    ancilla_reg = QuantumRegister(n_ancilla,'anc')
    
    # Obtain the quantum and classical registers of the original circuit.
    quantum_registers = []
    for index in range(len(circuit.qubits)):
        r = circuit.find_bit(circuit.qubits[index]).registers[0][0]
        if r not in quantum_registers:
            quantum_registers.append(r)
    classical_registers = []
    for index in range(len(circuit.clbits)):
        r = circuit.find_bit(circuit.clbits[index]).registers[0][0]
        if r not in classical_registers:
            classical_registers.append(r)
    
    # Instantiate the compiled circuit.
    compiled_circuit = QuantumCircuit()
    if ancilla_top: compiled_circuit.add_register(ancilla_reg)
    for index in range(len(quantum_registers)):
        compiled_circuit.add_register(quantum_registers[index])
    if not ancilla_top: compiled_circuit.add_register(ancilla_reg)
    for index in range(len(classical_registers)):
        compiled_circuit.add_register(classical_registers[index])
    
    # Copy the Clifford+T gates and compile the others.
    for d in data:
        name = d[0].name
        qubits = d[1]
        clbits = d[2]
        
        if name == 'barrier':
            compiled_circuit.barrier(qubits)
        elif name == 'x':
            compiled_circuit.x(qubits)
        elif name == 'z':
            compiled_circuit.z(qubits)
        elif name == 'h':
            compiled_circuit.h(qubits)
        elif name == 's':
            compiled_circuit.s(qubits)
        elif name == 'sdg':
            compiled_circuit.sdg(qubits)
        elif name == 't':
            compiled_circuit.t(qubits)
        elif name == 'tdg':
            compiled_circuit.tdg(qubits)
        elif name == 'cx':
            compiled_circuit.cx(qubits[0],qubits[1])
        
        elif name == 'y':
            compiled_circuit.x(qubits)
            compiled_circuit.z(qubits)
        elif name == 'cy':
            compiled_circuit.sdg(qubits[1])
            compiled_circuit.h(qubits[1])
            compiled_circuit.cx(qubits[0],qubits[1])
            compiled_circuit.h(qubits[1])
            compiled_circuit.s(qubits[1])
        elif name == 'cz':
            compiled_circuit.h(qubits[1])
            compiled_circuit.cx(qubits[0],qubits[1])
            compiled_circuit.h(qubits[1])
        
        elif name == 'ccx':
            toffoli(compiled_circuit,(qubits[0],qubits[1],qubits[2]))
        elif name == 'rx':
            theta = d[0].params[0]
            compiled_circuit.h(qubits)
            compiled_circuit.rz(theta,qubits)
            compiled_circuit.h(qubits)
        elif name == 'ry':
            theta = d[0].params[0]
            compiled_circuit.sdg(qubits)
            compiled_circuit.h(qubits)
            compiled_circuit.rz(theta,qubits)
            compiled_circuit.h(qubits)
            compiled_circuit.s(qubits)
        elif name == 'rz':
            theta = d[0].params[0]
            compiled_circuit.rz(theta,qubits)
        elif name == 'p':
            theta = d[0].params[0]
            compiled_circuit.p(theta,qubits)
        elif name == 'ch':
            control_h(compiled_circuit,qubits)
        elif name == 'crx':
            theta = d[0].params[0]
            control_rx(theta,compiled_circuit,qubits)
        elif name == 'cry':
            theta = d[0].params[0]
            control_ry(theta,compiled_circuit,qubits)
        elif name == 'crz':
            theta = d[0].params[0]
            control_rz(theta,compiled_circuit,qubits)
        elif name == 'cp':
            theta = d[0].params[0]
            control_p(theta,compiled_circuit,qubits)
        
        elif name == 'u':
            theta, phi, lam = d[0].params
            compiled_circuit.rz(lam,qubits)
            compiled_circuit.h(qubits)
            compiled_circuit.s(qubits)
            compiled_circuit.h(qubits)
            compiled_circuit.rz(theta,qubits)
            compiled_circuit.h(qubits)
            compiled_circuit.sdg(qubits)
            compiled_circuit.h(qubits)
            compiled_circuit.rz(phi,qubits)
        
        elif (name == 'mcx' or name == 'mcx_gray'):
            number_anc = len(qubits)-1 -2
            toffoli(compiled_circuit,(qubits[0],qubits[1],ancilla_reg[0]))
            for index in range(1,number_anc):
                toffoli(compiled_circuit,(qubits[1+index],ancilla_reg[index-1],ancilla_reg[index]))
            toffoli(compiled_circuit,(qubits[-2],ancilla_reg[number_anc-1],qubits[-1]))
            for index in range(number_anc-1,1-1,-1):
                toffoli(compiled_circuit,(qubits[1+index],ancilla_reg[index-1],ancilla_reg[index]))
            toffoli(compiled_circuit,(qubits[0],qubits[1],ancilla_reg[0]))
        
        elif name == 'swap':
            compiled_circuit.cx(qubits[0],qubits[1])
            compiled_circuit.cx(qubits[1],qubits[0])
            compiled_circuit.cx(qubits[0],qubits[1])
        
        elif name == 'measure':
            compiled_circuit.measure(qubits,clbits)
        elif name == 'reset':
            compiled_circuit.reset(qubits)
        
        else:
            raise Exception(f'Wrong gate in the circuit: {name}')
    
    # Compile the Rz gates.
    if compile_rz:
        
        number_rz = count_gates(compiled_circuit,['rz','p'])
        
        if number_rz > 0:
        
            # Calculate the error per gate.
            if error_circuit is not None: error_gate = error_circuit / number_rz
            
            compiled_circuit = compile_rotations(compiled_circuit,error_gate)
    
    return compiled_circuit

def compile_rotations(circuit,error_gate=None,seed=32):
    """Compile a quantum circuit in Clifford+T gates.
    Args:
        circuit: Quantum circuit to compile.
        error: Error of the Rz decomposition. Default: 1e-10.
        seed: Random seed for the gridsynth algorithm. Default: 32.
    Returns:
        compiled_circuit: Compiled circuit in Clifford+T gates.
    Raises:
        Exception: If the set of gates in the Rz decomposition is not correct.
    """
    
    if not check_gridsynth():
        print('Rz and phase gates have not been compiled in Clifford+T gates')
        return circuit
    
    # Obtain the quantum and classical registers of the original circuit.
    quantum_registers = []
    for index in range(len(circuit.qubits)):
        r = circuit.find_bit(circuit.qubits[index]).registers[0][0]
        if r not in quantum_registers:
            quantum_registers.append(r)
    classical_registers = []
    for index in range(len(circuit.clbits)):
        r = circuit.find_bit(circuit.clbits[index]).registers[0][0]
        if r not in classical_registers:
            classical_registers.append(r)
    
    # Instantiate the compiled circuit.
    compiled_circuit = QuantumCircuit()
    for index in range(len(quantum_registers)):
        compiled_circuit.add_register(quantum_registers[index])
    for index in range(len(classical_registers)):
        compiled_circuit.add_register(classical_registers[index])
    
    # Compile the rotation gates and copy the others.
    data = circuit.data
    for d in data:
        name = d[0].name
        qubits = d[1]
        
        if name == 'p' or name == 'rz':
            theta = d[0].params[0]
            
            output = compile_rz_gate(theta,error_gate)
            
            # The gates are read in the reverse order.
            for gate in output[::-1]:
                if gate == 'S':
                    compiled_circuit.s(qubits)
                elif gate == 'T':
                    compiled_circuit.t(qubits)
                elif gate == 'H':
                    compiled_circuit.h(qubits)
                elif gate == 'X':
                    compiled_circuit.x(qubits)
                elif gate == 'Z':
                    compiled_circuit.z(qubits)
                elif gate == 'I':
                    pass
                else:
                    raise Exception(f'Wrong gate in the Rz decomposition: {gate}')
        
        else:
            compiled_circuit.data.append(d)
    
    return compiled_circuit
