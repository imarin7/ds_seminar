#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from genetics import Genetics
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
pop = 10			#max veličina populacije
depot = 0			#inicijalno stanje skladišta
capacity = 100		#max kapacitet kamiona u jednoj ruti
v_num = 5			#broj raspoloživih vozila
gen_num = 200		#broj generacija

file = open("distance.txt")
distance = np.loadtxt(file)	#učitava matricu udaljenosti iz gorenavedene datoteke
file.close()
file = open("demand.txt")	
demand = np.loadtxt(file)	#učitava matricu potražnji količina robe iz gorenavedene datoteke
file.close()

c_num = demand.shape[0]

#inicijalizacija populacije, svi argumenti bitni za izvođenje se mijenjaju ovdje
population = Genetics(v_num, capacity, depot, pop, distance, demand, gen_num)
solution, cost = population.run()  # izvršava glavni program, te nakon izvršavanja vraća rješenje i trošak
costs = np.zeros(size, dtype = np.int32)  #inicijalizacija numpy polja u koja ćemo gatherat rezultate
solutions = np.zeros((size, v_num, c_num), dtype = np.int32)
comm.Gather([cost, MPI.INT], [costs, MPI.INT], root=0)  #svaki pokrenuti proces = jedna populacija, kad je izračun gotov svaki proces vraća rezultat u glavni proces (root=0)
comm.Gather([solution, MPI.INT], [solutions, MPI.INT], root=0)

index = costs.argmin();

# ispisuje najbolje rješenje (ruta i ukupna vrijednost troška/fitness)
if rank==0:
    print("Final solution: ")
    print(solutions[index])
    print("Cost: %d" %(costs[index]))
