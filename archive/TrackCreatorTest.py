import pygame
from SimulationObjects import *
from UIElements import Layer
from CustomStructures import *
from CreateUI import TrackCreatorUI
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
camera.set_pos(100 * 3, 100 * 3)

#Create layers
root_layer = Layer("root")
track_creator_layer = Layer("track creator layer")

track_creator = TrackCreator(win, camera, track_creator_layer, "Test Track2")

#Creator Layer
track_creator_layer.set_visibility(True)

track_creator_ui = TrackCreatorUI(win, track_creator_layer)
track_creator_ui.create_UI(track_creator)
track_creator_ui.commit()
# track_creator.load_track("TestTrack.txt", "./tracks/")

track_creator_layer.add_objects(single_obj = camera)


root_layer.add_child(track_creator_layer)
root_layer.set_visibility(True)



running = True #Run pygame loop
while running:

    clock.tick(FPS)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # print("Mouse down")
            # print(pygame.mouse.get_pos())
            pass

        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_SPACE:
                track_creator.undo_piece()
    
    mouse_pos = pygame.mouse.get_pos()

    win.fill(bgcol)

    root_layer.update(events)
    root_layer.draw()

    camera.test_ray.track_pieces = []
    camera.test_ray.add_track_pieces(multiple_pieces=track_creator.track_pieces.get_list())
    
    pygame.display.update()

pygame.quit()

