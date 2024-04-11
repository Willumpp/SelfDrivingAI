from CustomStructures import *
from StructureAlgorithms import bubble_sort
from FileHandlers import TextFile
import pygame
import math
import numpy as np
import random
import time
 

#Draw a circle at the given point
def draw_circle(inp, col, win, camera):
    pygame.draw.circle(win, col, camera.to_screen_pos(inp).get_pos(), 5)

'''
Simulation object class
Every object in the simulation should inherit from this

This allows for easy tracking of world position, camera position, and global position

Parameters:
    surface : the surface to draw pygame lines on
    camera : the camera which the object follows
    xpos and ypos : the global position of the object

Methods:
    to_screen_pos(vectos) : converts a given vector to the screen position to draw
'''
class SimulationObject:
    def __init__(self, surface, camera, simulation_handler, xpos, ypos, width=0, height=0):
        self.camera = camera
        self.surface = surface
        self.simulation_handler = simulation_handler
        self.size = Vector(width, height)
        self.direction = 0
        self._pos = Vector(xpos, ypos)
        self._screen_pos = Vector(xpos, ypos)
        self.tags = []
        self.visible = True


    #Returns the vector of objects position
    def get_pos(self):
        return self._pos

    #Set the position of the object
    def set_pos(self, xpos, ypos):
        self._pos = Vector(xpos, ypos)

    #Returns the vector of objects screen position
    def get_screen_pos(self):
        return self._screen_pos

    #Returns the vector of objects screen position
    def get_screen_size(self):
        if self.camera != None:
            return self.camera.scale * self.size
        else:
            return self.size

    #Set the direction of the object
    def set_direction(self, direction):
        self.direction = direction

    #Convert given vector to screen position with the camera
    def to_screen_pos(self, vector):
        return self.camera.scale * (vector - self.camera.get_pos()) + self.camera.get_screen_pos()

    #Convert given vector to world position
    def to_world_pos(self, vector):
        return (1/self.camera.scale * (vector  - self.camera.get_screen_pos()) ) + self.camera.get_pos()

    def _draw_border(self):
        pygame.draw.lines(self.surface, (0,0,0), True, [(self._screen_pos.x, self._screen_pos.y), (self._screen_pos.x + self.size.x, self._screen_pos.y),
                            (self._screen_pos.x + self.size.x, self._screen_pos.y + self.size.y), (self._screen_pos.x, self._screen_pos.y + self.size.y)])

    #Add tag to object
    #   tag : tag to add to object
    def add_tag(self, tag):
        self.tags.append(tag)
    
    #Returns if object has all tags in passed tag list
    def has_tags(self, tags):
        _has_all = True

        #If tag in list is not on object
        for tag in tags:
            if tag not in self.tags:
                _has_all = False


        return _has_all

    def draw(self):
        self._screen_pos = self.to_screen_pos(self._pos)

    def update(self, events):
        #Update screen position so its relative to camera
        #   +camera.screen pos to make the camera centered
        if self.camera != None:
            self._screen_pos = self.to_screen_pos(self._pos)

    def get_draw_centre(self):
        draw_size = self.get_screen_size()

        #This applies the matrix transformation rotation on the width and height of the area
        width = abs(draw_size.x * math.cos(self.direction)) + abs(draw_size.y * math.sin(self.direction))
        height = abs(draw_size.x * math.sin(self.direction)) + abs(draw_size.y  * math.cos(self.direction))


        return 0.5 * Vector(width, height)

    #Set visibility of object
    def set_visible(self, active):
        self.visible = active

'''
Camera class
Every object will be drawn relative to the camera's coordinates
'''
class Camera(SimulationObject):
    def __init__(self, surface, xpos, ypos):
        super().__init__(surface, None, None, xpos, ypos)
        self.scale = 1
        self.camera = self
        self.test_ray = Ray(surface, self, 0, 0, Vector(0,0))

    #Draw the camera at the screen position (debugging)
    def draw(self):
        pygame.draw.rect(self.surface, (255,0,0), pygame.Rect(self._screen_pos.x, self._screen_pos.y, 10, 10))

##        ray = self.test_ray
##        ray._pos = self._pos
##        mx, my = pygame.mouse.get_pos()
##        ray.set_direction(math.pi/2) 
##        # ray.direction = (Vector(mx, my) - self._screen_pos).normalised()
##        ray.draw()
##
##        for points in ray.tracks_collision_check():
##                for point in points:
##                    pygame.draw.circle(self.surface, (0,0,255), self.to_screen_pos(point).int().get_pos(), 5)

        


    def update(self, events):
        pass
        #Temporary camera movement test
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self._pos.x -= 10
        elif keys[pygame.K_RIGHT]:
            self._pos.x += 10

        if keys[pygame.K_UP]:
            self._pos.y -= 10
        elif keys[pygame.K_DOWN]:
            self._pos.y += 10


