#!/usr/bin/env python
from __future__ import with_statement

from sys import stdin, stderr
from optparse import OptionParser
from multiprocessing.dummy import Pool as ThreadPool
import random
import RNA
from numpy import std,mean
#from random import shuffle
#from subprocess import Popen, PIPE
#from collections import defaultdict
#from vfork.io.colreader import Reader

N_randomizations=None
min_stdev=None

def analyze_seq(seq_id_seq_tuple):
	global N_randomizations
	global min_stdev
	(seq_id,seq)=seq_id_seq_tuple
	L=len(seq)
	MFEs=list()
	MFEs_better=0
	
	# compute minimum free energy (MFE) and corresponding structure
	#(ss, mfe) = RNA.fold(random.sample(seq,L))
	(ss, mfe) = RNA.fold(seq)
	for i in range(N_randomizations):
		# compute minimum free energy (MFE) and corresponding structure
		(ss_rand, mfe_rand) = RNA.fold("".join(random.sample(seq,L)))
		MFEs.append(mfe_rand)
		if mfe_rand < mfe:
			MFEs_better+=1
	c=L-ss.count(".")
	sigma = std(MFEs, ddof=1)
	mu = mean(MFEs)
	if sigma==0.0:
		z = (mfe-mu)/min_stdev
	else:
		z = (mfe-mu)/sigma
		
	#	0	1	2	3	4	5		6	7	8	9	10					11		
	return [seq_id, seq, 	ss, 	L,	c,	float(c)/L, 	mfe, 	mu, 	sigma, 	z, 	float(MFEs_better)/N_randomizations, 	MFEs]
	
def print_out(out):
	out[11]=";".join((str(i) for i in out[11]))
	print "%s\t%s\t%s\t%i\t%i\t%f\t%f\t%f\t%f\t%f\t%f\t%s" % (out[0],out[1],out[2],out[3],out[4],out[5],out[6],out[7],out[8],out[9],out[10],out[11])

def input_iterator():
	for line in stdin:
		tokens = line.rstrip().split('\t')
		assert len(tokens) == 2
		yield(tuple(tokens))

def calculateParallel(function, iterable_input, threads=2):
    pool = ThreadPool(threads)
    results = pool.map(function, iterable_input)
    pool.close()
    pool.join()
    return results

def main():
	global N_randomizations
	global min_stdev
	global partfunc0
	usage = '''%prog N < STDIN.fasta.oneline
	The nucleotides of each seqeunce in input is suffeld N times
	The free energy of randomizzation is caclulated whit Vienna RNA fold.
	Then is compared to the free energy of the true sequence.
	'''
	parser = OptionParser(usage=usage)

	parser.add_option('-@', '--num_threads', type=int,   dest='num_threads', default=5, 	 help='number of threads to use [default: %default]', metavar='N')
	parser.add_option('-s', '--min_stdev',   type=float, dest='min_stdev',	 default=0.0001, help='if the stdev is 0.0, use S to compute z score [default: %default]', metavar='S')
	#parser.add_option('-p', '--dump-params', dest='params_file', help='some help FILE [default: %default]', metavar='FILE')
	parser.add_option('-p', '--partfunc0', dest='partfunc0', action='store_true', default=False, help='same as RNAfold -p0 [default: %default]')

	options, args = parser.parse_args()
	
	if len(args) != 1:
		exit('Unexpected argument number.')
	
	N_randomizations=int(args[0])
	min_stdev=options.min_stdev
	partfunc0=options.partfunc0

	seq_in=[]

	#input_=list(input_iterator())
	#for out in calculateParallel(analyze_seq, input_, options.num_threads):
	for out in map(analyze_seq, input_iterator()):
		print_out(out)

if __name__ == '__main__':
	main()
