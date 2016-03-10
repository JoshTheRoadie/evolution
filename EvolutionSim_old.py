## Evolution Simulator version 0.2.1
## Author: Joshua McCready

## VERSION 0.2.1 NOTES:
## Attempting to put a set amount of food in each habitat.  There will be
## an available food attribute for the habitat, a replenish rate attribute
## food, and an amount that each organism needs to eat.  If food runs out,
## organisms should starve and die.  Each generation the food supply
## replenishes as much as its replenish rate... hopefully.  

## Welcome to Version 0.2.0!  For previous version notes, refer to
##      Evolve_v0.1.6.py
## The main guts of the program now work.  It is now time for details
##      and polish.

## VERSION 0.2.0 NOTES:
## Added:
##  --  Comments galore.
##  --  Simple UI.  More will be added later.
##  --  Created constant declarations for ADAM and EVE Organisms
##          for each Habitat.
##  --  Made each Habitat a constant

## THINGS TO FIX:
## - Ecosystem.migrate() needs to check for elements leftover
##      in the migrants list.  If an organism cannot survive in
##      any habitat it will still be in the list
## - BUG! Check the Organism.express_genes() method.  I once saw an
##      organism with .water_needed = 0 and .life_span = 0 in
##      a data list.  They should not have been there.  It could
##      be in Habitat.remove_dead() or Ecosystem.remove_all_dead()


import string
import random
import sys
import copy


class Ecosystem:

    #habitat_list = list of Habitat()
    def __init__(self, habitat_list = []):
        self.habitats = habitat_list    # List of Habitat()


    def __str__(self):
        return "Number of habitats in Ecosystem: " + str(len(self.habitats))


    # Breeds organisms in each habitat
    def breed_all(self):
        for habitat in self.habitats:
            habitat.breed_wildlife()


    # Migrates organisms to a new habitat if they cannot survive the one
    #   that they are living in and can survive one of the other habitats.
    def migrate(self):
        migrants = []

        # Checks if each organism in each habitat's new_gen list can
        #   survive in the habitat in which it was bred.
        #   if .can_survive == True: the organism is added to its birthplace
        #       habitat.
        #   if .can_survive == False: the organism is added to the
        #       migrants list.
        for habitat in self.habitats:
            i = 0
            while i < len(habitat.new_gen):
                if habitat.new_gen[i].can_survive(habitat):
                    habitat.wildlife.append(habitat.new_gen[i])
                else:
                    migrants.append(habitat.new_gen[i])
                i += 1

        # Pops a migrant from the migrants list and begins to traverse
        #   the habitats available.  If the migrant can survive the
        #   habitat, it is added to that habitat's wildlife.  Once this
        #   occurs, the loop breaks and goes to the next migrant.
        #   So the migrant moves to the first survivable habitat.
        while migrants != []:
            migrant = migrants.pop()
            j = 0
            while j < len(self.habitats):
                if migrant.can_survive(self.habitats[j]) == True:
                    self.habitats[j].wildlife.append(migrant)
                    break
                j += 1

    # Calls Organism.get_older() on each organism in each habitat in
    #   self.habitats.
    def age_all(self):
        for habitat in self.habitats:
            habitat.age_organisms()


    # Calls Habitat.remove_dead() on each habitat in self.habitats.
    #   Dead = any Organism with .trait.life_span <= 0
    def remove_all_dead(self):
        for habitat in self.habitats:
            habitat.remove_dead()


    # Prints the name and number of Organisms in each habitat.
    def print_wildlife_totals(self):
        for habitat in self.habitats:
            print habitat.name + ":  " + str(len(habitat.wildlife))


                                
