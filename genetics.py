#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import numpy as np
import random

class Genetics:
    V_NUM = None
    V_CAP = None
    C_NUM = -1
    DEPOT = 0
    POP = 10
    DISTANCE = None
    DEMAND = None
    POPULATION = None
    FITNESS = None
	GEN_NUM = None
   
    
    def __init__(self, vehicle, capacity, depot, pop, distance, demand, gen):
        self.V_NUM = vehicle
        self.V_CAP = capacity
        self.DEPOT = depot
        self.POP = pop
        self.DISTANCE = distance.copy()
        self.DEMAND = demand.copy()
		self.GEN_NUM = gen

        self.C_NUM = self.DEMAND.shape[0]
        self.POPULATION = np.zeros((self.POP, self.V_NUM, self.C_NUM), dtype=np.int32)
        self.FITNESS = np.zeros(self.POP, dtype=np.int32)

		#izračunava fitness svih kromosoma
    def calc_fitness(self, chrom):
        cost = 0
        for r in chrom:
            if r[0] == -1:
                continue
            else:
                cost = cost + self.DISTANCE[r[0]][self.DEPOT]
            for i in range(len(r)):
                if r[i] != -1:
                    if i == len(r)-1:
                        cost = cost + self.DISTANCE[r[i]][self.DEPOT]
                    else:
                        if r[i+1] != -1:
                            cost = cost + self.DISTANCE[r[i]][r[i+1]]
                        else:
                            cost = cost + self.DISTANCE[r[i]][self.DEPOT]
                else:
                    break
        return cost
		
#vraća najbolji kromosom kako bi ga sačuvali za sljedeću generaciju
    def find_elite(self):
        for i in range(self.POP):
            if self.FITNESS.min()==self.FITNESS[i]:
                return i
# vraća najmanji kromosomi vrijednost fitnessa (trošak) 
    def get_best(self):
        return self.POPULATION[self.FITNESS.argmin()], self.FITNESS.min()

#redanje fitnessa po rankingu - najbolji je najmanji
    def rank_population(self):
        temp = self.FITNESS.argsort()
        fitness_rank = np.zeros(len(self.FITNESS), dtype = np.int32)
        fitness_rank[temp] = np.arange(len(self.FITNESS), dtype = np.int32)
        fitness_chance = np.zeros(self.POP, dtype = np.float32)    

        step = 0
        for i in range(self.POP):
            fitness_chance[i] = ((2*(self.POP-fitness_rank[i]))/(self.POP*(self.POP+1))) + step
            step = fitness_chance[i]        

        return fitness_chance

#input: broj mušterije, output: gdje se mušterija nalazi u kromosomu
    def get_element(self, x, b):
        for i in range(self.V_NUM):
            for j in range(self.C_NUM):
                if b[i][j] > -1:
                    if x==0:
                        return i,j
                    x = x-1

#random generator koji stvara child od dva parenta
    def crossover(self, a, b):
        x = random.randint(0, self.C_NUM-1)
        y = random.randint(0, self.C_NUM-1)

        if x<y:
            start = self.get_element(x, self.POPULATION[b])
            stop = self.get_element(y, self.POPULATION[b])
        else:
            stop = self.get_element(x, self.POPULATION[b])
            start = self.get_element(y, self.POPULATION[b])

        child = self.POPULATION[a].copy()

        if x==y:
            sub = self.POPULATION[b][start[0]][start[1]]
            sroute = [sub]

        elif start[0] == stop[0]:
            sub = []
            sub.append(self.POPULATION[b][start[0]][start[1]:stop[1]])

            sroute = []
            for i in range(len(sub)):
                for j in range(len(sub[i])):
                    if sub[i][j] != -1:
                        sroute.append(sub[i][j])
        
        else:
            sub = []
            sub.append(self.POPULATION[b][start[0]][start[1]:].copy())
            for i in range(start[0]+1, stop[0]):
                sub.append(self.POPULATION[b][i].copy())
            sub.append(self.POPULATION[b][stop[0]][:stop[1]].copy())

            sroute = []
            for i in range(len(sub)):
                for j in range(len(sub[i])):
                    if sub[i][j] != -1:
                        sroute.append(sub[i][j])

        a = sroute[0]
        for r in sroute:
            done = False 
            for i in range(self.V_NUM):
                for j in range(self.C_NUM):
                    if child[i][j] == r:
                        child[i][j] = -1
                        done = True
                        break
                if done:
                    break
  
        for i in range(self.V_NUM):
            route = np.array([-1]*self.C_NUM, dtype=np.int32)
            pomak = 0
            for j in range(self.C_NUM):
                if child[i][j] == -1:
                    pomak = pomak + 1
                else:
                    route[j-pomak] = child[i][j]
            child[i] = route

        d = 99999999
        for i in range(self.V_NUM):
            for j in range(self.C_NUM):
                if child[i][j] != -1:
                    if self.DISTANCE[a][child[i][j]] < d:
                        d = self.DISTANCE[a][child[i][j]]
                        ij = [i, j]


        route = np.array([-1]*self.C_NUM, dtype=np.int32)
        pomak = 0
        for j in range(self.C_NUM):
            if child[ij[0]][j] == -1:
                pomak = pomak + 1
            else:
                route[j-pomak] = child[ij[0]][j]

        new_route = []
        done = False
        for j in range (self.C_NUM):
            if route[j] != child[ij[0]][ij[1]] and not done:
                new_route.append(route[j])
            elif done:
                if route[j] != -1:
                    new_route.append(route[j])
                elif len(new_route) < self.C_NUM:
                    new_route.append(-1)
            else:
                new_route.append(route[j])
                for i in sroute:
                    new_route.append(i)
                done = True

        child[ij[0]] = new_route
        return child

		#uzima dijete kao parametar, te vrši randomno odabranu mutaciju nad njim
    def mutate(self, child):
        a = random.randint(0,2)
        #Swap
        if a==0:
            x = 0
            y = 0
            while(x == y):
                x = random.randint(0, self.C_NUM-1)
                y = random.randint(0, self.C_NUM-1)

            c1 = self.get_element(x, child)
            c2 = self.get_element(y, child)

            r1 = child[c1[0]][c1[1]]
            r2 = child[c2[0]][c2[1]]

            child[c1[0]][c1[1]] = r2
            child[c2[0]][c2[1]] = r1