'''
Vehicle class

population : the population which created the vehicle, can be left as "None"
'''
class Vehicle(SimulationObject):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos, fps, track_pieces, population):
        width = simulation_handler.physics_settings["vehicle-width"]
        height = simulation_handler.physics_settings["vehicle-height"]
        super().__init__(surface, camera, simulation_handler, xpos, ypos, width=width, height=height)

        self.rect_surface = pygame.Surface((self.size.x, self.size.y)) #Create the rect as a surface, this allows rotation
        #Set the background colour of the surface, this removes a coloured background in rotation
        self.rect_surface.set_colorkey((255, 255, 255)) 

        self.population = population

        self.track_pieces = track_pieces
        self.frame_period = 1 / fps
        self.set_direction(0)

        self.velocity = Vector(0, 0) 
        self.maximum_velocity = simulation_handler.physics_settings["maximum-velocity"] #Caps the velocity's magnitude to this value (pixels/second)
        self.acceleration = Vector(0, 0) #pixels/second/second , applied when moving
        self.acceleration_mag = simulation_handler.physics_settings["acceleration-magnitude"]
        self.drag_factor = simulation_handler.physics_settings["deceleration-magnitude"]/100 #Drag for when not moving, values closer to 1 means quicker deacceleration
        self.state_move = False #Set to true to move the vehicle

        self.turn_state = "none" #"left", "none", "right" to control turn direction
        self.turn_speed = simulation_handler.physics_settings["turn-velocity"] #radian per second turn speed

        self.alive = True
        self.tracks_crossed = []
        self.results = {
            "time-active" : 0, #Time spent active (incremented in update)
            "distance-travelled" : 0, #Total distance (not displacement) travelled
            "errors-made" : len(track_pieces), #How long spent off-road, distance from end
        }
    
    #Get the collected results from the vehicle
    def get_results(self):
        return self.results

    def reset_vehicle(self, xpos, ypos):
        self.set_direction(0)
        self.velocity = Vector(0, 0)
        self.acceleration = Vector(0, 0)
        self.state_move = False
        self.turn_state = "none"
        self._pos = Vector(xpos, ypos)
        self.draw_self = True
        self.alive = True
        self.results = {
            "time-active" : 0,
            "distance-travelled" : 0, 
            "errors-made" : len(self.track_pieces),
        }

    def kill(self):
        self.alive = False

    def update(self, events):
        super().update(events)
        #self.camera.set_pos(*self._pos.get_pos())

        #TEMPORARY - Point towards the mouse cursor 
        #   subtract pi / 2 to look towards the cursor
        # mouse_pos = pygame.mouse.get_pos()
        # self.set_direction(math.atan2(mouse_pos[0] - self._screen_pos.x, mouse_pos[1] - self._screen_pos.y) - math.pi/2)

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_SPACE]:
        #     self.state_move = True
        # else:
        #     self.state_move = False

        if self.alive == True:
            self.results["time-active"] += self.frame_period #time active in seconds (includes decimals)

            #Check if crossed any track pieces
            #   crossed if vehicle is closer than the size of the track
            _inside_track = False
            for track in self.track_pieces:
                #If vehicle is inside a track piece
                if track.collision_point(self._pos) == True:
                    _inside_track = True

                if track in self.tracks_crossed: continue

                #Calculate distance from end
                if (track._pos - self._pos).get_mag() <= track.size.get_mag():
                    self.tracks_crossed.append(track)
                    self.results["errors-made"] -= 1
            
            if _inside_track == False:
                self.results["errors-made"] += self.frame_period #time outside track



            self.acceleration.x = self.acceleration_mag * math.cos(self.direction)
            self.acceleration.y = -self.acceleration_mag * math.sin(self.direction)

            #Apply velocity if allowed to move
            if self.state_move == True:

                #Apply and cap acceleration
                if self.velocity.get_mag() < self.maximum_velocity:
                    self.velocity += self.frame_period * self.acceleration
                else:
                    self.velocity = (self.maximum_velocity - 1) * self.velocity.normalised()
            else:

                #Apply drag
                if int(self.velocity.get_mag()) != 0:
                    self.velocity = self.drag_factor * self.velocity #best factor ~0.9
                else:
                    self.velocity.set_pos(0,0)
            
            self._pos += self.frame_period * self.velocity
            self.results["distance-travelled"] += self.frame_period * self.velocity.get_mag() #distance = speed * time

            #Turn left or right
            if self.turn_state == "left":
                self.set_direction(self.direction + self.frame_period * self.turn_speed)
            elif self.turn_state == "right":
                self.set_direction(self.direction - self.frame_period * self.turn_speed)  


    def draw(self):
        if self.visible == True:
            self._screen_pos = self.to_screen_pos(self._pos)
            draw_size = self.get_screen_size()
            
            #Create new rotated rect surface
            if self.rect_surface.get_width() != draw_size.x or self.rect_surface.get_height() != draw_size.y:
                self.rect_surface = pygame.Surface(draw_size.get_pos())
                
            _draw_pos = self._screen_pos - self.get_draw_centre() #Centre object

            # self.rect_surface.fill((255,0,0)) #Fill red
            self.rect_surface.fill(self.simulation_handler.main_settings["vehicle-colour"]) #Fill with custom colour

            #Rotate the image
            rotated_image = pygame.transform.rotate(self.rect_surface, self.direction*180/math.pi) #Save the image to get the width etc
            self.surface.blit(rotated_image, _draw_pos.get_pos())

            #pygame.draw.circle(self.surface, (0,255,0), self._screen_pos.int().get_pos(), 5)
            # pygame.draw.rect(self.surface, (255,0,0), [*self._screen_pos.get_pos(), *self.get_screen_size().get_pos()])
            #self._draw_border()

'''
Vehicle using A* pathfinding
Inherits from vehicle
'''
class VehicleAStar(Vehicle):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos, fps, track_pieces, population):
        super().__init__(surface, camera, simulation_handler, xpos, ypos, fps, track_pieces, population)
        self.follow_strength = simulation_handler.algorithm_settings["follow-strength"]/100

    def update(self, events):
        super().update(events)
        dist = 100
        
        p1 = dist * Vector(math.cos(self.direction), -math.sin(self.direction)) + self._pos #Point in front of vehicle
        p2 = self.population.get_closest_point(p1) #Point on track closest to point in front of vehicle

        #Show points
        # draw_circle(p1, (255,0,0), self.surface, self.camera)
        # draw_circle(p2, (255,0,255), self.surface, self.camera)


        #Approach path
        _target_offset = p2 - self._pos
        _desired_velocity = self.maximum_velocity * (self.follow_strength/dist * _target_offset) #Scaled velocity based of the distance point is away

        self.velocity = _desired_velocity

        #Make points relative to vehicle
        p1 -= self._pos
        p2 -= self._pos

        self.state_move = True

        #Find angle between points and turn
        _angle = p1.angle(p2)

        if _angle > 0 :
            self.turn_state = "right"
        elif _angle < 0 :
            self.turn_state = "left"
        else:
            self.turn_state = "none"

'''
Vehicle using wandering behaviour
Inherits from vehicle
'''
class VehicleWandering(Vehicle):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos, fps, track_pieces, population):
        super().__init__(surface, camera, simulation_handler, xpos, ypos, fps, track_pieces, population)

        ray_count = 3
        ray_length = 500

        #Create rays for casting
        self.rays = []
        self.ray_count = ray_count
        self.ray_length = ray_length
        self.ray_distances = []
        self.draw_self = True
        angle = math.pi / (ray_count + 1)

        for i in range(0, self.ray_count):
            direction = Vector(math.cos((i+1) * angle - math.pi/2), math.sin((i+1) * angle - math.pi/2))

            _ray = Ray(surface, camera, xpos, ypos, direction)
            _ray.add_track_pieces(multiple_pieces=track_pieces)
            self.rays.append(_ray)
            self.ray_distances.append(self.ray_length)

        self.follow_strength = simulation_handler.algorithm_settings["follow-strength"]/100

        self.collision_range = min(*self.size.get_pos())


    #Updates "ray distances" to closest track intersections
    def cast_rays(self, events):

        #Ray cast to track edges
        angle = math.pi / (len(self.rays) + 1)
        for ray_i in range(0, len(self.rays)):
            _ray = self.rays[ray_i]

            _ray.set_pos(*(self._pos).get_pos())
            _ray.update(events)
            _ray.set_direction((ray_i + 1) * angle - self.direction - math.pi / 2)

            #get all the distances from all intersection points on ray cast
            #   ray cast has multiple intersections as ray passes through track pieces
            _distances = []
            for points in _ray.tracks_collision_check():

                for point in points:
                    _distance = (point - self._pos).get_mag()
                    _distances.append(_distance)

            #get the closest point if there are more than one
            if len(_distances) > 1:
                self.ray_distances[ray_i] = bubble_sort(_distances)[0] #get closest intersection point on line
            elif len(_distances) == 1:
                self.ray_distances[ray_i] = _distances[0]
            
            self.ray_distances[ray_i] = min(self.ray_distances[ray_i], self.ray_length)

    def update(self, events):
        if self.alive == True:
            super().update(events)

            self.cast_rays(events)
            self.state_move = True

            #Left/right movement
            if self.ray_distances[0] < 75 * self.follow_strength:
                self.turn_state = "right"
            elif self.ray_distances[2] < 75 * self.follow_strength:
                self.turn_state = "left"
            else:
                self.turn_state = "none"

            # _steering = _desired_velocity - self.velocity #Acceleration of the vehicle to slow down
            
            #Approach wall
            _target_offset = self.ray_distances[1] * Vector(math.cos(self.direction), -math.sin(self.direction)) #Coordinate of track intersection
            _distance = self.ray_distances[1] #Distance intersection is away
            _desired_velocity = self.maximum_velocity * (self.follow_strength/(self.ray_length) * _target_offset) #Scaled velocity based of the distance point is away

            self.velocity = _desired_velocity
            
            #Kill vehicle if collided with wall
            for distance in self.ray_distances:
                if distance <= self.collision_range:
                    self.kill()
                    break

    def draw(self):
        super().draw()

        for ray in self.rays:
            ray.draw()




