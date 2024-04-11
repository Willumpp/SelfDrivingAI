import pygame
from SimulationObjects import *
from UIElements import Layer
from FileHandlers import *
from TrackCreator import TrackCreator
import math


COLOURS = {
    "bg-lightblue": (214, 220, 229),
    "bg-lightgreen":(216, 235, 205),
    "white":        (255,255,255),
    "txt-red":      (192, 0, 0),
    "txt-blue":     (68, 114, 196),
    "black":        (0, 0, 0),
    "darkgrey":     (64, 64, 64),
    "grey":         (175, 171, 171),
    "lightgrey":    (242, 242, 242),
}

bgcol = (255,255,255)

#Only run as a test
pygame.init()

#Aspect ratio 16:9
# 1220 x 630
SCREEN_SIZE = Vector(1280, 720)
FPS = 60

pygame.font.init()
win = pygame.display.set_mode(SCREEN_SIZE.get_pos())
pygame.display.set_caption("Program")
clock = pygame.time.Clock()
camera = Camera(win, SCREEN_SIZE.x//2, SCREEN_SIZE.y//2)

#Create layers
root_layer = Layer("root")
simulation_layer = Layer("simulation layer")

track_creator = TrackCreator(win, camera, simulation_layer, "Square")
track_creator.load_track("Meander.txt", "./tracks/")
track_pieces = track_creator.get_pieces().get_list()

#Simulation Layer
simulation_layer.set_visibility(True)
root_layer.add_child(simulation_layer)

root_layer.set_visibility(True)

# population = PopulationGeneticAlgorithm(20, win, camera, 100, 0, FPS, 3, 500, track_pieces)

#population = PopulationWandering(1, win, camera, 100, 0, track_pieces)
population = PopulationAStar(1, win, camera, 100, 0, track_pieces)
camera.set_pos(100 * 3, 100 * 3)
camera.test_ray.add_track_pieces(multiple_pieces=track_pieces)

simulation_layer.add_objects(obj_list = track_pieces)
simulation_layer.add_objects(single_obj = camera)
simulation_layer.add_objects(single_obj = population)
simulation_layer.add_objects(obj_list = population.vehicles)


# simulation_layer.add_objects(single_obj = test_ray)

running = True #Run pygame loop
while running:

    clock.tick(FPS)
    

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pass

        if event.type == pygame.KEYDOWN:
            # if event.key == pygame.K_SPACE:
            #     population.create_nodes_on_track()
            pass
    
    mouse_pos = pygame.mouse.get_pos()

    win.fill(bgcol)
    

    root_layer.update(events)
    root_layer.draw()
    
    pygame.display.update()

pygame.quit()