class Habitat:

    # name = str, temp = int, water_avail = int, food_avail = list of str,
    # wildlife_list = list of Organism(), new_gen = list of Organism()
    def __init__(self, name, temp, water_avail, food_avail,
                 wildlife_list = [], new_gen = []):
        self.name = name               # Name of habitat
        self.temp = temp               # Temperature of the habitat
        self.water_avail = water_avail # Amount of water available
        self.food_avail = food_avail   # Names of food available
        self.wildlife = wildlife_list  # A list of organisms in this habitat
        self.new_gen = new_gen         # A list of the newest generation of organisms

        new_food_list = []             # Takes list of strings and turns it into
        for food in food_avail:        #   a list of Food() objects
            new_food = Food(food, FOOD_DICT[food])
            new_food_list.append(new_food)
        self.foods = new_food_list     # List of Food()

  
    def __str__(self):
        return "Life Forms: " + str(len(self.wildlife)) \
               + "  Temperature: " + str(self.temp)


    # Takes the list of Organisms in the self.wildlife attribute, pairs
    # them up and breeds them.  There must be two parents for breeding, so
    # one Organism in an odd-length list will not get to breed.
    def breed_wildlife(self):
        parent_list = self.wildlife[:]
        self.new_gen = []

        while True:
            # must have 2 available parents in the parent_list
            if len(parent_list) <= 1:
                break

            # Chooses and mom and dad by generating a random index
            #   and then popping that index from the list of parents.
            mom_index = random.randint(0, len(parent_list) - 1)
            mom = parent_list.pop(mom_index)

            dad_index = random.randint(0, len(parent_list) - 1)
            dad = parent_list.pop(dad_index)

            # Calls .breed() a number of times equal to the mom's
            #   .birth_rate using the same mom and dad as the
            #   parameters. 
            i = 1
            while i <= mom.traits.birth_rate:
                child = mom.breed(dad)
                self.new_gen.append(child)
                i += 1


    # Calls .get_older() on each Organism in self.wildlife.
    def age_organisms(self):
        for organism in self.wildlife:
            organism.get_older()


    # Removes each Organism in self.wildlife with .life_span
    #   that is <= 0.
    def remove_dead(self):
        for organism in self.wildlife[:]:
            if organism.traits.life_span <= 0:
                self.wildlife.remove(organism)

            
    # Prints each Organism in the self.wildlife list.           
    def print_wildlife(self):
        print self.name + ":"
        for organism in self.wildlife:
            print organism


    # Prints each Organism in the self.new_gen list.
    def print_new_gen(self):
        for organism in self.new_gen:
            print organism



class Organism:

    def __init__(self, genome, traits):
        self.genome = genome
        self.traits = traits

        
    def __str__(self):
        return "  " + self.genome + "-----\n" + str(self.traits)


    # Takes two Organism objects and returns a child Organism object
    def breed(self, other):
        mom = self.genome
        dad = other.genome
        child_genome = ''
        gene_pool = mom + dad
        number_of_genes = len(gene_pool) / 2
        
        mutate = random.randint(1, 100)
        if mutate <= MUTATION_RATE:
            mutated_gene_list = ['a', 'b', 'c', 'd']
            mutated_gene = mutated_gene_list[random.randint(0, len(mutated_gene_list) - 1)]
            gene_pool = gene_pool + mutated_gene
            number_of_genes = number_of_genes + 1
      
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


    # Determines whether or not an Organism can survive in a habitat
    def can_survive(self, habitat):
        survival_counter = 0
        if self.traits.temp_tol == habitat.temp: # checks temp_tol
            survival_counter += 1
        if self.traits.water_needed <= habitat.water_avail: # checks water_needed
            survival_counter += 1
        for food in self.traits.diet:  # checks diet
            if food in habitat.food_avail:
                survival_counter += 1
        if survival_counter >= 3:
            return True
        else:
            return False


    def get_older(self):
        self.traits.life_span = self.traits.life_span - 1

        
class Traits():

    def __init__(self, temp_tol, water_needed, diet,
                 food_needed = 1, birth_rate = 1, life_span = 4):
        self.temp_tol = temp_tol
        self.water_needed = water_needed
        self.diet = diet
        self.food_needed = food_needed
        self.birth_rate = birth_rate
        self.life_span = life_span


    def __str__(self):
        return "\tTemp: " + str(self.temp_tol) + "  Life Span: " + str(self.life_span) \
               + "  Birth Rate: " + str(self.birth_rate) + "  Water Needed: " + \
               str(self.water_needed) + "\n\tDiet: " + str(self.diet)


    def inc_temp(self):
        self.temp_tol = self.temp_tol + 1
        if self.temp_tol > MAX_TEMP:
            self.temp_tol = MAX_TEMP
        return


    def dec_temp(self):
        self.temp_tol = self.temp_tol - 1
        if self.temp_tol < MIN_TEMP:
            self.temp_tol = MIN_TEMP
        return


    def inc_water(self):
        self.water_needed = self.water_needed + 1
        if self.water_needed > MAX_WATER:
            self.water_needed = MAX_WATER
        return


    def dec_water(self):
        self.water_needed = self.water_needed - 1
        if self.water_needed < MIN_WATER:
            self.water_needed = MIN_WATER
        return


    def inc_birth_rate(self):
        self.birth_rate = self.birth_rate + 1
        if self.birth_rate > MAX_BIRTH:
            self.birth_rate = MAX_BIRTH
        return


    def dec_birth_rate(self):
        self.birth_rate = self.birth_rate - 1
        if self.birth_rate <= 0:
            self.life_span = 0
        return


    def inc_life_span(self):
        self.life_span = self.life_span + 1
        if self.life_span > MAX_LIFE:
            self.life_span = MAX_LIFE
        return


    def dec_life_span(self):
        self.life_span = self.life_span - 1


      
    def add_to_diet(self):
        current_foods = self.diet[:]
        all_foods = FOOD_DICT.keys()
        if len(current_foods) == len(all_foods):
            return
        else:
            for food in current_foods:
                all_foods.remove(food)
            food_to_add = random.choice(all_foods)
            self.diet.append(food_to_add)
            return


    def remove_from_diet(self):
        if len(self.diet) <= 1:
            self.diet = []
            self.life_span = 0
            return
        else:
            food_to_remove = random.choice(self.diet)
            self.diet.remove(food_to_remove)
            return