'''
Vehicle using a genetic algorithm
Inherits from vehicle
'''
class VehicleGeneticAlgorithm(Vehicle):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos, fps, ray_count, ray_length, track_pieces, population):
        super().__init__(surface, camera, simulation_handler, xpos, ypos, fps, track_pieces, population)

        self.net_sequence = [ray_count, 4, 4, 2]
        self.brain = Network(self.net_sequence)
        self.alive = True
        self.fitness = 0
        self.population_owner = None

        self.rays = []
        self.ray_length = ray_length
        self.ray_count = ray_count
        self.ray_distances = []
        self.draw_self = True
        angle = math.pi / (ray_count + 1)

        for i in range(0, ray_count):
            direction = Vector(math.cos((i+1) * angle - math.pi/2), math.sin((i+1) * angle - math.pi/2))

            self.rays.append(Ray(surface, camera, xpos, ypos, direction))
            self.ray_distances.append(self.ray_length)
        
        for ray in self.rays:
            ray.add_track_pieces(multiple_pieces=track_pieces)

        self.collision_range = min(*self.size.get_pos())


    #Updates "ray distances" to closest track intersections
    def cast_rays(self, events):

        #Ray cast to track edges
        angle = math.pi / (len(self.rays) + 1)
        for ray_i in range(0, len(self.rays)):
            _ray = self.rays[ray_i]

            _ray.set_pos(*(self._pos).get_pos())
            _ray.update(events)
            _ray.set_direction((ray_i + 1) * angle - self.direction - math.pi / 2)

            #get all the distances from all intersection points on ray cast
            #   ray cast has multiple intersections as ray passes through track pieces
            _distances = []
            for points in _ray.tracks_collision_check():

                for point in points:
                    _distance = (point - self._pos).get_mag()
                    _distances.append(_distance)

                    # if _distance <= 10:
                    #     self.velocity = 0.5 * self.velocity.get_mag() * (self._pos - point).normalised()
                    #     # self.acceleration = 0
                    #     # self.set_direction(-self.direction)


                
            #get the closest point if there are more than one
            if len(_distances) > 1:
                self.ray_distances[ray_i] = bubble_sort(_distances)[0] #get closest intersection point on line
            elif len(_distances) == 1:
                self.ray_distances[ray_i] = _distances[0]
            
            self.ray_distances[ray_i] = min(self.ray_distances[ray_i], self.ray_length)


    def update(self, events):
        if self.alive == True:
        
            self.cast_rays(events)
            # print(self.ray_distances)

            #Pass rays through brain
            brain_output = self.brain.forward(np.array(self.ray_distances))
            _max_index = np.argmax(brain_output) #return the index of the greatest value
            
            #Make choice on movement
            if _max_index == 0:
                self.turn_state = "left"
            elif _max_index == 1:
                self.turn_state = "right"

            self.state_move = True

            # elif _max_index == 2:
            #     self.state_move = True
            # elif _max_index == 3:
            #     self.state_move == False


            #Kill vehicle if collided with wall
            for distance in self.ray_distances:
                if distance <= self.collision_range/1.41:
                    self.kill()
                    
                    # self.kill("death wall collision")
                    break
            
            super().update(events)

    def draw(self):
        super().draw()
        # for ray in self.rays:
        #     ray.draw()

    def reset_vehicle(self, *args):
        super().reset_vehicle(*args)
        self.alive = True
        self.fitness = 0
        self.tracks_crossed.clear()

        self.ray_distances.clear()
        self.rays.clear()
        angle = math.pi / (self.ray_count + 1)
        for i in range(0, self.ray_count):
            direction = Vector(math.cos((i+1) * angle - math.pi/2), math.sin((i+1) * angle - math.pi/2))

            self.rays.append(Ray(self.surface, self.camera, *self._pos.get_pos(), direction))
            self.ray_distances.append(self.ray_length)
        
        for ray in self.rays:
            ray.add_track_pieces(multiple_pieces=self.track_pieces)

        # self.ray_distances.clear()
        # for i in range(self.ray_count):
        #     self.ray_distances.append(500)

    #Destroys the vehicle
    #   message : message to display when vehicle is destroyed
    def kill(self, message=""):
        if message != "":
            print("reason:", message)
        self.alive = False

        #Create fitness score
        self.fitness += len(self.tracks_crossed) ** 2 #Number of tracks crossed

        #Calculate fitness based on distance away from next closest piece
        # piece_distances = []
        # for piece in self.track_pieces:
        #     if piece in self.tracks_crossed: continue

        #     piece_distances.append((piece.get_end_pos() - self._pos).get_mag())

        # piece_distances = bubble_sort(piece_distances)
        # if len(piece_distances) > 0:
        #     self.fitness += 300 / piece_distances[0] #Closer vehicles have higher fitnesses

        if len(self.tracks_crossed) != 0:
            _distance = (self.tracks_crossed[-1].get_end_pos() - self._pos).get_mag()
            self.fitness += 300 / _distance

        #Add fitness score to population owner
        if self.population_owner != None:
            self.population_owner.add_fitness(self, self.fitness)

'''
Population class
Used to create a population of vehicles for the simualtion
All simulations will inherit from this
'''
class Population(SimulationObject):
    def __init__(self, population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces):
        super().__init__(surface, camera, simulation_handler, xpos, ypos)

        self.track_pieces = track_pieces
        self.population_size = population_size
        self.vehicles = []

        self.start_piece = None
        self.end_piece = None

        #Get the start and end pieces
        #   makes use of their tag having "start" or "end"
        for piece in track_pieces:
            if piece.has_tags(["start"]):
                self.start_piece = piece

            if piece.has_tags(["end"]):
                self.end_piece = piece

        if self.start_piece == None:
            raise Exception("Error; Start piece not found")
        if self.end_piece == None:
            raise Exception("Error; End piece not found")

        self._results_database = None
        self._test_id = 0
        self.vehicle_no = 0

        self.leaderboard = ["" for i in range(10)]

    def set_results_database(self, database, test_id):
        self._test_id = test_id
        self._results_database = database

    #Return the vehicle selected in the population
    def get_selected_vehicle(self):
        return self.selected_vehicle

    #Return the list of vehicles in the population
    def get_vehicles(self):
        return self.vehicles

    def update(self, events):
        #Set camera to the selected vehicle
        # self.camera.set_pos(*self.selected_vehicle.get_pos().get_pos())
        
        #Get finishing vehicle
        for vehicle in self.vehicles:
            if vehicle.alive == False:
                continue
            
            #If vehicle is within distance of end piece
            if (self.end_piece._pos - vehicle._pos).get_mag() < self.end_piece.size.x/2:
                vehicle.kill()

                #Add vehicle entry to database
                if self._results_database != None:
                    results = vehicle.get_results()
                    _next_id = self._results_database.highest_entry("Vehicles", "id") + 1
                    self._results_database.add_entry("Vehicles", id=_next_id, test_id=self._test_id, vehicle_no=self.vehicle_no, completion_time=results["time-active"], distance_travelled=results["distance-travelled"], errors_made=results["errors-made"])
                    self.vehicle_no += 1

