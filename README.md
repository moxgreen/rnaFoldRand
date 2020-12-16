# rnaFoldRand
Analyze RNA folding with randomization

## Installation
Clone the repository and create the appropriate conda environment using the provided `conda_env_from_history.yml` file:

```
git clone git@github.com:moxgreen/rnaFoldRand.git rnaFoldRand;
cd rnaFoldRand;
conda env create -f conda_env_from_history.yml;
```

Activate the newely created environment:

```
conda activate rnaFoldRand_v0.1
```

## Usage

```
Usage: rna_fold_rand.py N < STDIN.fasta.oneline
	The nucleotides of each seqeunce in input is suffeld N times
	The free energy of randomizzation is caclulated whit Vienna RNA fold.
	Then is compared to the free energy of the true sequence.
	

Options:
  -h, --help            show this help message and exit
  -@ N, --num_threads=N
                        number of threads to use [default: 5]
  -s S, --min_stdev=S   if the stdev is 0.0, use S to compute z score
                        [default: 0.0001]
  -p, --partfunc0       same as RNAfold -p0 [default: False]
```
