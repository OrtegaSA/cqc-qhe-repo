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

"""Utils for homormophic encryption simulation.
"""

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

def toffoli_T(circuit,qubits):
    """Apply a toffoli gate with T gates.
    Args:
        circuit: Quantum circuit.
        qubits: Set of qubits where the toffoli gate is applied.
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

def compile_clifford_t_circuit(circuit):
    """Compile a quantum circuit in clifford+T gates.
    Args:
        circuit: Quantum circuit to compile.
    Returns:
        compiled_circuit: Compiled circuit in cliffor+T gates
    Raises:
        Exception: If the set of gates is not correct.
    """
    
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
    
    # Instantiate the compiled circuit
    compiled_circuit = QuantumCircuit()
    compiled_circuit.add_register(ancilla_reg)
    for index in range(len(quantum_registers)):
        compiled_circuit.add_register(quantum_registers[index])
    for index in range(len(classical_registers)):
        compiled_circuit.add_register(classical_registers[index])
    
    # Copy the clifford+T gates and compile the others.
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
        elif name == 'ccx':
            toffoli_T(compiled_circuit,(qubits[0],qubits[1],qubits[2]))
        
        elif (name == 'mcx' or name == 'mcx_gray'):
            number_anc = len(qubits)-1 -2
            toffoli_T(compiled_circuit,(qubits[0],qubits[1],ancilla_reg[0]))
            for a in range(1,number_anc):
                toffoli_T(compiled_circuit,(qubits[1+a],ancilla_reg[a-1],ancilla_reg[a]))
            toffoli_T(compiled_circuit,(qubits[-2],ancilla_reg[number_anc-1],qubits[-1]))
            for a in range(number_anc-1,1-1,-1):
                toffoli_T(compiled_circuit,(qubits[1+a],ancilla_reg[a-1],ancilla_reg[a]))
            toffoli_T(compiled_circuit,(qubits[0],qubits[1],ancilla_reg[0]))
        
        elif name == 'swap':
            compiled_circuit.cx(qubits[0],qubits[1])
            compiled_circuit.cx(qubits[1],qubits[0])
            compiled_circuit.cx(qubits[0],qubits[1])
        
        elif name == 'measure':
            compiled_circuit.measure(qubits,clbits)
        elif name == 'reset':
            compiled_circuit.reset(qubits)
        
        else:
            raise Exception('Wrong set of gates.')
    
    return compiled_circuit

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
    job = simulator.run(circuit, shots=shots)
    counts = job.result().get_counts(0)
    if reverse == False: return counts
    else: return reverse_counts(counts)

def count_T(circuit):
    """Count the number of T gates.
    Args:
        circuit: Quantum circuit.
    Returns:
        counter: Number of T gates.
    """
    
    data = circuit.data
    counter = 0
    for d in data:
        name = d[0].name
        if name == 't' or name == 'tdg':
            counter += 1
    
    return counter

def classical_swap(circuit,bit_1,bit_2,ancilla_reg):
    """Apply a swap gate between two classical bits.
    Args:
        circuit: Quantum circuit.
        bit_1: Classical bit.
        bit_2: Classical bit.
        ancilla_reg: Quantum register used for the classical gates.
    """
    
    circuit.reset(ancilla_reg)
    circuit.x(ancilla_reg[0]).c_if(bit_1,1)
    circuit.x(ancilla_reg[1]).c_if(bit_2,1)
    circuit.swap(ancilla_reg[0],ancilla_reg[1])
    circuit.measure([ancilla_reg[0],ancilla_reg[1]],[bit_1,bit_2])

def classical_cnot(circuit,c_bit,t_bit,ancilla_reg):
    """Apply a classical cnot between two classical bits.
    Args:
        circuit: Quantum circuit.
        c_bit: Control bit.
        t_bit: Target bit.
        ancilla_reg: Quantum register used for the classical gates.
    """
    
    circuit.reset(ancilla_reg)
    circuit.x(ancilla_reg[0]).c_if(c_bit,1)
    circuit.x(ancilla_reg[1]).c_if(t_bit,1)
    circuit.cx(ancilla_reg[0],ancilla_reg[1])
    circuit.measure([ancilla_reg[0],ancilla_reg[1]],[c_bit,t_bit])

def classical_reset(circuit,bit,ancilla_reg):
    """Apply a classical reset to a classical bit.
    Args:
        circuit: Quantum circuit.
        bit: Classical bit.
        ancilla_reg: Quantum register used for the classical gates.
    """
    
    circuit.reset(ancilla_reg)
    circuit.measure(ancilla_reg[0],bit)

def create_homomorphic_circuit(init_circuit,main_circuit,measured_qubits=None):
    """Create the homomorphic circuit.
    Args:
        init_circuit: Initial circuit by the client.
        main_circuit: Main circuit by the server. It must be compiled in clifford+T gates.
        measured_qubits: Qubits that are measured to obtain the final result.
    Returns:
        homomorphic_circuit: Homomorphic circuit for the simulation.
    Raises:
        Exception: If the set of gates is not correct.
    """
    
    # Obtain the quantum registers of the main circuit.
    registers = []
    for a in range(len(main_circuit.qubits)):
        r = main_circuit.find_bit(main_circuit.qubits[a]).registers[0][0]
        if r not in registers:
            registers.append(r)

    # Instantiate the homomorphic circuit with the quantum registers.    
    homomorphic_circuit = QuantumCircuit()
    for a in range(len(registers)):
        homomorphic_circuit.add_register(registers[a])
    
    # Obtain the qubits of the main circuit.
    main_qubits = main_circuit.qubits
    
    # Create classical registers for the keys.
    x_init_key_reg = ClassicalRegister(len(main_qubits),'x_init_key')
    z_init_key_reg = ClassicalRegister(len(main_qubits),'z_init_key')
    homomorphic_circuit.add_register(x_init_key_reg)
    homomorphic_circuit.add_register(z_init_key_reg)
    x_key_reg = ClassicalRegister(len(main_qubits),'x_key')
    z_key_reg = ClassicalRegister(len(main_qubits),'z_key')
    homomorphic_circuit.add_register(x_key_reg)
    homomorphic_circuit.add_register(z_key_reg)
    
    # Create quantum registers for the Bell pairs.
    number_t_gates = count_T(main_circuit)
    bell_reg_list = [QuantumRegister(2,f'bell {_}') for _ in range(number_t_gates)]
    for a in range(number_t_gates):
        homomorphic_circuit.add_register(bell_reg_list[a])
    
    # Create classical registers for the Bell measurements.
    ra_reg = ClassicalRegister(number_t_gates,'ra')
    rb_reg = ClassicalRegister(number_t_gates,'rb')
    homomorphic_circuit.add_register(ra_reg)
    homomorphic_circuit.add_register(rb_reg)
    
    # Obtain the classical register of the original circuit (for semiclassical walks).
    classical_registers = []
    for a in range(len(main_circuit.clbits)):
        r = main_circuit.find_bit(main_circuit.clbits[a]).registers[0][0]
        if r not in classical_registers:
            classical_registers.append(r)
    
    for a in range(len(classical_registers)):
        homomorphic_circuit.add_register(classical_registers[a])
    
    # Initialize the keys at random to the corresponding classical registers.
    homomorphic_circuit.h(main_qubits)
    homomorphic_circuit.measure(main_qubits,x_init_key_reg)
    homomorphic_circuit.measure(main_qubits,x_key_reg)
    homomorphic_circuit.reset(main_qubits)
    homomorphic_circuit.barrier()
    homomorphic_circuit.h(main_qubits)
    homomorphic_circuit.measure(main_qubits,z_init_key_reg)
    homomorphic_circuit.measure(main_qubits,z_key_reg)
    homomorphic_circuit.reset(main_qubits)
    homomorphic_circuit.barrier()
    
    # Copy the initial circuit by the client.
    for d in init_circuit.data:
        homomorphic_circuit.data.append(d)
    homomorphic_circuit.barrier()
    
    # Encrypt the circuit.
    for index, q in enumerate(main_qubits):
        homomorphic_circuit.x(q).c_if(x_init_key_reg[index],1)
        homomorphic_circuit.z(q).c_if(z_init_key_reg[index],1)
    homomorphic_circuit.barrier()
    
    # Copy the main circuit by the server with the homomorphic quantum rules for t gates.
    qubits_dict = {q:index for index, q in enumerate(main_qubits)}
    t_count = 0
    for d in main_circuit.data:
        name = d[0].name
        # Obtain the bits and qubits of the gate.
        gate_qubits = d[1]
        gate_clbits = d[2]
        
        if name == 'x':
            homomorphic_circuit.x(gate_qubits)
        
        elif name == 'z':
            homomorphic_circuit.z(gate_qubits)
        
        elif name == 'h':
            homomorphic_circuit.h(gate_qubits)
        
        elif name == 's':
            homomorphic_circuit.s(gate_qubits)
        
        elif name == 'sdg':
            homomorphic_circuit.sdg(gate_qubits)
        
        elif name == 'cx':
            homomorphic_circuit.cx(gate_qubits[0],gate_qubits[1])
        
        elif name == 't':
            bell_reg = bell_reg_list[t_count]
            homomorphic_circuit.barrier()
            homomorphic_circuit.t(gate_qubits)
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.swap(gate_qubits[0],bell_reg[0])
            
            t_count += 1
            homomorphic_circuit.barrier()
        
        elif name == 'tdg':
            bell_reg = bell_reg_list[t_count]
            homomorphic_circuit.barrier()
            homomorphic_circuit.tdg(gate_qubits)
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.swap(gate_qubits[0],bell_reg[0])
            
            t_count += 1
            homomorphic_circuit.barrier()
        
        elif name == 'barrier':
            homomorphic_circuit.barrier(gate_qubits)
        
        elif name == 'measure':
            homomorphic_circuit.measure(gate_qubits,gate_clbits)
        
        elif name == 'reset':
            homomorphic_circuit.reset(gate_qubits)
        
        else:
            raise Exception('Wrong set of gates.')
    
    # Measure the qubits of the original circuit.
    if measured_qubits is not None:
        measured_reg = ClassicalRegister(len(measured_qubits),'circ')
        homomorphic_circuit.add_register(measured_reg)
        homomorphic_circuit.barrier()
        homomorphic_circuit.measure(measured_qubits,measured_reg)
        
    # Apply the homomorphic classical update rules in the circuit returned to the client.
    
    # Create a quantum register for the classical gates.
    # We use the first two qubits of the main circuit.
    cl_gates_reg = main_qubits[0:2]
        
    t_count = 0
    for d in main_circuit.data:
        name = d[0].name
        # Obtain the bits and qubits of the gate.
        gate_qubits = d[1]
        gate_clbits = d[2]
        
        if name == 'x':
            pass
        
        elif name == 'z':
            pass
        
        elif name == 'h':
            classical_swap(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 's':
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 'sdg':
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 'cx':
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],x_key_reg[qubits_dict[gate_qubits[1]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,z_key_reg[qubits_dict[gate_qubits[1]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 't':
            bell_reg = bell_reg_list[t_count]
            homomorphic_circuit.barrier()
            homomorphic_circuit.s(bell_reg[0]).c_if(x_key_reg[qubits_dict[gate_qubits[0]]],1)
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.measure(bell_reg,[rb_reg[t_count],ra_reg[t_count]])
            
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,rb_reg[t_count],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,ra_reg[t_count],x_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            
            t_count += 1
            homomorphic_circuit.barrier()
        
        elif name == 'tdg':
            bell_reg = bell_reg_list[t_count]
            homomorphic_circuit.barrier()
            homomorphic_circuit.s(bell_reg[0]).c_if(x_key_reg[qubits_dict[gate_qubits[0]]],1)
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.measure(bell_reg,[rb_reg[t_count],ra_reg[t_count]])
            
            classical_cnot(homomorphic_circuit,rb_reg[t_count],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,ra_reg[t_count],x_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            
            t_count += 1
            homomorphic_circuit.barrier()
        
        elif name == 'barrier':
            homomorphic_circuit.barrier(gate_qubits)
        
        elif name == 'measure':
            classical_reset(homomorphic_circuit,z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 'reset':
            classical_reset(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_reset(homomorphic_circuit,z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        else:
            raise Exception('Wrong set of gates.')
    
    return homomorphic_circuit

def create_simplified_homomorphic_circuit(init_circuit,main_circuit,measured_qubits=None):
    """Create the simplified homomorphic circuit.
    Args:
        init_circuit: Initial circuit by the client.
        main_circuit: Main circuit by the server. It must be compiled in clifford+T gates.
        measured_qubits: Qubits that are measured to obtain the final result.
    Returns:
        homomorphic_circuit: Simplified homomorphic circuit for the simulation.
    Raises:
        Exception: If the set of gates is not correct.
    """
    
    # Obtain the quantum registers of the main circuit.
    registers = []
    for a in range(len(main_circuit.qubits)):
        r = main_circuit.find_bit(main_circuit.qubits[a]).registers[0][0]
        if r not in registers:
            registers.append(r)
    
    # Instantiate the homomorphic circuit with the quantum registers.
    homomorphic_circuit = QuantumCircuit()
    for a in range(len(registers)):
        homomorphic_circuit.add_register(registers[a])
        
    # Obtain the qubits of the main circuit.
    main_qubits = main_circuit.qubits
    
    # Create classical registers for the keys.
    x_init_key_reg = ClassicalRegister(len(main_qubits),'x_init_key')
    z_init_key_reg = ClassicalRegister(len(main_qubits),'z_init_key')
    homomorphic_circuit.add_register(x_init_key_reg)
    homomorphic_circuit.add_register(z_init_key_reg)
    x_key_reg = ClassicalRegister(len(main_qubits),'x_key')
    z_key_reg = ClassicalRegister(len(main_qubits),'z_key')
    homomorphic_circuit.add_register(x_key_reg)
    homomorphic_circuit.add_register(z_key_reg)
    
    # Create a quantum register for the Bell pairs.
    bell_reg = QuantumRegister(2,'bell')
    homomorphic_circuit.add_register(bell_reg)
    
    # Create classical registers for the Bell measurements.
    number_t_gates = count_T(main_circuit)
    ra_reg = ClassicalRegister(number_t_gates,'ra')
    rb_reg = ClassicalRegister(number_t_gates,'rb')
    homomorphic_circuit.add_register(ra_reg)
    homomorphic_circuit.add_register(rb_reg)
    
    # Create a quantum register for the classical gates.
    # We use the same than the Bell pairs registers.
    cl_gates_reg = bell_reg
    
    # Obtain the classical register of the original circuit (for semiclassical walks).
    classical_registers = []
    for a in range(len(main_circuit.clbits)):
        r = main_circuit.find_bit(main_circuit.clbits[a]).registers[0][0]
        if r not in classical_registers:
            classical_registers.append(r)
    for a in range(len(classical_registers)):
        homomorphic_circuit.add_register(classical_registers[a])
    
    # Initialize the keys at random to the corresponding classical registers.
    homomorphic_circuit.h(main_qubits)
    homomorphic_circuit.measure(main_qubits,x_init_key_reg)
    homomorphic_circuit.measure(main_qubits,x_key_reg)
    homomorphic_circuit.reset(main_qubits)
    homomorphic_circuit.barrier()
    homomorphic_circuit.h(main_qubits)
    homomorphic_circuit.measure(main_qubits,z_init_key_reg)
    homomorphic_circuit.measure(main_qubits,z_key_reg)
    homomorphic_circuit.reset(main_qubits)
    homomorphic_circuit.barrier()
    
    # Copy the initial circuit by the client.
    for d in init_circuit.data:
        homomorphic_circuit.data.append(d)
    homomorphic_circuit.barrier()
    
    # Encrypt the circuit.
    for index, q in enumerate(main_qubits):
        homomorphic_circuit.x(q).c_if(x_init_key_reg[index],1)
        homomorphic_circuit.z(q).c_if(z_init_key_reg[index],1)
    homomorphic_circuit.barrier()
    
    # Copy the main circuit by the server with the homomorphic updating rules.
    qubits_dict = {q:index for index, q in enumerate(main_qubits)}
    t_count = 0
    
    for d in main_circuit.data:
        name = d[0].name
        # Obtain the bits and qubits of the gate.
        gate_qubits = d[1]
        gate_clbits = d[2]
        
        if name == 'x':
            homomorphic_circuit.x(gate_qubits)
        
        elif name == 'z':
            homomorphic_circuit.z(gate_qubits)
        
        elif name == 'h':
            homomorphic_circuit.h(gate_qubits)
            classical_swap(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 's':
            homomorphic_circuit.s(gate_qubits)
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 'sdg':
            homomorphic_circuit.sdg(gate_qubits)
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 'cx':
            homomorphic_circuit.cx(gate_qubits[0],gate_qubits[1])
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],x_key_reg[qubits_dict[gate_qubits[1]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,z_key_reg[qubits_dict[gate_qubits[1]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 't':
            homomorphic_circuit.barrier()
            homomorphic_circuit.t(gate_qubits)
            homomorphic_circuit.reset(bell_reg)
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.swap(gate_qubits[0],bell_reg[0])
            homomorphic_circuit.s(bell_reg[0]).c_if(x_key_reg[qubits_dict[gate_qubits[0]]],1)
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.measure(bell_reg,[rb_reg[t_count],ra_reg[t_count]])
            
            classical_cnot(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,rb_reg[t_count],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,ra_reg[t_count],x_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            
            t_count += 1
            homomorphic_circuit.barrier()
        
        elif name == 'tdg':
            homomorphic_circuit.barrier()
            homomorphic_circuit.tdg(gate_qubits)
            homomorphic_circuit.reset(bell_reg)
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.swap(gate_qubits[0],bell_reg[0])
            homomorphic_circuit.s(bell_reg[0]).c_if(x_key_reg[qubits_dict[gate_qubits[0]]],1)
            homomorphic_circuit.cx(bell_reg[0],bell_reg[1])
            homomorphic_circuit.h(bell_reg[0])
            homomorphic_circuit.measure(bell_reg,[rb_reg[t_count],ra_reg[t_count]])
            
            classical_cnot(homomorphic_circuit,rb_reg[t_count],z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_cnot(homomorphic_circuit,ra_reg[t_count],x_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            
            t_count += 1
            homomorphic_circuit.barrier()
        
        elif name == 'barrier':
            homomorphic_circuit.barrier(gate_qubits)
        
        elif name == 'measure':
            homomorphic_circuit.measure(gate_qubits,gate_clbits)
            classical_reset(homomorphic_circuit,z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
        
        elif name == 'reset':
            homomorphic_circuit.reset(gate_qubits)
            classical_reset(homomorphic_circuit,x_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            classical_reset(homomorphic_circuit,z_key_reg[qubits_dict[gate_qubits[0]]],cl_gates_reg)
            
        else:
            raise Exception('Wrong set of gates.')
    
    # Measure the qubits of the original circuit.
    if measured_qubits is not None:
        measured_reg = ClassicalRegister(len(measured_qubits),'circ')
        homomorphic_circuit.add_register(measured_reg)
        homomorphic_circuit.barrier()
        homomorphic_circuit.measure(measured_qubits,measured_reg)
    
    return homomorphic_circuit

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
        measured_positions: Position in the circuit of the quabits being measured.
    Returns:
        decrypted_counts: Decrypted counts.
    """
    
    decrypted_counts = {}
    for chain in counts:
        f_value = chain.split(' ')[-1]
        f_key = chain.split(' ')[2]
        f_value = [int(a) for a in f_value]
        f_key = [int(f_key[a]) for a in measured_positions]
        decrypted_chain = ''.join([str(f_key[a]^f_value[a]) for a in range(len(f_value))])
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



