### Quick Start: Running the Project

## Requirements

Before running the application, ensure that you have:

* Python 3 installed.
* Git installed (if cloning the repository).
* A Linux/macOS terminal or compatible shell.
* An internet connection for installing dependencies.
* Option 1: Automated Setup (Recommended)

Clone the repository:
```git clone https://github.com/CocoCat0/ML_Homomorphic_Encryption.git```

Navigate into the project directory:
```cd ML_Homomorphic_encryption```

Make the execution script executable:
```chmod +x run.sh```

Run the application:
```./run.sh```

The script automatically:
* Creates a Python virtual environment.
* Activates the environment.
* Installs the required dependencies.
* Executes the main application.
* Generates the performance evaluation results.

## Option 2: Manual Setup
Create a virtual environment:
```python3 -m venv .venv```

Activate it:
```source .venv/bin/activate```

Install dependencies:
```pip install -r requirements.txt```

Execute the application:
```python main.py```

Expected Output: 
After successful execution, the application displays:

* Encryption performance measurements.
* Encrypted inference measurements.
* Decryption performance measurements.
* Numerical accuracy comparisons.
* Key rotation statistics.
* CKKS configuration comparisons.

The final results are saved to:

'results/ckks_performance_results.csv'

This file contains the performance measurements for both CKKS configurations.
