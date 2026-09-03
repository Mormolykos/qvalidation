import sys
import os
repo_root = r"C:\Users\User\Desktop\benchpress_test"
sys.path.insert(0, repo_root)

from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from benchpress.utilities.backends import FlexibleBackend

qasm = os.path.join(repo_root, "benchpress", "qasm", "qasmbench-large", "bv_n140", "bv_n140.qasm")
circuit = QuantumCircuit.from_qasm_file(qasm)
backend = FlexibleBackend(circuit.num_qubits, "linear", control_flow=True)
gate = backend.two_q_gate_type          # expect 'cz'

pm = generate_preset_pass_manager(optimization_level=2, backend=backend, seed_transpiler=777)
val = pm.run(circuit).count_ops().get(gate, 0)
print(val)
