# Evolution Simulator version 0.2.1
# Author: Joshua McCready

import random
import sys


class Ecosystem(object):

    def __init__(self, habitat_list):
        """
        The Ecosystem class object acts as the world for the Evolution Simulator
        :param habitat_list: a list of Habitat objects
        :return: no return value
        """
        self.habitats = habitat_list

    def breed_all(self):
        """
        Calls the Habitat.breed_wildlife method on all habitats to simulate breeding.
        :return: no return value
        """
        for habitat in self.habitats:
            habitat.breed_wildlife()

    def migrate(self):
        """
        Checks to see if the new_gen organisms in each habitat can survive where they were born,
        if not they migrate to a habitat in which they can survive.
        :return: no return value
        """
        migrants = []
        for habitat in self.habitats:
            for organism in habitat.new_gen:
                if organism.can_survive(habitat):
                    habitat.wildlife.append(organism)
                else:
                    migrants.append(organism)
        for migrant in migrants:
            for habitat in self.habitats:
                if migrant.can_survive(habitat):
                    habitat.wildlife.append(migrant)
                    break

    def age_all(self):
        for habitat in self.habitats:
            [organism.get_older() for organism in habitat.wildlife]

    def remove_all_dead(self):
        for habitat in self.habitats:
            habitat.wildlife = [organism for organism in habitat.wildlife if organism.traits.life_span > 0]

    def print_wildlife_totals(self):
        for habitat in self.habitats:
            print habitat.name + ":  " + str(len(habitat.wildlife))

    def __repr__(self):
        return "Number of habitats in Ecosystem: {}".format(len(self.habitats))


class Habitat(object):

    def __init__(self, name, temp, water_avail, food_avail, wildlife_list=None, new_gen=None):
        """
        Creates a Habitat object.
        :param name: string, name of the habitat
        :param temp: int, the temperature of the habitat
        :param water_avail: int, the amount of water available
        :param food_avail: list of strings, the types of food available
        :param wildlife_list: list of organisms, can be None
        :param new_gen: list of new organisms, can be None
        :return: Habitat object
        """
        self.name = name
        self.temp = temp
        self.water_avail = water_avail
        self.food_avail = food_avail
        self.wildlife = wildlife_list
        self.new_gen = new_gen

    # Takes the list of Organisms in the self.wildlife attribute, pairs
    # them up and breeds them.  There must be two parents for breeding, so
    # one Organism in an odd-length list will not get to breed.
    def breed_wildlife(self):
        parent_list = self.wildlife[:]
        self.new_gen = []

        while True:
            if len(parent_list) <= 1:
                break

            mom_index = random.randint(0, len(parent_list) - 1)
            mom = parent_list.pop(mom_index)

            dad_index = random.randint(0, len(parent_list) - 1)
            dad = parent_list.pop(dad_index)

            i = 1
            while i <= mom.traits.birth_rate:
                child = mom.breed(dad)
                self.new_gen.append(child)
                i += 1

    def print_wildlife(self):
        print self.name + ":"
        for organism in self.wildlife:
            print organism

    def print_new_gen(self):
        for organism in self.new_gen:
            print organism

    def __repr__(self):
        return 'Life Forms: {}   Temperature: {}'.format(len(self.wildlife), self.temp)


class Organism(object):

    def __init__(self, genome, traits):
        self.genome = genome
        self.traits = traits

    def breed(self, mate):
        mom = self.genome
        dad = mate.genome
        child_genome = ''
        gene_pool = mom + dad
        number_of_genes = len(gene_pool) / 2
        
        mutate = random.randint(1, 100)
        if mutate <= MUTATION_RATE:
            mutated_gene_list = ['a', 'b', 'c', 'd']
            mutated_gene = mutated_gene_list[random.randint(0, len(mutated_gene_list) - 1)]
            gene_pool += mutated_gene
            number_of_genes += 1
      
        i = 0
        while i < number_of_genes:
            child_genome = child_genome + gene_pool[random.randint(0, len(gene_pool) - 1)]
            i += 1

        temp = self.traits.temp_tol
        water = self.traits.water_needed
        birth_rate = self.traits.birth_rate
        diet = self.traits.diet
        child_traits = Traits(temp, water, diet, birth_rate)
        child = Organism(child_genome, child_traits)
        child.express_genes()
        return child

    def express_genes(self):
        for key in GENE_EXPRESSION_DICT:
            if key in self.genome:
                GENE_EXPRESSION_DICT[key](self.traits)

    def can_survive(self, habitat):
        for food in self.traits.diet:
            if food in habitat.food_avail:
                if self.traits.temp_tol == habitat.temp and self.traits.water_needed <= habitat.water_avail:
                    return True
        return False

    def get_older(self):
        self.traits.life_span -= 1

    def __repr__(self):
        return "  " + self.genome + "-----\n" + str(self.traits)


