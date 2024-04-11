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


#Simulation Layer
simulation_layer.set_visibility(True)
root_layer.add_child(simulation_layer)

root_layer.set_visibility(True)


camera.set_pos(100 * 3, 100 * 3)

simulation_layer.add_objects(single_obj = camera)

def draw_circle(inp, col):
    pygame.draw.circle(win, col, camera.to_screen_pos(inp).get_pos(), 5)


p1 = Vector(0, 0)
p2 = Vector(0, 500)
p3 = Vector(500, 500)
p4 = Vector(500, 0)

t = 0

running = True #Run pygame loop
while running:

    clock.tick(FPS)
    

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # win.fill(bgcol)

    t += 100/FPS
    _t = (int(t) % 100)/100

    #Lerp between points
    draw_circle(p1, (255,0,0)) #p1 (red)
    draw_circle(p2, (0,0,255)) #p2 (blue)
    draw_circle(p3, (0,255,0)) #p3 (green)
    draw_circle(p4, (0,255,255)) #p4 (cyan)

    draw_circle(cubic_bezier(p1, p2, p3, p4, _t), (255, 0, 255)) #output (magenta)


    root_layer.update(events)
    root_layer.draw()
    
    pygame.display.update()

pygame.quit()

