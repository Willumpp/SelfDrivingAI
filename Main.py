
import pygame
from CreateUI import *
from UIElements import *
from CustomStructures import Vector
from FileHandlers import *
import TrackCreator as tc
import SimulationObjects as so
import Simulation as si

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
FPS = 60

pygame.font.init()
win = pygame.display.set_mode(SCREEN_SIZE.get_pos())
pygame.display.set_caption("Program")
clock = pygame.time.Clock()

bgcol = [COLOURS["bg-lightgreen"]] #as a list so it can be passed by reference

#Create databases
users_database = Database("Users.db", "./databases/")
# users_database.remove_entry("Tracks", user_id=4)

try:
    users_database.create_table("Logins", id=int, Username=str, Password=str)
except Exception:
    pass



#Create layers
root_layer = Layer("root")


login_layer = Layer("login")
create_user_layer = Layer("create new user")


main_menu_layer = Layer("main menu")
select_track_layer = Layer("main menu select track")
menu_track_creator_layer = Layer("main menu track creator")
settings_menu_layer = Layer("main menu settings")

select_track_select_layer = Layer("main menu select track select")
physics_settings_layer = Layer("select track physics settings")
algorithm_settings_layer = Layer("select track algorithm settings")


simulation_layer = Layer("simulation")
track_creator_layer = Layer("track creator")


#-----Create objects

#Create camera
camera = so.Camera(win, SCREEN_SIZE.x/2, SCREEN_SIZE.y/2)


simulation_object = si.Simulation(win, camera, simulation_layer)

track_creator_object = tc.TrackCreator(win, camera, track_creator_layer, simulation_object, "")

track_creator_layer.add_objects(obj_list=track_creator_object.track_pieces.get_list())
track_creator_layer.add_objects(single_obj=camera)
track_creator_layer.add_objects(single_obj=track_creator_object)






#----------Main Menu layer
main_menu_layer.set_visibility(False)

main_menu = MainMenu(win, main_menu_layer)
main_menu.create_UI()
main_menu.commit()

#Settings menu:
settings_menu_layer.set_visibility(False)

settings_menu = MainMenuSettings(win, settings_menu_layer, simulation_object)
settings_menu.create_UI()
settings_menu.commit()

main_menu_layer.add_child(settings_menu_layer)


#-----Track Creator menu
menu_track_creator_layer.set_visibility(False)

main_menu_track_creator = MainMenuTrackCreator(win, menu_track_creator_layer)
main_menu_track_creator.create_UI(root_layer, "track creator layer", bgcol, track_creator_object)
main_menu_track_creator.commit()

main_menu_layer.add_child(menu_track_creator_layer)


#"Create new user" layer
create_user_layer.set_visibility(False)

create_new_user_menu = CreatenewUserMenu(win, create_user_layer, users_database)
create_new_user_menu.create_UI("login")
create_new_user_menu.commit()



#----Select track menu
select_track_layer.set_visibility(False)

select_track = MainMenuSelectTrack(win, select_track_layer)

main_menu_layer.add_child(select_track_layer)

#Select track select layer
select_track_select_layer.set_visibility(False)

select_track_select = MainMenuSelectTrackSelect(win, select_track_select_layer)
select_track_select.create_UI("select track physics settings")
select_track_select.commit()

#Physics settings layer
physics_settings_layer.set_visibility(False)

physics_settings = SelectTrackPhysicsSettings(win, physics_settings_layer)
physics_settings.create_UI("main menu select track select", "select track algorithm settings")
physics_settings.commit()

#Algorithm settings layer
algorithm_settings_layer.set_visibility(False)

#Algorithm settings header layer
#   this is used to store all the sub-layers for the algorithm settings
algorithm_settings_layer.set_visibility(False)
algorithm_settings_header_layer = Layer("select track algorithm settings header")
algorithm_settings_layer.add_child(algorithm_settings_header_layer)


#Astar pathfining settings
algorithm_settings_astar_layer = Layer("algorithm settings astar")
algorithm_settings_astar_layer.set_visibility(False)
algorithm_settings_header_layer.add_child(algorithm_settings_astar_layer)

astar_settings = AlgorithmSettingsAstar(win, algorithm_settings_astar_layer)
astar_settings.create_UI()
astar_settings.commit()

#Genetic algorithm settings
algorithm_settings_genetic_layer = Layer("algorithm settings genetic")
algorithm_settings_genetic_layer.set_visibility(False)
algorithm_settings_header_layer.add_child(algorithm_settings_genetic_layer)

genetic_algorithm_settings = AlgorithmSettingsGenetic(win, algorithm_settings_genetic_layer)
genetic_algorithm_settings.create_UI()
genetic_algorithm_settings.commit()

#Obstacle avoidance settings
algorithm_settings_obstacle_layer = Layer("algorithm settings obstacles")
algorithm_settings_obstacle_layer.set_visibility(False)
algorithm_settings_header_layer.add_child(algorithm_settings_obstacle_layer)

obstacle_avoidance_settings = AlgorithmSettingsObstacles(win, algorithm_settings_obstacle_layer)
obstacle_avoidance_settings.create_UI()
obstacle_avoidance_settings.commit()

#Greedy best first search settings
algorithm_settings_greedy_layer = Layer("algorithm settings greedy")
algorithm_settings_greedy_layer.set_visibility(False)
algorithm_settings_header_layer.add_child(algorithm_settings_greedy_layer)

greedy_algorithm_settings = AlgorithmSettingsGreedy(win, algorithm_settings_greedy_layer)
greedy_algorithm_settings.create_UI()
greedy_algorithm_settings.commit()


algorithm_settings = SelectTrackAlgorithmSettings(win, algorithm_settings_layer, simulation_object, root_layer, select_track_select, track_creator_object, bgcol, physics_settings)
algorithm_settings.create_UI("select track physics settings", algorithm_settings_header_layer, astar_settings, genetic_algorithm_settings, obstacle_avoidance_settings, greedy_algorithm_settings)
algorithm_settings.commit()

select_track_layer.add_child(algorithm_settings_layer)
select_track_layer.add_child(physics_settings_layer)
select_track_layer.add_child(select_track_select_layer)




#-----Track creator layer
track_creator_layer.set_visibility(False)

track_creator_ui = TrackCreatorUI(win, track_creator_layer, bgcol)
track_creator_ui.create_UI(track_creator_object)
track_creator_ui.commit()



#-----Simulation Layer
simulation_layer.set_visibility(False)

simulation_ui = SimulationUI(win, simulation_layer, bgcol, simulation_object)
simulation_ui.create_UI()
simulation_ui.commit()



#---------Login menu layer
login_layer.set_visibility(True)

#Create login menu UI elements
login_menu = LoginMenu(win, login_layer, users_database, main_menu, settings_menu, track_creator_ui, select_track_select, algorithm_settings)
login_menu.create_UI("create new user", bgcol, main_menu_layer) #"Create new user" navigates to "create user" layer
login_menu.commit() #Add to "login layer"



#Root layer
root_layer.add_child(create_user_layer)
root_layer.add_child(login_layer)
root_layer.add_child(main_menu_layer)
root_layer.add_child(simulation_layer)
root_layer.add_child(track_creator_layer)




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

    #Fill background to login menu light blue    
    win.fill(bgcol[0])

    #Fill background to login menu light green    
    # win.fill(COLOURS["bg-lightgreen"])

    root_layer.update(events)
    root_layer.draw()

    
    pygame.display.update()

pygame.quit()

