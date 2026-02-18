# Linnea Inspector

Linear algebra expressions are the building blocks of countless computational problems. Such expressions can often be computed in many different ways, each corresponding to a specific sequence of kernel calls provided by highly optimized libraries such as BLAS and LAPACK. Although these sequences (also referred to as algorithmic variants) are mathematically equivalent, they can differ significantly in performance.

Linnea Inspector is a tool for identifying patterns of kernel operations that lead to suboptimal algorithmic performance.

For a given linear algebra expression, Linnea inspector generates multiple algorithmic variants for different problem sizes using [Linnea](https://github.com/HPAC/linnea.git). The kernel sequences of these variants are traced, and their execution times are measured. The resulting traces are then used to construct process models that identify and predict kernel operation patterns associated with suboptimal performance.

## Setup

### Requirements

- Python (recommended: Python 3.9+)
- Graphviz  
- Julia (Only required for building new models)

The remaining requirements are taken care of in the installation step.  

### Installation

```bash
git clone https://github.com/process-inspector/linnea_inspector.git
cd linnea_inspector
pip install .
```

### Verify

```bash
linnea-inspector -h
```

Output:
```
usage: linnea-inspector <command>

Linnea Inspector CLI

options:
  -h, --help            show this help message and exit

commands:
  {generator,runner,register,process,clean,sbatch,widget,store}
    generator           Generate algorithms using Linnea.
    runner              Generate run scripts for the generated algs.
    register            Register a run by linnea inspector.
    process             Process the trace files from the experiment runs and store the results in the linnea store.
    clean               Clean up data from failed runs.
    sbatch              Wrapper around sbatch that accepts arguments from a parameter file
    widget              Launch the Linnea Inspector web application.
    store               Lauch the Linnea Inspector store web application.
```




