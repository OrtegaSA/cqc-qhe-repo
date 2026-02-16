# Copyright 2025 Sergio A. Ortega and Miguel A. Martin-Delgado.

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

Utils for gridsynth.
"""

import os
import sys
import urllib.request
import stat
import subprocess

binary_name = "gridsynth"
install_dir = os.path.join(os.path.expanduser("~"), ".cqc_qhe", "bin")
binary_path = os.path.join(install_dir, binary_name)
if sys.platform.startswith("win"): binary_path += '.exe'
gridsynth_path = os.path.join(install_dir, binary_name)

def install_gridsynth():
    """Downloads the appropriate 'gridsynth' binary for the current OS and installs it to ~/.cqc_qhe/bin.
    """
    
    if sys.platform.startswith("win"):
        url = "https://www.mathstat.dal.ca/~selinger/newsynth/downloads/win/gridsynth.exe"
    elif sys.platform == "darwin":
        url = "https://www.mathstat.dal.ca/~selinger/newsynth/downloads/mac/gridsynth"
    else:
        url = "https://www.mathstat.dal.ca/~selinger/newsynth/downloads/lin/gridsynth"

    if os.path.isfile(binary_path):
        print(f"gridsynth is already installed at: {binary_path}")
        
    else:
        print("This binary is licensed under GPL-3.0 and is not part of this software.")
        choice = input("Proceed with installation? [Y/n] (default: Y): ").strip().lower()
        
        if choice not in ("", "y"):
            print("Installation cancelled.")
        
        else:
            print(f"Downloading gridsynth from: {url}")
            try:
                os.makedirs(install_dir, exist_ok=True)
                urllib.request.urlretrieve(url, binary_path)
    
                # Make the binary executable on Unix-like systems (Linux and macOS)
                if not sys.platform.startswith("win"):
                    mode = os.stat(binary_path).st_mode
                    os.chmod(binary_path, mode | stat.S_IXUSR)
    
                print(f"gridsynth installed at: {binary_path}")
    
            except Exception as e:
                print(f"Failed to download or install gridsynth: {e}")


def uninstall_gridsynth():
    """Removes the installed 'gridsynth' binary from ~/.cqc_qhe/bin, if it exists.
    """
    
    if os.path.isfile(binary_path):
        try:
            os.remove(binary_path)
            print(f"Removed gridsynth from: {binary_path}")
        except Exception as e:
            print(f"Failed to remove gridsynth: {e}")
    else:
        print(f"gridsynth is not installed at: {binary_path}")


def check_gridsynth():
    """Checks whether the 'gridsynth' binary is installed.
    Returns:
        True if it exists, otherwise False.
    """
    
    if os.path.isfile(binary_path):
        return True
    else:
        print(f"gridsynth is not installed at: {binary_path}")
        print("To install it, run:")
        print("    import cqc_qhe as cqc")
        print("    cqc.install_gridsynth()")
        return False

def gridsynth(theta,error=None,seed=None):
    """Run the 'gridsynth' binary.
    Args:
        theta: Angle of the rotation gate.
        error: Error of the decomposition. Default: 1e-10.
        seed: Random seed for the gridsynth algorithm. Default: random.
    Returns:
        output: String with the sequence of Clifford+T gates.
    """
    
    if error is not None:
        if seed is not None:
            comando = [gridsynth_path,f"({theta})","-p","-e",str(error),"-r",str(seed)]
        else:
            comando = [gridsynth_path,f"({theta})","-p","-e",str(error)]
    else:
        if seed is not None:
            comando = [gridsynth_path,f"({theta})","-p","-r",str(seed)]
        else:
            comando = [gridsynth_path,f"({theta})","-p"]
    
    if sys.platform.startswith("win"):
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    else:
        resultado = subprocess.run(comando,capture_output=True,text=True,check=True)
    
    output = resultado.stdout.strip()
    
    return output