'''
Population of vehicles using A* pathfinding
'''
class PopulationAStar(Population):
    #Node for pathfinding
    class Node:
        def __init__(self, xpos, ypos, start_pos, end_pos, node_size, grid):
            self.start_pos = start_pos
            self.end_pos = end_pos
            self._pos = Vector(xpos, ypos)

            self.start_distance = 2**32 #g-val
            self.heuristic = (self.end_pos - self._pos).get_mag() #h-val
            self.sum_val = 2**32 #f-val

            self.visited = False

            self.previous_node = None

            self.grid_pos = ((1/node_size) * Vector(xpos, ypos)).int()
            grid[self.grid_pos.x][self.grid_pos.y] = self

        #Use recursion to retrace path back to the start
        def retrace(self, path):
            # print(self.previous_node)
            if self.previous_node == None:
                return self

            path.append(self.previous_node.retrace(path))

            return self

        #Calculate start distance (f-val), heuristic (h-val), and sum val (g val)
        #   calculates from the relative node
        def set_values(self, relative_node):
            if self.previous_node == None:
                self.start_distance = 0
            else:
                self.start_distance = self.calculate_distance(relative_node)

            self.sum_val = self.start_distance + self.heuristic
            self.previous_node = relative_node

        #Returns distance from start to the given node
        def calculate_distance(self, relative_node):
            return (self._pos - relative_node._pos).get_mag() + relative_node.start_distance



    def __init__(self, population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces):
        super().__init__(population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces)

        #Create the population
        for i in range(population_size):
            self.vehicles.append(VehicleAStar(self.surface, self.camera, simulation_handler, xpos, ypos, 60, track_pieces, self))

        
        self.start_pos = self.start_piece.get_pos()
        self.end_pos = self.end_piece.get_pos()
        self.nodes = []
        self.assigned_nodes = [] #Nodes with sum values less than infinity
        self.node_size = 10

        node_grid = []
        for x in range(0, 1000):
            _row = []
            for y in range(0, 1000):
                _row.append(None)
            node_grid.append(_row)

        self.node_grid = node_grid

        self.start_node = PopulationAStar.Node(xpos, ypos, self.start_pos, self.end_pos, self.node_size, self.node_grid)
        self.start_node.set_values(self.start_node)
        self.start_node.previous_node = None
        self.nodes.append(self.start_node)
        self.assigned_nodes.append(self.start_node)

        self.create_nodes_on_track()

        path = []

        start_time = time.time()
        # self.find_path(path)

        path = self.find_path(path)
        self.path = []
        print(len(path))


        #Add every n nodes to path
        #   4 * (len(path)//4) so loop to closest multiple of 4 (cubic beziers work with 4 nodes each)
        for node_i in range(0, 4 * (len(path)//4)):
        # for node_i in range(0, 4 * (len(path)//4) + 1):

            #Every nth node is considered
            if node_i % 4 == 0 and path[node_i] != None:
                self.path.append(path[node_i])

        self.t = 0
        self.segment_count = len(path)//4

        print(time.time() - start_time)


    #Returns the node with the lowest f-cost
    def f_lowest(self):
        _lowest_val = 2**32
        _lowest_node = None

        #Find the lowest costing node
        for node in self.assigned_nodes:
            if node.visited == True: continue

            if node.sum_val < _lowest_val and node.visited == False:
                _lowest_node = node
                _lowest_val = node.sum_val

        return _lowest_node


    #Return all neighbours to the given node
    def get_neighbours(self, current_node):
        neighbours = []

        for node in self.nodes:
            if (node._pos - current_node._pos).get_mag() <= 1.45*self.node_size and node != current_node:
                neighbours.append(node)

        return neighbours

    #Populates the track with nodes to pathfind accross
    #   loops through each tack piece testing every possible node location
    def create_nodes_on_track(self):

        for piece in self.track_pieces:

            _top_bottom = (piece.bottom_right - piece.top_left).sign()            
            _top_left = (piece.top_left + piece._pos).int() - _top_bottom
            _bottom_right = (piece.bottom_right + piece._pos).int() - _top_bottom

            for y in range(_top_left.y, _bottom_right.y, _top_bottom.y * self.node_size):
                for x in range(_top_left.x, _bottom_right.x, _top_bottom.x * self.node_size):
                    
                    if piece.collision_point(Vector(x,y)):
                        _node = PopulationAStar.Node(x, y, self.start_pos, self.end_pos, self.node_size, self.node_grid)
                        self.nodes.append(_node)

    #Generalised form of a cubic bezier
    def cubic_bezier(self, p1,p2,p3,p4,t):
        return (-t**3 + 3*t**2 - 3*t + 1) * p1 + (3*t**3 - 6*t**2 + 3*t) * p2 + (-3*t**3 + 3*t**2) * p3 + (t**3) * p4

    #Return the x and y coordinates of the point fraction "t" along the found path
    def point_along_path(self, t):
        path = self.path
        _fraction = t % 1 #return the decimal part of the number "t"
        _whole = int(t) #get the whole number part
        
        #Get four nodes and interpolate
        if len(path[_whole*3:_whole*3+4]) == 4:
            #Return nodes for spline
            nodes = path[_whole*3:_whole*3+4]

            p1 = nodes[0]._pos
            p2 = nodes[1]._pos
            p3 = nodes[2]._pos
            p4 = nodes[3]._pos

            return self.cubic_bezier(p1, p2, p3, p4, _fraction)
        #When at the end of the path
        else:
            return path[-3]._pos

    #Returns the closest point on track to given point
    #   point : point to find closet point on graph to
    def get_closest_point(self, point):
        least_val = 2**32
        least_point = Vector(0,0)

        #Check all points along track to find the closest
        #   multiply by 10 so t can increment in 0.1
        for t in range(0, self.segment_count*10, 1):
            _t = t/10

            track_point = self.point_along_path(_t) 
            _dist = (point - track_point).get_mag()

            #When a closer point is found:
            if _dist < least_val:
                least_val = _dist
                least_point = track_point

        return least_point


    #Find the path using A* algorithm
    #   path_output : path of nodes is added to this list
    def find_path(self, path_output):
        # for i in range(500):
        while True:
            current_node = self.f_lowest()

            #If node has reached the end
            if current_node != None:
                if (self.end_pos - current_node._pos).get_mag() <= self.node_size:
                    current_node.retrace(path=path_output)
                    return path_output

            #Get nodes close to current node
            neighbours = self.get_neighbours(current_node)

            #Re-calculate the distances to each neighbouring node
            for neighbour in neighbours:
                if neighbour.visited == False:

                    _distance = neighbour.calculate_distance(current_node)

                    if _distance < neighbour.sum_val:
                        neighbour.set_values(current_node)

                        if neighbour not in self.assigned_nodes:
                            self.assigned_nodes.append(neighbour)

            #Mark node as visited
            current_node.visited = True

    def draw(self):
        super().draw()

        # for node in self.nodes:
        #     draw_col = (0, 0, 255)
        #     pygame.draw.rect(self.surface, draw_col, pygame.Rect(*self.to_screen_pos(node._pos).get_pos(), self.node_size, self.node_size))

        #     if node.visited == True:
        #         draw_col = (0, 255, 0)
        #         pygame.draw.rect(self.surface, draw_col, pygame.Rect(*self.to_screen_pos(node._pos).get_pos(), self.node_size, self.node_size))

        #     if node in self.path:
        #         draw_col = (255, 0, 0)
        #         pygame.draw.rect(self.surface, draw_col, pygame.Rect(*self.to_screen_pos(node._pos).get_pos(), self.node_size, self.node_size))

    def update(self, events):
        super().update(events)

        #Bezier curve test
        # self.t += 1/60 * self.speed
        
        # mx, my = pygame.mouse.get_pos()
        # self.test_vehicle._pos = self.test_vehicle.to_world_pos(Vector(mx, my))
        # self.test_vehicle.draw()
        # point = self.get_closest_point(self.test_vehicle._pos)
        # draw_circle(point, (255,0,255), self.surface, self.camera)


'''
Population of vehicles using A* pathfinding
'''
class PopulationGreedy(Population):
    #Node for pathfinding
    class Node:
        def __init__(self, xpos, ypos, start_pos, end_pos, node_size):
            self.start_pos = start_pos
            self.end_pos = end_pos
            self._pos = Vector(xpos, ypos)

            self.heuristic = (self.end_pos - self._pos).get_mag() #h-val

            self.visited = False

            self.previous_node = None
            
        #Use recursion to retrace path back to the start
        def retrace(self, path):
            # print(self.previous_node)
            if self.previous_node == None:
                return self

            path.append(self.previous_node.retrace(path))

            return self


        #Returns distance from start to the given node
        def calculate_distance(self, relative_node):
            return (self._pos - relative_node._pos).get_mag() + relative_node.start_distance



    def __init__(self, population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces):
        super().__init__(population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces)

        #Create the population
        for i in range(population_size):
            self.vehicles.append(VehicleAStar(self.surface, self.camera, simulation_handler, xpos, ypos, 60, track_pieces, self))

        
        self.start_pos = self.start_piece.get_pos()
        self.end_pos = self.end_piece.get_pos()
        self.nodes = []
        self.node_size = 10


        self.start_node = PopulationGreedy.Node(xpos, ypos, self.start_pos, self.end_pos, self.node_size)
        self.start_node.previous_node = None
        self.nodes.append(self.start_node)

        self.create_nodes_on_track()

        path = []

        start_time = time.time()
        # self.find_path(path)

        path = self.find_path(path)
        self.path = []
        print(len(path))


        #Add every n nodes to path
        #   4 * (len(path)//4) so loop to closest multiple of 4 (cubic beziers work with 4 nodes each)
        for node_i in range(0, 4 * (len(path)//4)):
        # for node_i in range(0, 4 * (len(path)//4) + 1):

            #Every nth node is considered
            if node_i % 4 == 0 and path[node_i] != None:
                self.path.append(path[node_i])

        self.t = 0
        self.segment_count = len(path)//4

        print(time.time() - start_time)


    #Returns the node with the lowest h-cost
    def h_lowest(self):
        _lowest_val = 2**32
        _lowest_node = None

        #Find the lowest costing node
        for node in self.assigned_nodes:
            if node.visited == True: continue

            if node.heuristic < _lowest_val and node.visited == False:
                _lowest_node = node
                _lowest_val = node.heuristic

        return _lowest_node


    #Return all neighbours to the given node
    def get_neighbours(self, current_node):
        neighbours = []

        for node in self.nodes:
            if (node._pos - current_node._pos).get_mag() <= 1.45*self.node_size and node != current_node:
                neighbours.append(node)

        return neighbours

    #Populates the track with nodes to pathfind accross
    #   loops through each tack piece testing every possible node location
    def create_nodes_on_track(self):

        for piece in self.track_pieces:
            #Get the bounding box of the track piece and the orientation
            _top_bottom = (piece.bottom_right - piece.top_left).sign()            
            _top_left = (piece.top_left + piece._pos).int() - _top_bottom
            _bottom_right = (piece.bottom_right + piece._pos).int() - _top_bottom

            #Loop through every possible location on top of track piece
            for y in range(_top_left.y, _bottom_right.y, _top_bottom.y * self.node_size):
                for x in range(_top_left.x, _bottom_right.x, _top_bottom.x * self.node_size):

                    #Check if the given point is inside the track's bounding box
                    if piece.collision_point(Vector(x,y)):
                        _node = PopulationAStar.Node(x, y, self.start_pos, self.end_pos, self.node_size)
                        self.nodes.append(_node)

    #Generalised form of a cubic bezier
    def cubic_bezier(self, p1,p2,p3,p4,t):
        return (-t**3 + 3*t**2 - 3*t + 1) * p1 + (3*t**3 - 6*t**2 + 3*t) * p2 + (-3*t**3 + 3*t**2) * p3 + (t**3) * p4

    #Return the x and y coordinates of the point fraction "t" along the found path
    def point_along_path(self, t):
        path = self.path
        _fraction = t % 1 #return the decimal part of the number "t"
        _whole = int(t) #get the whole number part
        
        #Get four nodes and interpolate
        if len(path[_whole*3:_whole*3+4]) == 4:
            #Return nodes for spline
            nodes = path[_whole*3:_whole*3+4]

            p1 = nodes[0]._pos
            p2 = nodes[1]._pos
            p3 = nodes[2]._pos
            p4 = nodes[3]._pos

            return self.cubic_bezier(p1, p2, p3, p4, _fraction)
        #When at the end of the path
        else:
            return path[-3]._pos

    #Returns the closest point on track to given point
    #   point : point to find closet point on graph to
    def get_closest_point(self, point):
        least_val = 2**32
        least_point = Vector(0,0)

        #Check all points along track to find the closest
        #   multiply by 10 so t can increment in 0.1
        for t in range(0, self.segment_count*10, 1):
            _t = t/10

            track_point = self.point_along_path(_t) 
            _dist = (point - track_point).get_mag()

            #When a closer point is found:
            if _dist < least_val:
                least_val = _dist
                least_point = track_point

        return least_point


    #Find the path using A* algorithm
    #   path_output : path of nodes is added to this list
    def find_path(self, path_output):
        visit_queue = PriorityQueue(64)
        visit_queue.enqueue((self.start_node, 0))
        path_output = []
        
        for i in range(500):
        #while True:
            current_node = visit_queue.dequeue()

            #If node has reached the end
            if current_node != None:
                if (self.end_pos - current_node._pos).get_mag() <= self.node_size:
                    current_node.retrace(path=path_output)
                    return path_output

            #Get nodes close to current node
            neighbours = self.get_neighbours(current_node)

            #Re-calculate the distances to each neighbouring node
            for neighbour in neighbours:
                if neighbour.visited == False:

                    visit_queue.enqueue((neighbour, 1/neighbour.heuristic))
                    neighbour.previous_node = current_node

            #Mark node as visited
            current_node.visited = True

    def draw(self):
        super().draw()

        # for node in self.nodes:
        #     draw_col = (0, 0, 255)
        #     pygame.draw.rect(self.surface, draw_col, pygame.Rect(*self.to_screen_pos(node._pos).get_pos(), self.node_size, self.node_size))

        #     if node.visited == True:
        #         draw_col = (0, 255, 0)
        #         pygame.draw.rect(self.surface, draw_col, pygame.Rect(*self.to_screen_pos(node._pos).get_pos(), self.node_size, self.node_size))

        #     if node in self.path:
        #         draw_col = (255, 0, 0)
        #         pygame.draw.rect(self.surface, draw_col, pygame.Rect(*self.to_screen_pos(node._pos).get_pos(), self.node_size, self.node_size))

    def update(self, events):
        super().update(events)

        #Bezier curve test
        # self.t += 1/60 * self.speed
        
        # mx, my = pygame.mouse.get_pos()
        # self.test_vehicle._pos = self.test_vehicle.to_world_pos(Vector(mx, my))
        # self.test_vehicle.draw()
        # point = self.get_closest_point(self.test_vehicle._pos)
        # draw_circle(point, (255,0,255), self.surface, self.camera)


'''
Population of vehicles using the wandering algorithm
'''
class PopulationWandering(Population):
    def __init__(self, population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces):
        super().__init__(population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces)

        #Create all vehicles
        for i in range(population_size):
            _vehicle = VehicleWandering(surface, camera, simulation_handler, xpos, ypos, 60, track_pieces, self)
            self.vehicles.append(_vehicle)




'''
Population of vehicles using a genetic algorithm
'''
class PopulationGeneticAlgorithm(Population):
    def __init__(self, population_size, surface, camera, simulation_handler, xpos, ypos, fps, ray_count, ray_length, track_pieces):
        super().__init__(population_size, surface, camera, simulation_handler, xpos, ypos, track_pieces)
        self.fps = fps
        self.ray_count = ray_count
        self.ray_length = ray_count
        self.generation_number = 0
        self.generation_duration = 7

        for i in range(population_size):
            _vehicle = VehicleGeneticAlgorithm(surface, camera, simulation_handler, xpos, ypos, fps, ray_count, ray_length, track_pieces, self)
            _vehicle.population_owner = self
            self.vehicles.append(_vehicle)

        #Assign selected vehicle
        #   selected vehicle is the vehicle the camera should follow
        if population_size <= 0:
            raise Exception("Error; Invalid population size")
        else:
            self.selected_vehicle = self.vehicles[0]

        self.fitnesses = PriorityQueue(population_size)

        self.frame_period = 1 / fps
        self.clock = 0

        self.best_fitness = 0
        self.best_vehicle = None

        #print(self.selected_vehicle.brain)
        # print(self.selected_vehicle.brain.forward(np.array([[100,], [10,], [30,]])) / ray_length)

        self.mutation_rate = simulation_handler.algorithm_settings["mutation-rate"]/100
        self.mutation_chance = simulation_handler.algorithm_settings["mutation-chance"]/100


    def update(self, events):
        super().update(events)

        #Reset generation every "generation_duration" seconds
        self.clock += self.frame_period

        if self.clock >= self.generation_duration + self.best_fitness / 10:
            self.clock = 0
            self.reset_generation()



    #Re-create the generation using the vehicle with the best fitness score
    def reset_generation(self):
        print("new generation", self.generation_number)
        self.generation_number += 1
        self.vehicle_no = self.generation_number

        for vehicle in self.vehicles:
            if vehicle.alive == True:
                vehicle.kill()

        #Get the best performing vehicle
        #   have chance to pick worse performing vehicles
        #chance of picking vehicle = probability ^ (vehicle index+1)
        for i in range(self.population_size):
            random_num = random.randint(0, 100)
            best_vehicle = self.fitnesses.dequeue()

            if random_num <= self.mutation_chance*100:
                break
        
        # if leaderboard[-1][0] > best_vehicle.time:
        #     leaderbaord[0] = (best_vehicle.time, )
        #     #bubble sort leaderboard

        # mutations = 2

        #Get vehicle's brain and copy
        #   need a copy otherwise it passes by reference, not value
        #   this will change the contents of the brain
        brain = best_vehicle.brain

        self.best_fitness = best_vehicle.fitness
        best_vehicle.reset_vehicle(*self._pos.get_pos())
        best_vehicle.alive = True
        self.best_vehicle = best_vehicle
        self.vehicles[0] = best_vehicle

        #Re-populate vehicle list
        for vehicle_i in range(1, self.population_size):
            weights = []
            biases = []

            #Increase variance in vehicle's abilities for fewer vehicles
            mutations = int(self.mutation_rate * (vehicle_i**2)/5)

            #Copy best vehicle's brain
            for weight in brain.weights:
                weights.append(weight.copy())
            for bias in brain.biases:
                biases.append(bias.copy())

            #Apply mutation
            #   gets random layer, then neuron, then weight to change
            #   do same for biases
            #Mutations = number of weights and biases selected and chose (e.g mutation val 2 = 2 weights and biases)
            for mutation_i in range(mutations):
                _layer_i = random.randint(0, len(weights)-1)

                #Mutate weights
                _shape = weights[_layer_i].shape
                _neuron_i =  (random.randint(0, _shape[0]-1), random.randint(0, _shape[1]-1))
                weights[_layer_i][_neuron_i[0], _neuron_i[1]] = np.random.rand() - 0.5

                #Mutate biases
                _shape = biases[_layer_i].shape
                _neuron_i =  (random.randint(0, _shape[0]-1), random.randint(0, _shape[1]-1))
                biases[_layer_i][_neuron_i[0], _neuron_i[1]] = np.random.rand() - 0.5

            #Apply brain and reset vehicle
            vehicle = self.vehicles[vehicle_i]
            vehicle.brain = Network(vehicle.net_sequence, weights=weights, biases=biases, gen_new=False)
            vehicle.reset_vehicle(*self._pos.get_pos())
            vehicle.alive = True

        self.fitnesses = PriorityQueue(self.population_size)
        

    #Add vehicle to fitness queue
    def add_fitness(self, vehicle, fitness):
        self.fitnesses.enqueue(vehicle, fitness)



'''
Ray object

Used to cast a ray in a given direction
    collision checks only appy to track objects (for now)

Parameters:
    direction : the direction the ray will travel (vector)

Methods:
    track_collision_check(track_piece) : performs a collision check with the given track and returns the points of intersection
    intersect(vec_pos, ved_dir) : returns the point of intersection with the given vector line positon and direction
'''
class Ray(SimulationObject):
    def __init__(self, surface, camera, xpos, ypos, direction):
        super().__init__(surface, camera, None, xpos, ypos)
        self.direction = direction #Direction (vector) of ray's travel
        self._end_pos = self._pos + 100 * self.direction.normalised()
        self.track_pieces = []


    #Sets the direction of the direction attribute
    #   direction : vector of direction (preferably normalised)
    def set_direction_vector(self, direction):
        self.direction = direction

    #Sets the direction of the direction attribute
    #   direction : angle of the vector
    def set_direction(self, direction):
        self.direction = Vector(math.cos(direction), math.sin(direction))

        if abs(self.direction.x) <= 0.01:
            self.direction.x = 0
        if abs(self.direction.y) <= 0.01:
            self.direction.y = 0

    def draw(self):
        #TEMPORARY
        #draw the ray and direction it travels
        self._screen_pos = self.to_screen_pos(self._pos)
        self._end_pos = self._pos + (100 * self.direction.normalised())
        _screen_end_pos = self.to_screen_pos(self._end_pos)
        pygame.draw.line(self.surface, (0,0,255), self._screen_pos.get_pos(), _screen_end_pos.get_pos())

        for points in self.tracks_collision_check():
            for point in points:
                _screen_int_point = self.to_screen_pos(point)
                pygame.draw.circle(self.surface, (0,255,0), _screen_int_point.int().get_pos(), 5)

    def update(self, events):
        super().update(events)

    #Adds track pieces to collision detection
    #   single_piece : a singular piece to add to the array
    #   multiple_pieces : adds multiple pieces to the collision check
    def add_track_pieces(self, single_piece=None, multiple_pieces=[]):
        if single_piece != None:
            self.track_pieces.append(single_piece)

        for piece in multiple_pieces:
            self.track_pieces.append(piece)

    #Returns all the collision points with all track pieces for ray
    def tracks_collision_check(self):
        out = []

        for piece in self.track_pieces:
            points = self.track_collision_check(piece)
            if len(points) != 0 :
                out.append(points)

        return out
    
    #Check for collision with a given track piece
    #   track_piece : piece to check for collision with this ray
    def track_collision_check(self, track_piece):
        _intersection_points = []

        #Loop through all sides of example piece
        #   solve for intersection of each segment of piece
        #   check if segment is in range
        for side in track_piece.sides:

            for vec_i in range(0, len(side)-1):
                vec_pos = side[vec_i] + track_piece.get_pos() #position of the vector
                vec_dir = side[vec_i+1] - side[vec_i] #the direction the vector travels

                if abs(vec_dir.y) < 0.01:
                    vec_dir.y = 0
                if abs(vec_dir.x) < 0.01:
                    vec_dir.x = 0

                x, y, lam = self.intersect(vec_pos, vec_dir)

                # if "straight" in track_piece.tags:
                #     print(abs(y - (vec_pos.y + 0.5 * vec_dir.y)))
                #     print(abs(0.5 * vec_dir.y))
                #     print((0 <= abs(y - (vec_pos.y + 0.5 * vec_dir.y)) <= abs(0.5 * vec_dir.y)))

                #Find distance from mid point of segment and intersection
                #   if intersection is within half of the segment length, it is on the segment
                #the abs() fixes the issue of negatives with the direction of the vector
                if (0 <= abs(x - (vec_pos.x + 0.5 * vec_dir.x)) <= abs(0.5 * vec_dir.x) and 0 <= abs(y - (vec_pos.y + 0.5 * vec_dir.y)) <= abs(0.5 * vec_dir.y)) or (Vector(x,y) - vec_pos).get_mag() < 1.5:
                    
                    #Check if point is in front of ray
                    #   if signs of directions are the same, they are in front
                    if self.direction.sign().get_pos() == (Vector(x, y) - self._pos).sign().get_pos():
                        _intersection_points.append(Vector(x, y))

                    #Check if point is in front of the ray
                    #   when x (x - self._pos.x) / self.direction.x is negative, it is behind
                    # if self.direction.x != 0:
                    #     if (x - self._pos.x) / self.direction.x > 0:
                    #         _intersection_points.append(Vector(x, y))
                    # elif self.direction.y != 0:
                    #     if (y - self._pos.y) / self.direction.y > 0:
                    #         _intersection_points.append(Vector(x, y))

            # print("\n\n\n", track_piece.tags)
            #     pygame.draw.circle(self.surface, (255,255,0), self.to_screen_pos(Vector(x,y)).get_pos(), 5)
            #     pygame.display.update()

            # if "curve-left" in track_piece.tags:
            #     time.sleep(5)

        return _intersection_points


    #Used to solve for collision points
    #   vec1 = col1 of matrix
    #   vec2 = col2 of matrix
    def determinant(self, vec1, vec2):
        return vec1.x * vec2.y - vec1.y * vec2.x

    #Find the intersection point of this ray and a given vector
    #Solves the system of vector equations of given vector and direction of travel of ray
    #   vec_pos : vector position to find collision for
    #   vec_dir : direction of vector to find collision for
    def intersect(self, vec_pos, vec_dir):

        #Solve for how far away the point of intersection is (lambda)
        #   makes use of determinant calculation and 2x2 matrix simultaneous equation
        try:
            lam = (self.determinant(vec_pos, self.direction) + self.determinant(self.direction, self._pos)) / self.determinant(self.direction, vec_dir)
        except ZeroDivisionError as error:
            # print("vec_pos", vec_pos)
            # print("vec_dir", vec_dir)
            # print("self.direction", self.direction)
            # print("self._pos", self._pos)
            # # raise ZeroDivisionError(error)
            lam = 2 ** 32 #when dividing by zero, make self "infinity"

        x = (lam * vec_dir.x) + vec_pos.x
        y = (lam * vec_dir.y) + vec_pos.y

        return x, y, lam

        



'''
Track Piece class

This is the parent class of all track pieces
    Needs to contain the code to detect collision from a sequence of vectors

Parameters:
    surface : the pygame surface to be drawn on
    xpos : the x position of the piece
    ypos : the y position of the piece
'''
class TrackPiece(SimulationObject):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos):
        super().__init__(surface, camera, simulation_handler, xpos, ypos)
        self.size = Vector(0, 0)

        #Each element is a list of vectors representing a "side"
        #   Each "side" will detect collision and be drawn
        #Note:positions stored are relative to the position of the track piece
        self.sides = []
        self._orig_sides = []

        self.top_left = Vector(0, 0)
        self.bottom_right = Vector(0, 0)
        self.bottom_left = Vector(self.top_left.x, self.bottom_right.y)

    #Returns the colour value of this piece
    def get_col(self):
        return self.simulation_handler.main_settings["track-colour"]

    #Returns a list containig tuple pairs of a given side
    #   index : the index of the side to get
    def get_side(self, index):
        return [(vec+ self._pos).get_pos() for vec in self.sides[index]]

    #Returns the actual coordinates of the end position
    def get_end_pos(self):
        return self._pos + self.end_pos

    def get_centre(self):
        x_pos = 0
        y_pos = 0
        total = 0
        for side in self.sides:
            for pos in side:
                x_pos += pos.x
                y_pos += pos.y
                total += 1

        return Vector(x_pos / total, y_pos / total)

    #Draws the track using the list of vectors
    def draw(self):
        # pygame.draw.circle(self.surface, (0,255,0), self.to_screen_pos(self._pos + self.get_centre()).get_pos(), 5)
        # pygame.draw.circle(self.surface, (0,255,0), self.to_screen_pos(self._pos + self.size).get_pos(), 5)
        # pygame.draw.circle(self.surface, (0,255,0), self.to_screen_pos(self._pos).get_pos(), 5)
        # pygame.draw.circle(self.surface, (255, 0,0), self.to_screen_pos(self._pos + self.end_pos).get_pos(), 5)

        for side_i in range(len(self.sides)):
            pygame.draw.lines(self.surface, self.get_col(), False, [self.to_screen_pos(vec+ self._pos).get_pos() for vec in self.sides[side_i]])
            # pygame.draw.lines(self.surface, (0,0,0), False, [(vec+ self._screen_pos).get_pos() for vec in self.sides[side_i]])

    #Sets the orientation of a track piece
    #   rotation : rotation in radians (positive is anti-clockwise)
    def set_direction(self, rotation):
        self.sides = self._orig_sides
        self.direction = rotation
        _rot_matrix = (Vector(math.cos(rotation), math.sin(rotation)), Vector(-math.sin(rotation), math.cos(rotation)))

        out = []
        for side in self.sides:
            new_side =[]
            for vec in side:
                new_side.append(vec.transformation(*_rot_matrix))

            out.append(new_side)

        self.sides = out
        self.end_pos = self.end_pos.transformation(*_rot_matrix)

        self.top_left = self.top_left.transformation(*_rot_matrix)
        self.bottom_right = self.bottom_right.transformation(*_rot_matrix)
        self.bottom_left = self.bottom_left.transformation(*_rot_matrix)


    #Returns if point is inside the track
    #   point : vector of point
    def collision_point(self, point):
        #Get cornders of bounding box
        _top_bottom = (self.bottom_right - self.top_left).sign() #direction piece is facing

        _top_left = (self.top_left + self._pos).int() - _top_bottom
        _bottom_right = (self.bottom_right + self._pos).int() - _top_bottom

        #Check if point lies in bounding box
        #   divide by "top bottom" to flip the inequality for when the top left is greater than the bottom right
        if _top_left.x/_top_bottom.x <= point.x/_top_bottom.x <= _bottom_right.x/_top_bottom.x and _top_left.y/_top_bottom.y <= point.y/_top_bottom.y <= _bottom_right.y/_top_bottom.y:
            return True

        return False

    
'''
Straight Piece class
This is a straight track piece
'''
class StraightLinePiece(TrackPiece):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos):
        super().__init__(surface, camera, simulation_handler, xpos, ypos)

        self.size = Vector(300, 100)
        self.sides = [
            [Vector(0, self.size.y/2), Vector(self.size.x, self.size.y/2)], 
            [Vector(0, -self.size.y/2), Vector(self.size.x, -self.size.y/2)]]

        self.end_pos = Vector(self.size.x, 0)
        self._orig_sides = self.sides.copy()

        self.top_left = Vector(0, -self.size.y/2)
        self.bottom_right = Vector(self.size.x, self.size.y/2)
        self.bottom_left = Vector(self.top_left.x, self.bottom_right.y)

        self.add_tag("straight")

'''
Start piece class
This denotes the start of a track
'''
class StartPiece(TrackPiece):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos):
        super().__init__(surface, camera, simulation_handler, xpos, ypos)

        self.size = Vector(300, 100)
        self.sides = [
            [Vector(self.size.x, self.size.y/2), Vector(0, self.size.y/2), Vector(0, -self.size.y/2), Vector(self.size.x, -self.size.y/2)]]
        
        self.start_coordinates = self._pos + 0.5 * self.size #Centre of piece
        self.end_pos = Vector(self.size.x, 0)

        self._orig_sides = self.sides.copy()

        self.top_left = Vector(0, -self.size.y/2)
        self.bottom_right = Vector(self.size.x, self.size.y/2)
        self.bottom_left = Vector(self.top_left.x, self.bottom_right.y)

        self.add_tag("start")

'''
End piece class
This denotes the end of a track
'''
class EndPiece(TrackPiece):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos):
        super().__init__(surface, camera, simulation_handler, xpos, ypos)

        self.size = Vector(300, 100)
        self.sides = [
            [Vector(0, self.size.y/2), Vector(self.size.x, self.size.y/2), Vector(self.size.x, -self.size.y/2), Vector(0, -self.size.y/2)]]
        
        self.end_coordinates = self._pos + 0.5 * self.size #Centre of piece
        self.end_pos = Vector(self.size.x, 0)

        self._orig_sides = self.sides.copy()

        self.top_left = Vector(0, -self.size.y/2)
        self.bottom_right = Vector(self.size.x, self.size.y/2)
        self.bottom_left = Vector(self.top_left.x, self.bottom_right.y)

        self.add_tag("end")

