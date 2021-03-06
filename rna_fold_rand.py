#!/usr/bin/env python


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
partfunc0=False

def process_sequence(seq):
	global partfunc0
	#https://www.tbi.univie.ac.at/RNA/ViennaRNA/doc/html/examples_python.html

	# create fold_compound data structure (required for all subsequently applied  algorithms)
	fc = RNA.fold_compound(seq)
	# compute MFE and MFE structure
	(ss, mfe) = fc.mfe()
	if partfunc0:
		# rescale Boltzmann factors for partition function computation
		fc.exp_params_rescale(mfe)
		# compute partition function
		(pp, pf) = fc.pf()
		return (pp, pf)
	else:
		return (ss, mfe)

	## compute centroid structure
	##(centroid_struct, dist) = fc.centroid()
	## compute free energy of centroid structure
	##centroid_en = fc.eval_structure(centroid_struct)
	## compute MEA structure
	##(MEA_struct, MEA) = fc.MEA()
	## compute free energy of MEA structure
	##MEA_en = fc.eval_structure(MEA_struct)
	## print everything like RNAfold -p --MEA
	##print("%s\n%s (%6.2f)" % (seq, mfe_struct, mfe))
	##print("%s [%6.2f]" % (pp, pf))
	##print("%s {%6.2f d=%.2f}" % (centroid_struct, centroid_en, dist))
	##print("%s {%6.2f MEA=%.2f}" % (MEA_struct, MEA_en, MEA))
	##print(" frequency of mfe structure in ensemble %g; ensemble diversity %-6.2f" % (fc.pr_structure(mfe_struct), fc.mean_bp_distance()))V
	

def analyze_seq(seq_id_seq_tuple):
	global N_randomizations
	global min_stdev
	(seq_id,seq)=seq_id_seq_tuple
	L=len(seq)
	energies=list()
	energies_better=0
	
	# compute minimum free energy (MFE) and corresponding structure
	(ss, energy) = process_sequence(seq)
	process_sequence(seq)
	for i in range(N_randomizations):
		# compute minimum free energy (MFE) and corresponding structure
		(structure_rand, energy_rand) = process_sequence("".join(random.sample(seq,L)))
		energies.append(energy_rand)
		if energy_rand < energy:
			energies_better+=1
	c=L-ss.count(".")
	sigma = std(energies, ddof=1)
	mu = mean(energies)
	if sigma==0.0:
		z = (energy-mu)/min_stdev
	else:
		z = (energy-mu)/sigma
		
	#	0	1	2	3	4	5		6	7	8	9	10					11		
	return [seq_id, seq, 	ss, 	L,	c,	float(c)/L, 	energy,	mu, 	sigma, 	z, 	float(energies_better)/N_randomizations,energies]
	
def print_out(out):
	out[11]=";".join((str(i) for i in out[11]))
	print("%s\t%s\t%s\t%i\t%i\t%f\t%f\t%f\t%f\t%f\t%f\t%s" % (out[0],out[1],out[2],out[3],out[4],out[5],out[6],out[7],out[8],out[9],out[10],out[11]))

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
