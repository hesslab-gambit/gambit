# GAMBIT

[![Build Status](https://github.com/hesslab-gambit/gambit/actions/workflows/ci.yml/badge.svg)](https://github.com/hesslab-gambit/gambit/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/hesslab-gambit/badge/?version=latest)](https://hesslab-gambit.readthedocs.io/en/latest/?badge=latest)
[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/hesslab-gambit/README.html)

GAMBIT (Genomic Approximation Method for Bacterial Identification and Tracking) is a tool for rapid taxonomic identification of microbial pathogens.
It uses an extremely efficient genomic distance metric along with a curated database of approximately 50,000 reference genomes (derived from NCBI
[RefSeq](https://www.ncbi.nlm.nih.gov/refseq/)) to identify unknown bacterial genomes within seconds.

Developed by Jared Lumpe in collaboration with the David Hess lab at Santa Clara University.
Preprint available [here](https://www.biorxiv.org/content/10.1101/2022.06.14.496173v1).

See the [documentation](https://hesslab-gambit.readthedocs.io/en/stable) for more
detailed information on the tool and how to use it.


## Installation

Install the Python library from Bioconda:

```
conda install -c bioconda hesslab-gambit
```

Then download the reference database files and place them in a directory of your choice:

* [gambit-genomes-1.0b1-210719.db](https://storage.googleapis.com/hesslab-gambit-public/databases/refseq-curated/1.0-beta/gambit-genomes-1.0b1-210719.db)
* [gambit-signatures-1.0b1-210719.h5](https://storage.googleapis.com/hesslab-gambit-public/databases/refseq-curated/1.0-beta/gambit-signatures-1.0b1-210719.h5)

(Note - these are marked as "beta" but little is likely to change in the upcoming 1.0 release).


## Usage

    gambit [-d /path/to/database/] query [-o results.csv] genome1.fasta genome2.fasta ...

`GENOMES` are one or more FASTA files containing query genome assemblies. You must provide the path
to the directory containing the database files using either the `-d` option (*before* the `query`
subcommand) or by setting`GAMBIT_DB_PATH` environment variable.

See the documentation for additional details on the command line interface and description of the output.


## Contact

For questions regarding usage of the software itself, please contact Jared Lumpe at [mjlumpe@gmail.com](mailto:mjlumpe@gmail.com).
All other questions should be directed to David Hess at [dchess@scu.edu](mailto:dchess@scu.edu).