'''
Curved track piece
This will bend round corners

Parameters:
    rotation : the orientation of the piece (radian)
'''
class CurvePieceRight(TrackPiece):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos):
        super().__init__(surface, camera, simulation_handler, xpos, ypos)

        self.size = Vector(300, 300)
        w = self.size.x / 18
        h = self.size.y / 18
        self.sides = [
            [Vector(0, -3*h), Vector(5*w, -2*h), Vector(8*w, -1*h), Vector(11*w, 1*h), Vector(14*w, 4*h), Vector(16*w, 7*h), Vector(17*w, 10*h), Vector(18*w, 15*h)],
            [Vector(0, 3*h), Vector(4*w, 4*h), Vector(7*w, 6*h), Vector(9*w, 8*h), Vector(11*w, 11*h), Vector(12*w, 15*h)]]

        self._orig_sides = self.sides.copy()

        self.end_pos = Vector(15*w, 15*h)

        self.top_left = Vector(0, -3*h)
        self.bottom_right = Vector(18*w, 15*h)
        self.bottom_left = Vector(self.top_left.x, self.bottom_right.y)

        self.add_tag("curve-right")


    #Returns if collision point lies within the track arcs
    def collision_point(self, point):
        _top_bottom = (self.bottom_right - self.top_left).sign()
        _top_left = (self.top_left + self._pos).int() - _top_bottom
        _bottom_right = (self.bottom_right + self._pos).int() - _top_bottom 
        _bottom_left = (self.bottom_left + self._pos).int()

        #Get the distance away from the origin of the arc
        _dist = (point - _bottom_left).get_mag()

        #Check if point lies in radius between the two arcs radius
        #   width of track = 100, radius of greatest arc = 300
        if _top_left.x/_top_bottom.x <= point.x/_top_bottom.x <= _bottom_right.x/_top_bottom.x and 300 - 100 <= _dist <= 300:
            return True
        else:
            return False


    # def draw(self):
    #     super().draw()
    #     _top_left = (self.top_left + self._pos).int()
    #     _bottom_right = (self.bottom_right + self._pos).int()

    #     _bottom_left = Vector(_top_left.x, _bottom_right.y)

    #     pygame.draw.circle(self.surface, (255,0,0), self.to_screen_pos(_top_left).get_pos(), 4)
    #     pygame.draw.circle(self.surface, (0,255,0), self.to_screen_pos(_bottom_right).get_pos(), 4)
    #     pygame.draw.circle(self.surface, (255,255,0), self.to_screen_pos(_bottom_left).get_pos(), 4)
                

'''
Curved track piece
Flipped verion of the curve right
'''
class CurvePieceLeft(CurvePieceRight):
    def __init__(self, surface, camera, simulation_handler, xpos, ypos):
        super().__init__(surface, camera, simulation_handler, xpos, ypos)

        self.size = Vector(300, 300)

        #Vertically flip the right piece
        _sides = []
        for side in self.sides:
            _side = []

            for pos in side:
                _side.append(pos.transformation(Vector(1, 0), Vector(0, -1)))

            _sides.append(_side)

        self.sides = _sides
        self.end_pos = self.end_pos.transformation(Vector(1, 0), Vector(0, -1))

        self.top_left = self.top_left.transformation(Vector(1, 0), Vector(0, -1))
        self.bottom_right = self.bottom_right.transformation(Vector(1, 0), Vector(0, -1))
        self.bottom_left = self.bottom_left.transformation(Vector(1, 0), Vector(0, -1))

        self._orig_sides = self.sides.copy()

        self.tags = ["curve-left"]


