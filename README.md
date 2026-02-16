<div align="center">    
 
# CQC-QHE


[![arXiv](http://img.shields.io/badge/arXiv-2412.01966-B31B1B.svg)](https://arxiv.org/abs/2412.01966)
[![Journal](http://img.shields.io/badge/Journal_of_Physics:_Complexity-2025-4b44ce.svg)](https://iopscience.iop.org/article/10.1088/2632-072X/add3aa)

</div>
 
## Description   
Classical-Quantum Circuits for Quantum Homomorphic Encryption.

## Installation  
Open a system's console or an Anaconda Prompt depending on your python installation.

First, clone the repository.
```bash
git clone https://github.com/OrtegaSA/cqc-qhe-repo
```
This creates a folder called cqc-qhe-repo. Change the directory to it.
```bash
cd cqc-qhe-repo
```
Install the package using pip.
```bash
pip install .
```

Alternativelly, you can download the folder cqc_qhe and copy it in your python working directory, or in some directory included in PYTHONPATH.

## Optional

For automatic compilation of rotation gates and controlled-rotation gates, you need to install the binary gridsynth.

*Neil J. Ross and Peter Selinger. Optimal ancilla-free Clifford+T approximation of z-rotations. Quantum Information and Computation 16(11-12):901-953, 2016.*

The binary is licensed under GPL-3.0 and is not part of this software.

To install it, open a python console and run:
```python-repl
import cqc_qhe as cqc
cqc.install_gridsynth()
```

Alternatively, you can download the binary corresponding to your operating system from [here](https://www.mathstat.dal.ca/~selinger/newsynth/), and copy it into `your_user_name/.cqc_qhe/bin`.

To uninstall it:
```python-repl
import cqc_qhe as cqc
cqc.uninstall_gridsynth()
```

## Important

This package requires qiskit >= 1.0 and < 2.0, and qiskit-aer.

## Tutorials
There are example tutorials implementing the quantum and semiclassical walks of our paper. Moreover, there is also a jupyter notebook explaining how the different functions of our library work.

### Citation
<!---
```
@article{ortega2024cqc-qhe,
  title={Implementing Semiclassical Szegedy Walks in Classical-Quantum Circuits for Homomorphic Encryption},
  author={Ortega, S. A. and Fernández, P. and Martin-Delgado, M. A.},
  journal={arXiv:2412.01966},
  year={2024},
}
```
-->
```
@article{ortega2024cqc-qhe,
        title={Implementing Semiclassical Szegedy Walks in Classical-Quantum Circuits for Homomorphic Encryption},
        author={Ortega, S. A. and Fernández, P. and Martin-Delgado, M. A.},
        journal={Journal of Physics: Complexity},
        volume={6},
        pages={025010},
        year={2025},
}
```

