import SimulationObjects as so
import FileHandlers as fh
import os
 
'''
Used for handling the simulation

Parameters:
    surface : surface which the simulation is drawn on
    camera : camera object used to view the simulation
'''
class Simulation:
    def __init__(self, surface, camera, layer):
        self.surface = surface
        self.camera = camera
        self.layer = layer
        self.algorithm = ""
        self.track_pieces = [] #Track which vehicles will follow
        self.algorithm_settings = {} #Simulation settings
        self.physics_settings = {} #Physics settings
        self.main_settings = {}
        self.population = None
        self._results_database = None #All test results are stored in here
        self._next_id = 0
        self._next_test = 0
        self.track_name = ""
        self.restart_count = 0
        self.simulation_ui = None #Not necessary, the simulation's ui
        self.save_simulation_file_path = ""

    #Set the results table to add data to
    #   additionally set the test id
    def set_results_database(self, database):
        self._results_database = database

        #Should not be able to pass none
        if database == None:
            raise Exception("Error; results database equals None")

        self._next_id = self._results_database.highest_entry("Tests", "id") + 1
        self._next_test = self._results_database.highest_entry("Tests", "test") + 1


    #Apply the algorithm settings to the simulation
    #   algorithm : string name of algorithm to use ("Astar", "Genetic", "Obstacle Avoidance")
    #   track_pieces : list of track pieces the vehicles should follow
    #   settings : the algorithm settings to apply to the vehicles (physics)
    def apply_algorithm_settings(self, algorithm, track_pieces, track_name, **settings):
        self.track_name = track_name
        self.algorithm = algorithm
        self.track_pieces = track_pieces
        self.algorithm_settings = settings

        #A* Algorithm choice
        if self._results_database == None:
            pass
        elif self.algorithm == "Astar":
            self._results_database.add_entry("AStarTests", test_id=self._next_test, follow_strength=self.algorithm_settings["follow-strength"])

        #Genetic Algorithm choice
        elif self.algorithm == "Genetic":
            self._results_database.add_entry("GeneticAlgTests", test_id=self._next_test, population_size=self.algorithm_settings["population-size"], mutation_rate=self.algorithm_settings["mutation-rate"], mutation_chance=self.algorithm_settings["mutation-chance"], existing_network="None")
            self.save_simulation_file_path = self.algorithm_settings["existing-network"]

        #Obstace avoidance choice
        elif self.algorithm == "Obstacle Avoidance":
            print("found")
            self._results_database.add_entry("WanderingTests", test_id=self._next_test, follow_strength=self.algorithm_settings["follow-strength"])
        else:
            raise Exception(f"Error; Invalid algorithm '{self.algorithm}'")


    #Apply the physics settings to the simulation
    def apply_physics_settings(self, **settings):
        self.physics_settings = settings

        #Create new entry to table
        if self._results_database != None:
            
            #Add the physics settings
            self._results_database.add_entry("Tests", id=self._next_id, test=self._next_test, maximum_velocity=settings["maximum-velocity"], acceleration_magnitude=settings["acceleration-magnitude"], deceleration_magnitude=settings["deceleration-magnitude"], turn_velocity=settings["turn-velocity"], vehicle_width=settings["vehicle-width"], vehicle_height=settings["vehicle-height"], track_name=self.track_name)


    #Apply the main menu settings to the simulation
    def apply_main_settings(self, **settings):
        self.main_settings = settings

    #Updates the ui's leaderbaord using the population's leaderboard
    def update_leaderboard(self):
        self.simulation_ui.update_leaderboard(population.leaderboard)

    #Reset vehicles in simulation
    #   essentially-re-creates the whole simulation
    def restart_simulation(self):
        self.restart_count += 1
        self.initialise_simulation()
        self.population.vehicle_no = self.restart_count

    #Save the simulation to an external file
    #   primary use for saving neural network in genetic algorithm
    def save_simulation(self):
        if self.algorithm == "Genetic":
            print(self.save_simulation_file_path)
            network_file = fh.TextFile("SavedNetwork.txt", "./output/")
            best_vehicle = self.population.best_vehicle

            if best_vehicle != None:
                best_network = best_vehicle.brain #get the NN of the best performing vehicle

                network_file.write_serialised([best_network.weights, best_network.biases])

    #Load a pre-existing simulation file with the given file name and path to file
    #   genetic algorithm modifies the network of the first vehicle in the vehicles array
    def load_simulation(self, file_name, file_path):
        if self.algorithm == "Genetic":

            network_file = fh.TextFile(file_name, file_path)
            output = network_file.read_serialised() #outputs network information [weights, biases]
            weights = output[0]
            biases = output[1]

            #Set network = set network to the given weights/biases
            self.population.vehicles[0].brain.set_network(weights, biases)



    #Initialises the simulation
    def initialise_simulation(self):

        #A* Algorithm choice
        if self.algorithm == "Astar":
            self.population = so.PopulationAStar(1, self.surface, self.camera, self, 100, 0, self.track_pieces)

        #Genetic Algorithm choice
        elif self.algorithm == "Genetic":
            self.population = so.PopulationGeneticAlgorithm(
                self.algorithm_settings["population-size"], 
                self.surface, self.camera, self,
                100, 0, 60, 
                3, 500, 
                self.track_pieces)

            #If there is an existing network specified
            if self.save_simulation_file_path != "" and os.path.exists(self.save_simulation_file_path):

                #Split path file name and path
                file_path, file_name = os.path.split(self.save_simulation_file_path)
                self.load_simulation(file_name=file_name, file_path=file_path+"/") #Split does not return "/" on end of path
            
        #Obstace avoidance choice
        elif self.algorithm == "Obstacle Avoidance":
            self.population = so.PopulationWandering(1, self.surface, self.camera, self, 100, 0, self.track_pieces)
        else:
            raise Exception(f"Error; Invalid algorithm '{self.algorithm}'")

        #Set results database so vehicles can be monitored
        self.population.set_results_database(self._results_database, self._next_test)

        #Add vehicles to layer
        self.layer.clear_objects()
        self.layer.add_objects(obj_list=self.population.vehicles)
        self.layer.add_objects(single_obj=self.population)
        self.layer.add_objects(single_obj=self.camera)
        self.layer.add_objects(obj_list=self.track_pieces)

        

        
