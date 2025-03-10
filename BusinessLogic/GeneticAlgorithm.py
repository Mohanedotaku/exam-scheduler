import random
import numpy as np

class GeneticAlgorithm:
    def __init__(self, teachers, exams, population_size=50, generations=100, mutation_rate=0.1, elite_size=5):
        self.teachers = teachers
        self.exams = exams
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size

    def create_initial_population(self):
        population = []
        for _ in range(self.population_size):
            # Create a random assignment of teachers to exams
            chromosome = {}
            for exam in self.exams:
                # Randomly assign required number of teachers to each exam
                available_teachers = [t for t in self.teachers if self.is_teacher_available(t, exam)]
                if len(available_teachers) >= exam['supervisors_needed']:
                    selected_teachers = random.sample(available_teachers, exam['supervisors_needed'])
                    chromosome[exam['id']] = [t['id'] for t in selected_teachers]
                else:
                    # If not enough teachers available, assign as many as possible
                    chromosome[exam['id']] = [t['id'] for t in available_teachers]
            population.append(chromosome)
        return population

    def is_teacher_available(self, teacher, exam):
        # Check if teacher is available for this exam (no time conflict)
        # This would include checking weekly supervision limit
        exam_week = exam['date'].isocalendar()[1]  # Get the week number of the exam

        # Count how many supervisions the teacher already has in this week
        weekly_supervisions = sum(1 for e in self.exams
                                  if e['date'].isocalendar()[1] == exam_week
                                  and teacher['id'] in e.get('assigned_teachers', []))

        return weekly_supervisions < teacher['supervision_capacity']

    def fitness(self, chromosome):
        score = 0
        teacher_assignments = {t['id']: 0 for t in self.teachers}
        weekly_assignments = {t['id']: {} for t in self.teachers}

        # Check each exam
        for exam_id, assigned_teachers in chromosome.items():
            exam = next(e for e in self.exams if e['id'] == exam_id)
            week_num = exam['date'].isocalendar()[1]

            # Check if enough teachers are assigned
            if len(assigned_teachers) < exam['supervisors_needed']:
                score -= 100 * (exam['supervisors_needed'] - len(assigned_teachers))

            # Update assignment counts
            for teacher_id in assigned_teachers:
                teacher_assignments[teacher_id] += 1

                if week_num not in weekly_assignments[teacher_id]:
                    weekly_assignments[teacher_id][week_num] = 0
                weekly_assignments[teacher_id][week_num] += 1

        # Check weekly supervision limits
        for teacher in self.teachers:
            teacher_id = teacher['id']
            for week, count in weekly_assignments[teacher_id].items():
                if count > teacher['supervision_capacity']:
                    score -= 50 * (count - teacher['supervision_capacity'])

        # Reward balanced distribution
        std_dev = np.std(list(teacher_assignments.values()))
        score -= 20 * std_dev

        return score

    def select_parents(self, population, fitness_scores):
        # Tournament selection
        tournament_size = 3
        selected_parents = []

        # Add elite chromosomes first
        elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
        for idx in elite_indices:
            selected_parents.append(population[idx])

        # Tournament selection for the rest
        while len(selected_parents) < self.population_size:
            tournament = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament]
            winner_idx = tournament[np.argmax(tournament_fitness)]
            selected_parents.append(population[winner_idx])

        return selected_parents

    def crossover(self, parent1, parent2):
        child = {}
        for exam_id in parent1:
            if random.random() < 0.5:
                child[exam_id] = parent1[exam_id].copy()
            else:
                child[exam_id] = parent2[exam_id].copy()
        return child

    def mutate(self, chromosome):
        for exam_id in chromosome:
            if random.random() < self.mutation_rate:
                exam = next(e for e in self.exams if e['id'] == exam_id)

                # Either add or remove a teacher
                if random.random() < 0.5 and len(chromosome[exam_id]) > 0:
                    # Remove a random teacher
                    chromosome[exam_id].remove(random.choice(chromosome[exam_id]))
                else:
                    # Add a random teacher
                    available_teachers = [t['id'] for t in self.teachers
                                          if t['id'] not in chromosome[exam_id]
                                          and self.is_teacher_available(t, exam)]
                    if available_teachers:
                        chromosome[exam_id].append(random.choice(available_teachers))
        return chromosome

    def evolve(self):
        population = self.create_initial_population()

        for generation in range(self.generations):
            fitness_scores = [self.fitness(chrom) for chrom in population]

            # Select parents
            parents = self.select_parents(population, fitness_scores)

            # Create new population
            new_population = []

            # Keep elite chromosomes
            elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(population[idx])

            # Create offspring
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(parents, 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)

            population = new_population

            # Print progress
            best_fitness = max(fitness_scores)
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            print(f"Generation {generation}: Best Fitness = {best_fitness}, Avg Fitness = {avg_fitness}")

        # Return the best solution
        fitness_scores = [self.fitness(chrom) for chrom in population]
        best_idx = np.argmax(fitness_scores)
        return population[best_idx]