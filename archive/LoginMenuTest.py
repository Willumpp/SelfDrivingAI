
import pygame
from CreateUI import *
from UIElements import *
from CustomStructures import Vector

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


#Only run as a test
pygame.init()

#Aspect ratio 16:9
# 1220 x 630
SCREEN_SIZE = Vector(1280, 720)
FPS = 30

pygame.font.init()
win = pygame.display.set_mode(SCREEN_SIZE.get_pos())
pygame.display.set_caption("Login menu")
clock = pygame.time.Clock()

elements = []

#Converts the powerpoint coordinates to on-screen coordinates
#   Returns a vector
def ptc(x, y):
    return Vector(x/33.87 * SCREEN_SIZE.x, y/19.05 * SCREEN_SIZE.y)

def placeholder():
    print("placeholder")

def get_element(tag, elements):
    output =[]
    for element in elements:
        if element.get_tag() == tag:
            output.append(element)

    return output

def display_data():
    print("Username:", get_element("username field", elements)[0].get_text())
    print("Password:", get_element("password field", elements)[0].get_text())


#Login menu layer
login_layer = Layer("login")
login_layer.set_visibility(True)

#Create login menu UI elements
login_menu = LoginMenu(win, login_layer)
login_menu.create_UI("create new user") #"Create new user" navigates to "create user" layer
login_menu.commit() #Add to "login layer"

#"Create new user" layer
create_user_layer = Layer("create new user")
create_user_layer.set_visibility(False)

create_new_user_menu = CreatenewUserMenu(win, create_user_layer)
create_new_user_menu.create_UI("login")
create_new_user_menu.commit()

#Root layer
root_layer = Layer("root")
root_layer.add_child(create_user_layer)
root_layer.add_child(login_layer)






running = True #Run pygame loop
while running:

    clock.tick(FPS)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Mouse down")
            print(pygame.mouse.get_pos())

    #Fill background to login menu light blue    
    win.fill(COLOURS["bg-lightblue"])
    #Fill background to login menu light green    
    # win.fill(COLOURS["bg-lightgreen"])


    root_layer.update(events)
    root_layer.draw()

    
    pygame.display.update()

pygame.quit()