class Food():

    def __init__(self, name, replenish_rate = 10):
        self.name = name
        self.replenish_rate = replenish_rate


    def __str__(self):
        return self.name + "  Replenish Rate: " + str(self.replenish_rate)

        
# CONSTANT DECLARATIONS
MUTATION_RATE = 10

    # Foods and Food Dictionary
GRASS = 'grass'
SEEDS = 'seeds'
LEAVES = 'leaves'
FRUIT = 'fruit'


FOREST_FOODS = [LEAVES, SEEDS]
PLAINS_FOODS = [GRASS, SEEDS]
JUNGLE_FOODS = [LEAVES, SEEDS, FRUIT]
DESERT_FOODS = [GRASS, SEEDS]

FOOD_DICT = {GRASS : 12, SEEDS : 8,
             LEAVES : 10, FRUIT : 9} # format for k/v = name : replenish_rate

    # Max and Min for attributes to avoid going out of range
MAX_TEMP = 5
MIN_TEMP = 3

MAX_WATER = 4
MIN_WATER = 1

MAX_BIRTH = 3

MAX_LIFE = 8

    # Gene Expression Dictionary.  Maps Trait methods to the genes that
    # trigger them.
GENE_EXPRESSION_DICT = {'aa' : Traits.inc_life_span,
                       'ad' : Traits.inc_water,
                       'bb' : Traits.dec_life_span,
                       'bd' : Traits.dec_water,
                       'ca' : Traits.inc_temp,
                       'cc' : Traits.add_to_diet,
                       'cd' : Traits.dec_birth_rate,
                       'db' : Traits.dec_temp,
                       'dc' : Traits.inc_birth_rate,
                       'dd' : Traits.remove_from_diet}

    # Seed organisms for each habitat and their lists
FOREST_ADAM = Organism('ab', Traits(3, 3, [LEAVES]))
FOREST_EVE  = Organism('bc', Traits(3, 3, [LEAVES]))
PLAINS_ADAM = Organism('da', Traits(4, 2, [GRASS]))
PLAINS_EVE  = Organism('bc', Traits(4, 2, [GRASS]))
JUNGLE_ADAM = Organism('ab', Traits(5, 4, [FRUIT]))
JUNGLE_EVE  = Organism('cd', Traits(5, 4, [FRUIT]))
DESERT_ADAM = Organism('ba', Traits(5, 1, [SEEDS]))
DESERT_EVE  = Organism('ad', Traits(5, 1, [SEEDS]))

FOREST_LIFE = [FOREST_ADAM, FOREST_EVE]
PLAINS_LIFE = [PLAINS_ADAM, PLAINS_EVE]
JUNGLE_LIFE = [JUNGLE_ADAM, JUNGLE_EVE]
DESERT_LIFE = [DESERT_ADAM, DESERT_EVE]

    
FOREST = Habitat('Forest', 3, 3, FOREST_FOODS, FOREST_LIFE, [])
PLAINS = Habitat('Plains', 4, 2, PLAINS_FOODS, [], [])
JUNGLE = Habitat('Jungle', 5, 4, JUNGLE_FOODS, [], [])
DESERT = Habitat('Desert', 5, 1, DESERT_FOODS, [], [])
HABITATS = [FOREST, PLAINS, DESERT, JUNGLE]

# MAIN FUNCTION        
def main():

    WORLD = Ecosystem(HABITATS)

    print "Evolution Simulator\n\n"
    while True:
        print "\nHow many generations would you like to progress?"
        print "Type 0 to quit."
        generations = int(raw_input("Enter choice: "))
        if generations == 0:
            sys.exit()
        i = 1
        while i <= generations:
            WORLD.breed_all()
            WORLD.migrate()
            WORLD.age_all()
            WORLD.remove_all_dead()
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
                WORLD.print_wildlife_totals()
            elif choice == 2:
                print "\nOrganisms in Each Habitat: "
                for habitat in HABITATS:
                    habitat.print_wildlife()


    
if __name__ == '__main__':
    main()