class Traits(object):

    ALL_FOODS = ['grass', 'seeds', 'leaves', 'fruit']

    def __init__(self, temp_tol, water_needed, diet, food_needed=1, birth_rate=1, life_span=4):
        self.temp_tol = temp_tol
        self.water_needed = water_needed
        self.diet = diet
        self.food_needed = food_needed
        self.birth_rate = birth_rate
        self.life_span = life_span

    def inc_temp(self):
        self.temp_tol += 1
        if self.temp_tol > MAX_TEMP:
            self.temp_tol = MAX_TEMP
        return

    def dec_temp(self):
        self.temp_tol -= 1
        if self.temp_tol < MIN_TEMP:
            self.temp_tol = MIN_TEMP
        return

    def inc_water(self):
        self.water_needed += 1
        if self.water_needed > MAX_WATER:
            self.water_needed = MAX_WATER
        return

    def dec_water(self):
        self.water_needed -= 1
        if self.water_needed < MIN_WATER:
            self.water_needed = MIN_WATER
        return

    def inc_birth_rate(self):
        self.birth_rate += 1
        if self.birth_rate > MAX_BIRTH:
            self.birth_rate = MAX_BIRTH
        return

    def dec_birth_rate(self):
        self.birth_rate -= 1
        if self.birth_rate <= 0:
            self.life_span = 0
        return

    def inc_life_span(self):
        self.life_span += 1
        if self.life_span > MAX_LIFE:
            self.life_span = MAX_LIFE
        return

    def dec_life_span(self):
        self.life_span -= 1

    def add_to_diet(self):
        if len(self.diet) == len(self.ALL_FOODS):
            return
        else:
            self.diet.append(random.choice(list(set(self.diet) ^ set(self.ALL_FOODS))))
            return

    def remove_from_diet(self):
        if len(self.diet) <= 1:
            self.diet = []
            self.life_span = 0
            return
        else:
            self.diet.remove(random.choice(self.diet))
            return

    def __repr__(self):
        return "\tTemp: " + str(self.temp_tol) + "  Life Span: " + str(self.life_span) \
               + "  Birth Rate: " + str(self.birth_rate) + "  Water Needed: " + \
               str(self.water_needed) + "\n\tDiet: " + str(self.diet)


# CONSTANT DECLARATIONS
MUTATION_RATE = 10

FOREST_FOODS = ['leaves', 'seeds']
PLAINS_FOODS = ['grass', 'seeds']
JUNGLE_FOODS = ['leaves', 'seeds', 'fruit']
DESERT_FOODS = ['grass', 'seeds']

ALL_FOODS = ('grass', 'seeds', 'leaves', 'fruit')

MAX_TEMP = 5
MIN_TEMP = 3
MAX_WATER = 4
MIN_WATER = 1
MAX_BIRTH = 3
MAX_LIFE = 8

GENE_EXPRESSION_DICT = {'aa': Traits.inc_life_span,
                        'ad': Traits.inc_water,
                        'bb': Traits.dec_life_span,
                        'bd': Traits.dec_water,
                        'ca': Traits.inc_temp,
                        'cc': Traits.add_to_diet,
                        'cd': Traits.dec_birth_rate,
                        'db': Traits.dec_temp,
                        'dc': Traits.inc_birth_rate,
                        'dd': Traits.remove_from_diet}

# Seed organisms for each habitat
FOREST_ADAM = Organism('ab', Traits(3, 3, ['leaves']))
FOREST_EVE  = Organism('bc', Traits(3, 3, ['leaves']))
PLAINS_ADAM = Organism('da', Traits(4, 2, ['grass']))
PLAINS_EVE  = Organism('bc', Traits(4, 2, ['grass']))
JUNGLE_ADAM = Organism('ab', Traits(5, 4, ['fruit']))
JUNGLE_EVE  = Organism('cd', Traits(5, 4, ['fruit']))
DESERT_ADAM = Organism('ba', Traits(5, 1, ['seeds']))
DESERT_EVE  = Organism('ad', Traits(5, 1, ['seeds']))

FOREST_LIFE = [FOREST_ADAM, FOREST_EVE]
PLAINS_LIFE = [PLAINS_ADAM, PLAINS_EVE]
JUNGLE_LIFE = [JUNGLE_ADAM, JUNGLE_EVE]
DESERT_LIFE = [DESERT_ADAM, DESERT_EVE]

FOREST = Habitat('Forest', 3, 3, FOREST_FOODS, FOREST_LIFE, [])
PLAINS = Habitat('Plains', 4, 2, PLAINS_FOODS, [], [])
JUNGLE = Habitat('Jungle', 5, 4, JUNGLE_FOODS, [], [])
DESERT = Habitat('Desert', 5, 1, DESERT_FOODS, [], [])
HABITATS = [FOREST, PLAINS, DESERT, JUNGLE]


def main():

    world = Ecosystem(HABITATS)

    print "Evolution Simulator\n\n"
    while True:
        print "\nHow many generations would you like to progress?"
        print "Type 0 to quit."
        generations = int(raw_input("Enter choice: "))
        if generations == 0:
            sys.exit()
        i = 1
        while i <= generations:
            world.breed_all()
            world.migrate()
            world.age_all()
            world.remove_all_dead()
            i += 1
        while True:
            print "\nChoose one of the following:"
            print "0 - Back to generations."
            print "1 - Print number of organisms in each habitat."
            print "2 - Print wildlife in each habitat."
            choice = int(raw_input("Enter selection: "))
            if choice == 0:
                break
            elif choice == 1:
                print "\nTotal Wildlife in Each Habitat: "
                world.print_wildlife_totals()
            elif choice == 2:
                print "\nOrganisms in Each Habitat: "
                for habitat in HABITATS:
                    habitat.print_wildlife()


if __name__ == '__main__':
    main()
