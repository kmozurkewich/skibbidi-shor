from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import numpy as np
from math import gcd
from fractions import Fraction
from collections import Counter
import time

# IBM Quantum API Token
IBM_QUANTUM_TOKEN = "YOUR_API_TOKEN"

def c_amod15(a, power, qc, n, control, target):
    """Controlled multiplication by a mod 15"""
    if a not in [2,7,8,11,13]:
        raise ValueError("'a' must be 2,7,8,11 or 13")
    
    if a in [2,13]:
        qc.cswap(control, target[1], target[2])
        qc.cswap(control, target[0], target[1])
    if a in [7,8]:
        qc.cswap(control, target[0], target[1])
        qc.cswap(control, target[1], target[2])
    if a == 11:
        qc.cswap(control, target[0], target[1])
        qc.cswap(control, target[1], target[2])
        qc.cx(control, target[0])
        qc.cx(control, target[1])
        qc.cx(control, target[2])

def qft_dagger(qc, q, n):
    """n-qubit QFT dagger"""
    for qubit in range(n//2):
        qc.swap(q[qubit], q[n-qubit-1])
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), q[m], q[j])
        qc.h(q[j])

def create_shor_circuit(N=77, a=2):
    """Create muh quantum circuit for Shor's algorithm to factor N, becuase those photonic bonds need to be diversified, yo."""
    n_count = 8  # number of counting qubits
    n_target = 4  # size of target register
    
    q_count = QuantumRegister(n_count, 'count')
    q_target = QuantumRegister(n_target, 'target')
    c_count = ClassicalRegister(n_count, 'c')
    
    qc = QuantumCircuit(q_count, q_target, c_count)
    
    # Initialize counting qubits in superposition
    for q in range(n_count):
        qc.h(q_count[q])
    
    # Initialize target register to |1>
    qc.x(q_target[0])
    
    # Apply controlled multiplication operations
    for i in range(n_count):
        c_amod15(a, 2**i, qc, N, q_count[i], q_target)
    
    # Apply inverse QFT to counting register
    qft_dagger(qc, q_count, n_count)
    
    # Measure counting register
    qc.measure(q_count, c_count)
    
    return qc

def process_bitarray(bit_array):
    """Process BitArray data into measurement counts"""
    counts = Counter()
    array_data = bit_array.array
    
    # Data comes as a (n,1) shaped numpy array of decimal values
    for measurement in array_data:
        # Extract the value and convert to Python int
        value = int(measurement[0])
        counts[value] += 1
    
    return counts

def find_factors(N, measurement, n_count):
    """Find factors of N given the measurement result."""
    try:
        if measurement == 0:
            return None
        
        # Convert to Python int to avoid numpy type issues
        measurement = int(measurement)
        N = int(N)
        n_count = int(n_count)
        
        # Calculate x/2^n
        x = Fraction(measurement, 2**n_count)
        
        # Find closest fraction with denominator <= N
        frac = Fraction(x).limit_denominator(N)
        r = int(frac.denominator)  # Ensure Python int
        
        if r % 2 == 0:
            # Use modular exponentiation instead of direct power
            a = 2  # We're using a=2 in our implementation
            half_r = r // 2
            
            # Calculate modular exponentiations safely
            base = pow(a, half_r, N)  # Built-in modular exponentiation
            guess1 = gcd(base - 1, N)
            guess2 = gcd(base + 1, N)
            
            factors = [g for g in [guess1, guess2] if g not in [1, N]]
            return factors if factors else None
            
        return None
    except Exception as e:
        print(f"Error in factor calculation: {e}")
        return None

def analyze_and_print_results(counts, N=77):
    """Analyze and print the measurement results"""
    total_shots = sum(counts.values())
    print(f"\nProcessed {total_shots} shots")
    print("\nTop 10 most frequent measurements:")
    
    all_factors = set()
    
    for measurement, count in counts.most_common(10):
        probability = count / total_shots
        binary = format(measurement, '08b')
        
        print(f"\nMeasurement: {measurement:3d} (binary: {binary})")
        print(f"Count: {count:4d} of {total_shots} shots (probability: {probability:.3f})")
        
        # Try to find factors
        factors = find_factors(N, measurement, 8)
        if factors:
            all_factors.update(factors)
            print(f"Found factors: {factors}")
    
    # Print summary statistics
    print("\nMeasurement Statistics:")
    print(f"Total unique measurements: {len(counts)}")
    print(f"Most common measurement: {counts.most_common(1)[0][0]} "
          f"(occurred {counts.most_common(1)[0][1]} times)")
    mean = sum(m * c for m, c in counts.items()) / total_shots
    print(f"Average measurement value: {mean:.2f}")
    
    if all_factors:
        print(f"\nAll factors found: {sorted(list(all_factors))}")
    else:
        print("\nNo factors found in this run")

def main():
    # Initialize the runtime service
    service = QiskitRuntimeService(
        channel="ibm_quantum", 
        token=IBM_QUANTUM_TOKEN
    )
    
    # Use IBM Brisbane becuase all the other free-tier regions hate me.  Incidently on Friday afternoons the queues really clear-out.
    backend = service.backend("ibm_brisbane")
    print(f"Running on {backend.name}")
    
    # Create and transpile the circuit
    qc = create_shor_circuit(N=77, a=2)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pm.run(qc)
    
    # Execute the circuit
    try:
        sampler = Sampler(mode=backend)
        job = sampler.run([isa_circuit], shots=5000)
        job_id = job.job_id()
        print(f"Job ID: {job_id}")
        print("Waiting for job completion...")
        
        # Monitor job status
        last_status = None
        while True:
            status = job.status()
            if status != last_status:
                print(f"Current status: {status}")
                last_status = status
            
            if status in ["DONE", "Completed"]:
                print("Job completed, processing results...")
                result = job.result()
                bit_array = result[0].data.c
                counts = process_bitarray(bit_array)
                analyze_and_print_results(counts)
                break
            elif status == "Failed":
                print("Job failed. Please check the IBM Quantum dashboard.")
                print(f"https://quantum.ibm.com/jobs/{job_id}")
                break
                
            time.sleep(5)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"You can check the job status at https://quantum.ibm.com/jobs/{job_id}")
        raise

if __name__ == "__main__":
    main()