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

Circuits for homormophic encryption simulation.
"""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from cqc_qhe.utils import count_gates

def classical_cnot(circuit,c_bit,t_bit,ancilla_reg):
    """Apply a classical cnot between two classical bits.
    Args:
        circuit: Quantum circuit.
        c_bit: Control bit.
        t_bit: Target bit.
        ancilla_reg: Quantum register used for the classical gates.
    """
    
    # circuit.reset(ancilla_reg)
    # circuit.x(ancilla_reg[0]).c_if(c_bit,1)
    # circuit.x(ancilla_reg[1]).c_if(t_bit,1)
    # circuit.cx(ancilla_reg[0],ancilla_reg[1])
    # circuit.measure([ancilla_reg[0],ancilla_reg[1]],[c_bit,t_bit])
    
    circuit.reset(ancilla_reg[0])
    circuit.x(ancilla_reg[0]).c_if(t_bit,1)
    circuit.x(ancilla_reg[0]).c_if(c_bit,1)
    circuit.measure([ancilla_reg[0]],[t_bit])

def classical_swap(circuit,bit_1,bit_2,ancilla_reg):
    """Apply a swap gate between two classical bits.
    Args:
        circuit: Quantum circuit.
        bit_1: Classical bit.
        bit_2: Classical bit.
        ancilla_reg: Quantum register used for the classical gates.
    """
    
    # circuit.reset(ancilla_reg)
    # circuit.x(ancilla_reg[0]).c_if(bit_1,1)
    # circuit.x(ancilla_reg[1]).c_if(bit_2,1)
    # circuit.swap(ancilla_reg[0],ancilla_reg[1])
    # circuit.measure([ancilla_reg[0],ancilla_reg[1]],[bit_1,bit_2])
    
    circuit.reset(ancilla_reg)
    circuit.x(ancilla_reg[0]).c_if(bit_1,1)
    circuit.x(ancilla_reg[1]).c_if(bit_2,1)
    circuit.measure([ancilla_reg[1],ancilla_reg[0]],[bit_1,bit_2])

def classical_reset(circuit,bit,ancilla_reg):
    """Apply a classical reset to a classical bit.
    Args:
        circuit: Quantum circuit.
        bit: Classical bit.
        ancilla_reg: Quantum register used for the classical gates.
    """
    
    circuit.reset(ancilla_reg[0])
    circuit.measure(ancilla_reg[0],bit)

def create_homomorphic_circuit(init_circuit,main_circuit,measured_qubits=None):
    """Create the homomorphic circuit.
    Args:
        init_circuit: Initial circuit by the client.
        main_circuit: Main circuit by the server. It must be compiled in Clifford+T gates.
        measured_qubits: Qubits that are measured to obtain the final result.
    Returns:
        homomorphic_circuit: Homomorphic circuit for the simulation.
    Raises:
        Exception: If the set of gates is not correct.
    """
    
    # Obtain the quantum registers of the main circuit.
    registers = []
    for index in range(len(main_circuit.qubits)):
        r = main_circuit.find_bit(main_circuit.qubits[index]).registers[0][0]
        if r not in registers:
            registers.append(r)

    # Instantiate the homomorphic circuit with the quantum registers.    
    homomorphic_circuit = QuantumCircuit()
    for index in range(len(registers)):
        homomorphic_circuit.add_register(registers[index])
    
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
    number_t_gates = count_gates(main_circuit,['t','tdg'])
    bell_reg_list = [QuantumRegister(2,f'bell {_}') for _ in range(number_t_gates)]
    for index in range(number_t_gates):
        homomorphic_circuit.add_register(bell_reg_list[index])
    
    # Create classical registers for the Bell measurements.
    ra_reg = ClassicalRegister(number_t_gates,'ra')
    rb_reg = ClassicalRegister(number_t_gates,'rb')
    homomorphic_circuit.add_register(ra_reg)
    homomorphic_circuit.add_register(rb_reg)
    
    # Obtain the classical register of the original circuit (for semiclassical algorithms).
    classical_registers = []
    for index in range(len(main_circuit.clbits)):
        r = main_circuit.find_bit(main_circuit.clbits[index]).registers[0][0]
        if r not in classical_registers:
            classical_registers.append(r)
    
    for index in range(len(classical_registers)):
        homomorphic_circuit.add_register(classical_registers[index])
    
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
            raise Exception(f'Wrong gate in the circuit: {name}')
    
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
            raise Exception(f'Wrong gate in the circuit: {name}')
    
    return homomorphic_circuit

def create_simplified_homomorphic_circuit(init_circuit,main_circuit,measured_qubits=None):
    """Create the simplified homomorphic circuit.
    Args:
        init_circuit: Initial circuit by the client.
        main_circuit: Main circuit by the server. It must be compiled in Clifford+T gates.
        measured_qubits: Qubits that are measured to obtain the final result.
    Returns:
        homomorphic_circuit: Simplified homomorphic circuit for the simulation.
    Raises:
        Exception: If the set of gates is not correct.
    """
    
    # Obtain the quantum registers of the main circuit.
    registers = []
    for index in range(len(main_circuit.qubits)):
        r = main_circuit.find_bit(main_circuit.qubits[index]).registers[0][0]
        if r not in registers:
            registers.append(r)
    
    # Instantiate the homomorphic circuit with the quantum registers.
    homomorphic_circuit = QuantumCircuit()
    for index in range(len(registers)):
        homomorphic_circuit.add_register(registers[index])
        
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
    number_t_gates = count_gates(main_circuit,['t','tdg'])
    ra_reg = ClassicalRegister(number_t_gates,'ra')
    rb_reg = ClassicalRegister(number_t_gates,'rb')
    homomorphic_circuit.add_register(ra_reg)
    homomorphic_circuit.add_register(rb_reg)
    
    # Create a quantum register for the classical gates.
    # We use the same than the Bell pairs registers.
    cl_gates_reg = bell_reg
    
    # Obtain the classical register of the original circuit (for semiclassical algorithms).
    classical_registers = []
    for index in range(len(main_circuit.clbits)):
        r = main_circuit.find_bit(main_circuit.clbits[index]).registers[0][0]
        if r not in classical_registers:
            classical_registers.append(r)
    for index in range(len(classical_registers)):
        homomorphic_circuit.add_register(classical_registers[index])
    
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
            raise Exception(f'Wrong gate in the circuit: {name}')
    
    # Measure the qubits of the original circuit.
    if measured_qubits is not None:
        measured_reg = ClassicalRegister(len(measured_qubits),'circ')
        homomorphic_circuit.add_register(measured_reg)
        homomorphic_circuit.barrier()
        homomorphic_circuit.measure(measured_qubits,measured_reg)
    
    return homomorphic_circuit