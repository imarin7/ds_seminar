#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import random
import numpy as np

customers = input("Customers: ")  #ovdje unosimo koliko zelimo musterija

demand = np.zeros((int(customers), 2), dtype=np.int32)
distance = np.zeros((int(customers)+1, int(customers)+1), dtype = np.int32)

for i in range(0, int(customers)):
    demand[i][0] = i+1
    demand[i][1] = random.randint(0,50)   #limit potražnje svakog kupca na max 50 komada robe

	
	#matrica potražnji ima dimenzije: (broj kupaca+1) * (broj kupaca+1) ==> kvadratna matrica 
for i in range(0, int(customers)+1):
    for j in range(0, int(customers)+1):
        if i==j:
            distance[i][j]=0
        if i<j:
            distance[i][j]=random.randint(0, 50)   #limit udaljenosti izmedju točaka na 50; rand generirane u kvadratnu matricu
        if j<i:
            distance[i][j] = distance[j][i]

	#matrice se zapisuju u navedene datoteke
np.savetxt("distance.txt", distance, fmt='%i')
np.savetxt("demand.txt", demand, fmt='%i')
