# Quantum Factoring with Shor's Algorithm

This project implements Shor's algorithm to factor the number 77 using IBM Quantum's cloud service.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- IBM Quantum account

## Installation

1. Create and activate a virtual environment (recommended):
```bash
python -m venv skibbidi
source skibbidi/bin/activate  
```

2. Install required packages:
```bash
pip install qiskit[all]~=1.3.1
pip install qiskit-ibm-runtime~=0.34.0
```

## IBM Quantum Setup

1. Create an IBM Quantum account at https://quantum.ibm.com/
2. Log in and get your API token from your account settings
3. Replace `YOUR_API_TOKEN` in the code with your actual token

## Running the Program

1. Run the program:
```bash
python diddy.py
```

The program will:
- Connect to IBM Quantum
- Submit the quantum circuit to the ibm_brisbane backend
- Monitor job execution
- Display results when complete

## Example Output

A successful run will show:
```
Running on ibm_brisbane
Job ID: [job_id]
Current status: QUEUED
...
Current status: RUNNING
...
Job completed, processing results...

Processed 5000 shots
Top 10 most frequent measurements:
[measurement details]

All factors found: [7, 11]
```

## Understanding the Results

The program attempts to factor N=77 using Shor's algorithm. A successful run will find the factors 7 and 11. The output shows:
- Quantum measurements and their frequencies
- Period calculations for each measurement
- Factors found from the period calculations
- Overall statistics about the quantum measurements

## Troubleshooting

- If the job times out, you can retrieve results later using the job ID
- Check the IBM Quantum dashboard to monitor job status
- Ensure your API token is valid and has not expired

## Notes

- Quantum computing time is limited for free accounts
- Jobs may queue depending on backend availability
- Results are probabilistic due to the quantum nature of the algorithm