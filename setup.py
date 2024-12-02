from setuptools import setup, find_packages

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(name='cqc-qhe',
      version='1.0',
      description='Classical-Quantum Circuits for Quantum Homomorphic Encryption',
      author='Sergio A. Ortega, Pablo Fernandez and Miguel A. Martin-Delgado',
      author_email='sortega5892@gmail.com',
      url='https://github.com/OrtegaSA/cqc-qhe-repo',
      license='Apache 2.0',
      # classifiers=[
      #   "Environment :: Console",
      #   "License :: OSI Approved :: Apache Software License",
      #   "Intended Audience :: Developers",
      #   "Intended Audience :: Science/Research",
      #   "Operating System :: Microsoft :: Windows",
      #   "Operating System :: MacOS",
      #   "Operating System :: POSIX :: Linux",
      #   "Programming Language :: Python :: 3 :: Only",
      #   "Topic :: Scientific/Engineering",
      # ],
      install_requires=REQUIREMENTS,
      python_requires=">=3.0",
      include_package_data=True,
      packages=find_packages(),
     )