#Invert
        if a==1:
            x = 0
            x = random.randint(0, self.V_NUM-1)
            new_route = []
            for j in range(len(child[x])-1, -1, -1):
                if child[x][j] != -1:
                    new_route.append(child[x][j])
            while len(new_route) < self.C_NUM:
                new_route.append(-1)

            child[x] = new_route
#Insert
        if a==2:
            x = random.randint(0, self.C_NUM-1)      
            c1 = self.get_element(x, child)        
            r1 = child[c1[0]][c1[1]]        

            child[c1[0]][c1[1]] = -1         
              
            new_route = np.array([-1]*self.C_NUM, dtype = np.int32)        
            pomak = 0        
            for i in range (len(child[c1[0]])):             
                if child[c1[0]][i] == -1:                
                    pomak = pomak + 1                
                else:                
                    new_route[i-pomak] = child[c1[0]][i]                

            child[c1[0]] = new_route   
            y1 = c1[0]        
            while y1 == c1[0]:            
                y1 = random.randint(0, self.V_NUM-1)            
            y2 = random.randint(0, self.C_NUM-1)        
 
            new_route = []        
            pomak = 0
            for j in range (self.C_NUM):
         
                if len(new_route) < self.C_NUM:                
                    if j == y2:                    
                        new_route.append(r1)        
                        pomak += 1            
                    else:                    
                        new_route.append(child[y1][j-pomak])                    

            while len(new_route) < self.C_NUM:            
                new_route.append(-1)            

            child[y1] = new_route     
            pomak = 0        
            new_route = np.array([-1]*self.C_NUM, dtype = np.int32)        
            for i in range (len(child[y1])):             
                if child[y1][i] == -1:                
                    pomak = pomak + 1                
                else:                
                    new_route[i-pomak] = child[y1][i]                
            child[y1] = new_route        
  
        return child
 
    #stvara random populaciju i pazi da kapacitet vozila na svakoj ruti 
	     #nije veći od onoga što vozilo moze podnijeti
	#ako je nemoguće prevesti teret (zahtjevi veći od vozila*kapacitet u idealnom slučaju koji je rijetko moguć)
	#program javlja fatal error - PAŽNJA KOD KORISNIČKOG UNOSA!!
    def create_population(self):
        #Create self.POPULATION
        v_load = np.zeros((self.POP, self.V_NUM), dtype=np.int32)
        for i in range(self.POP):
            unassigned = []
            routes = []
            for j in range(self.V_NUM):
                routes.append([])
        
            for j in range (self.C_NUM):
                a = random.randint(0, self.V_NUM-1)
                if v_load[i][a] + self.DEMAND[j][1] > self.V_CAP:
                    unassigned.append(self.DEMAND[j][0])
                else:
                    routes[a].append(self.DEMAND[j][0])
                    v_load[i][a] = v_load[i][a] + self.DEMAND[j][1]

            if len(unassigned) != 0:
                for n in range(len(unassigned)):
                    for j in range (self.V_NUM):
                        if v_load[i][j] + self.DEMAND[unassigned[n]-1][1] <= self.V_CAP:
                            v_load[i][j] = v_load[i][j] + self.DEMAND[unassigned[n]-1][1]
                            routes[j].append(self.DEMAND[unassigned[n]-1][0])
                            break
                
            for j in range(len(routes)):
                while(len(routes[j]) < self.C_NUM):
                    routes[j].append(-1)
                self.POPULATION[i][j] = routes[j]

        #Calculate self.FITNESS for each variation
        for i in range(self.POP):
            self.FITNESS[i] = self.calc_fitness(self.POPULATION[i])

    
    def get_size(self):
        return self.V_NUM, self.C_NUM

    def run(self):   
        self.create_population()     
        generation = 0

        while(generation < int(self.GEN_NUM)):
            elite = self.find_elite()
            fitness_chance = self.rank_population()
            fitness_temp = self.FITNESS.copy()
            best = self.POPULATION[elite].copy()
            best_fit = self.FITNESS[elite]
           
        # stvara novu populaciju (polje) koje će puniti s najboljima (child+parent) 
        
            new_population = np.zeros((self.POP, self.V_NUM, self.C_NUM), dtype=np.int32)
            m=0
            while fitness_temp.max() > 0:
                #Select parents        """ovdje se biraju roditelji"""
                selected = False
                while selected == False:
                    parent_a = random.random()
                    for i in range(len(fitness_chance)):
                        if fitness_chance[i] >= parent_a:
                            if fitness_temp[i] != -1:
                                parent_a = i
                                fitness_temp[i] = -1
                                selected = True
                                break

                selected = False
                while selected == False:
                    parent_b = random.random()
                    for i in range(len(fitness_chance)):
                        if fitness_chance[i] >= parent_b:
                            if parent_a != i and fitness_temp[i] != -1:
                                parent_b = i
                                fitness_temp[i] = -1
                                selected = True
                            break
				#crossover funkcija: od dva dobivena roditelja vraća dijete
                child_a = self.crossover(parent_a, parent_b)
                child_b = self.crossover(parent_b, parent_a)

                a = random.random()
                if a < 0.05:
                    child_a = self.mutate(child_a.copy())	#dijete a mutira sa šansom od 5%

                a = random.random()
                if a < 0.05:
                    child_b = self.mutate(child_b.copy()) 	#dijete b mutira sa šansom od 5%
            
                for i in range(self.V_NUM):		#provjera kapaciteta za dijete a (max 100)
                    cap_a = 0
                    for j in range (self.C_NUM):
                        if child_a[i][j] != -1:
                            for n in self.DEMAND:
                                if n[0] == child_a[i][j]:
                                    cap_a += n[1]
                                    break
                    if cap_a > self.V_CAP:
                        child_a =  None
                        break

                for i in range(self.V_NUM):		#provjera kapaciteta za dijete b (max 100)
                    cap_b = 0		
                    for j in range (self.C_NUM):
                        if child_b[i][j] != -1:
                            for n in self.DEMAND:
                                if n[0] == child_b[i][j]:
                                    cap_b += n[1]
                                    break
                    if cap_b > self.V_CAP:
                        child_b = None
                        break
        
                fit_f = []
                family = []
                if child_a != None:
                    fit_a = self.calc_fitness(child_a)   #računamo i pridodajemo vrijednost fitness za svako dijete a
                    fit_f.append(fit_a)
                    family.append(child_a.copy())
                if child_b != None:
                    fit_b = self.calc_fitness(child_b)
                    fit_f.append(fit_b)
                    family.append(child_b.copy())

                fit_f.append(self.FITNESS[parent_a])		#računamo i pridodajemo vrijednost fitness za svako dijete a
                family.append(self.POPULATION[parent_a].copy())
                fit_f.append(self.FITNESS[parent_b])
                family.append(self.POPULATION[parent_a].copy())

                for i in range(2):
                    a = random.random()						#stvaramo populaciju veličine 10 od prethodno napunjenih roditelja i djece (veličina 10)
                    for n in range(len(fit_f)):
                        if fit_f[n] > a:					
                            new_population[m] = family[n].copy()
                            m += 1
                            break
			
			#mičemo najslabiju jedinku iz populacije i zamjenjujemo ju najboljom iz populacije
            for i in range(self.POP):
                self.FITNESS[i] = self.calc_fitness(new_population[i].copy())
            new_population[self.FITNESS.argmax()] = self.POPULATION[elite].copy()
            self.FITNESS[self.FITNESS.argmax()] = self.calc_fitness(self.POPULATION[elite].copy())
            self.POPULATION = new_population.copy()
			
			#nova generacija
            generation += 1
		
		#vraća najbolji kromosom i njegovu fitness vrijednost (najmanju)
        return self.POPULATION[self.FITNESS.argmin()], self.FITNESS.min()
