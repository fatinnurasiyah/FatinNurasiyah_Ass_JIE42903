import streamlit as st
import csv
import random

def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings
    return program_ratings

import os
ratings = read_csv_to_dict(os.path.join(os.path.dirname(__file__), "program_ratings_modified.csv"))

st.title("📺 TV Program Scheduling using Genetic Algorithm")

st.sidebar.header("Adjust GA Parameters")
CO_R = st.sidebar.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8)
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R)", 0.01, 0.05, 0.02)

GEN = 100
POP = 50
EL_S = 2

all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))

def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot % len(ratings[program])]
    return total_rating

def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    population = [initial_schedule]
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for generation in range(generations):
        population.sort(key=lambda s: fitness_function(s), reverse=True)
        new_population = population[:elitism_size]

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = new_population[:population_size]

    return population[0]

if st.button("Run Genetic Algorithm"):
    initial_schedule = list(all_programs)
    random.shuffle(initial_schedule)
    best_schedule = genetic_algorithm(initial_schedule, crossover_rate=CO_R, mutation_rate=MUT_R)

    st.subheader("🕒 Optimal Schedule Result")
    table_data = {"Time Slot": [], "Program": []}
    for i, program in enumerate(best_schedule[:len(all_time_slots)]):
        table_data["Time Slot"].append(f"{all_time_slots[i]}:00")
        table_data["Program"].append(program)
    
    st.table(table_data)
    st.success(f"Total Ratings: {fitness_function(best_schedule):.2f}")
