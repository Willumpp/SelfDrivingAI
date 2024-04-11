from UIElements import *
from CustomStructures import Vector
from StructureAlgorithms import bubble_sort
import FileHandlers as fh
import hashlib
import colorsys

SCREEN_SIZE = Vector(1280, 720)
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

def ptc(x, y):
    return Vector(x/33.87 * SCREEN_SIZE.x, y/19.05 * SCREEN_SIZE.y)

def placeholder():
    print("placeholder")

def placeholder2():
    print("placeholder2")
    

'''
UI Creator class
Anything that creates a UI - making use of the "UIelements.py" file - should be inherited from here

Parameters:
    surface : the pygame surface to draw UI elements onto
    parent_layer : the layer OBJECT the UI elements will be created onto

Methods:
    create_UI(button_functions) : this populates the "elements" list will all the UI element objects
        button functions are keyword arguments for changing the functions for buttons in navigation
'''
class UICreator:
    def __init__(self, surface, parent_layer=None):
        self.elements = []
        self.surface = surface

        self.parent_layer = parent_layer

    #Creates all UI objects 
    #   button_functions : the functions which the buttons will be calling
    def create_UI(self, **button_functions):
        print("this is a placeholder; this needs to be changed")
        print(kwargs)
        pass
    
    #Adds the UI elements to the "parent layer"
    def commit(self):
        if self.parent_layer == None:
            raise Exception("Error; parent layer has not been specified")

        self.parent_layer.add_UIelements(element_list=self.elements)

    def get_elements(self):
        return self.elements

    #Get an element from layer
    #   tag : tag of element to get
    def get_element(self, tag):
        for element in self.elements:
            if element.get_tag() == tag:
                return element

        raise Exception(f"Error; Element '{tag}' is has not been found")


'''
Login menu 
This is the first menu the user sees and allows the user to log into their account
'''
class LoginMenu(UICreator):
    def __init__(self, surface, layer, users_database, main_menu_ui, main_menu_settings_ui, track_creator_ui, track_selection_ui, algorithm_settings_ui):
        super().__init__(surface, layer)
        self.users_database = users_database
        self.main_menu_ui = main_menu_ui
        self.main_menu_settings_ui = main_menu_settings_ui
        self.track_creator_ui = track_creator_ui
        self.track_selection_ui = track_selection_ui
        self.algorithm_settings_ui = algorithm_settings_ui
        self.user_id = 0
        self.results_database = None #This changes when the user logs in

    def display_invalid_password(self):
        self.parent_layer.clear_ui()
        elements = self.elements
        win = self.surface
        
        #Login attempt failure text box:
        _pos = ptc(13.25, 11.65)
        _size = ptc(8.09, 0.86)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Username or password does not exist")
        elements.append(_element)

        self.commit()

    #bgcol : list to pass by reference
    def confirm_button(self, bgcol, main_menu_layer):
        username_field = self.get_element("username field")
        password_field = self.get_element("password field")

        username_text = username_field.get_text()
        password_text = password_field.get_text()

        user = self.users_database.get_contents("Logins", Username=username_text)

        if len(user) == 0:
##            print("Username does not exist")
            self.display_invalid_password()
            return
        
        password_hash = hashlib.sha256(password_text.encode()).hexdigest()

##        print("password text", password_text)
        #index 2 = password
        if password_hash != user[0][2]:
##            print("Invalid password")
##            print("hashed password text", password_hash)
##            print("stored hash", user[0][2])
            self.display_invalid_password()
            return
    

        self.parent_layer.set_visibility(False) #set the login menu to hidden

        #Get the main menu from name
        # main_menu = self.parent_layer.parent_layer.find_layer(main_menu_layer)[1].tail()
        main_menu = main_menu_layer
        main_menu.set_visible(True)
        self.main_menu_ui.get_element("Username Text").set_text(username_text) #Set "Username" in main menu

        # self.parent_layer.switch_layer(main_menu_layer, True)
        bgcol[0] = COLOURS["bg-lightblue"]

        #"Vehicle Colour: text input r", i"Vehicle Colour: text input g"), "Vehicle Colour: text input b"

        def hex_to_rgb(hex):
            val = hex.replace("#", "")
            rgb = (int(val[:2], 16), int(val[2:4], 16), int(val[4:6], 16))
            return rgb
        
        #Apply stored user settings
        user_id = user[0][0]
        self.user_id = user_id
        settings = self.users_database.get_contents("UserSettings", id=user_id)[0]
        headings = ["Vehicle Colour:", "Track Colour:", "Rock Colour:", "Tree Colour:", "Offroad Colour:"]
        settings_output = {}

        for heading_i in range(len(headings)):
            heading = headings[heading_i]
            colour = settings[1+heading_i] #Colour is hex value so needs converting
            r, g, b = hex_to_rgb(colour)
            #Apply settings to output
            settings_output[heading + " text input r"] = r
            settings_output[heading + " text input g"] = g
            settings_output[heading + " text input b"] = b
        
        #Apply settings to menu
        self.main_menu_settings_ui.set_settings(settings_output)
        self.main_menu_settings_ui.user_id = user_id
        self.main_menu_settings_ui.users_database = self.users_database

        #Change attributes in track creator ui
        self.track_creator_ui.user_id = user_id
        self.track_creator_ui.users_database = self.users_database


        #Import user created tracks
        #   uses the track selection ui to add the elements
        if self.users_database != None:
            tracks = self.users_database.get_contents("Tracks", user_id=self.user_id)
            win = self.surface

            for track_i in range(len(tracks)):
                track_name = tracks[track_i][3]
                track_path = tracks[track_i][2]

                #Create button at given coordinates on grid
                _pos = ptc(7.57 + (track_i % 5) * 5, 7.26 + (track_i//5) * 3.4)
                _size = ptc(3.76, 2.26)
                _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.track_selection_ui.track_button, args=(track_name, track_path))
                _element.set_text(track_name)
                _element.bgcol = COLOURS["darkgrey"]
                _element.fgcol = COLOURS["white"]
                _fnt = pygame.font.SysFont("Comic Sans MS", 24)
                _element.set_font(_fnt, align="centre")
                self.track_selection_ui.elements.append(_element)

            self.track_selection_ui.parent_layer.clear_ui()
            self.track_selection_ui.commit()

        #Get the results database
        results_database_info = self.users_database.get_contents("Results", id=user_id)[0]

        self.results_database = fh.Database(file_name=results_database_info[1], file_path=results_database_info[2])
        self.algorithm_settings_ui.results_database = self.results_database


    #Create_new_user_layer : layer name of the menu the "Create new user" button navigates to
    #main_menu_layer : object
    def create_UI(self, create_new_user_layer, bgcol, main_menu_layer):
        elements = self.elements
        win = self.surface

        #Username Field:
        _pos = ptc(12.13, 6.99)
        _size = ptc(9.6, 1.19)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "Username", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("username field")
        #_element.set_text("TestUser8") #TEMPORARY
        elements.append(_element)

        #Password Field:
        _pos = ptc(12.13, 9.76)
        _size = ptc(9.6, 1.19)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "Password: ******", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("password field")
        #_element.set_text("!Qwert1") #TEMPORARY
        _element.hide_text = True
        elements.append(_element)
        
        #"Confirm" button
        _pos = ptc(15.49, 13.21)
        _size = ptc(2.88, 1.19)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.confirm_button, args=(bgcol, main_menu_layer))
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18), align="centre")
        _element.set_text("Confirm")
        elements.append(_element)

        #"Create new user" button
        _pos = ptc(14.03, 17.71)
        _size = ptc(5.8, 1.03)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.parent_layer.switch_layer, args=(create_new_user_layer, True) )
        _element.set_text("Create New User")
        _element.fgcol = COLOURS["txt-blue"]
        _element.bgcol = COLOURS["bg-lightgreen"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 24, italic=True)
        #_fnt.underline = True
        _element.set_font(_fnt, align="centre")
        _element.draw_border = False
        elements.append(_element)

        #"Reveal password" button
        _pos = ptc(20.26, 9.8)
        _size = ptc(1.16, 1.16)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, placeholder)
        _element.draw_border = False
        _element.set_image("./sprites/HiddenPassword.png")
        elements.append(_element)

'''
User creation menu 
This is navigated from the login menu
This allows the user to create a new account
'''
class CreatenewUserMenu(UICreator):
    def __init__(self, surface, layer, users_database):
        super().__init__(surface, layer)
        self.users_database = users_database

    def invalid_user_message(self, message):
        self.parent_layer.clear_ui()
        elements = self.elements
        win = self.surface
        
        #Login attempt failure text box:
        _pos = ptc(13.25, 11.65)
        _size = ptc(8.09, 0.86)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text(message)
        elements.append(_element)

        self.commit()

    #Validate a given username
    #   username : username to validate
    def validate_username(self, username):
        if len(username) > 16 or len(username) < 4:
            return False

        return True

    #Validate a given password
    #   password : password to validate
    #returns True/False if allowed/not allowed
    def validate_password(self, password):

        #Used to check if password has a character with ascii code in given range (inclusive)
        def has_ASCII(inp, _min, _max):
            for char_i in range(len(inp)):
                
                #ord(char) converts to ascii
                if _min <= ord(inp[char_i]) <= _max:
                    return True
                
            return False

        if len(password) > 16 or len(password) < 6:
            return False

        #Has at least one capital
        #   ASCII for A is 65, Z is 90
        if has_ASCII(password, 65, 90) == False:
            return False

        #Has at least one number
        #   ASCII for 0 is 48, 9 is 57
        if has_ASCII(password, 48, 57) == False:
            return False

        #Contains a "special character"
        #   character which isnt a number, lower or upper case letter
        _found= False
        for char_i in range(len(password)):
            _code = ord(password[char_i])
            
            #if charcter is number or capital or lowercase == False
            if (48 <= _code <= 57 or 65 <= _code <= 90 or 97 <= _code <= 122) == False:
                _found = True

        if _found == False:
            return False

        #print("Valid password")
        #If all checks succeed:
        return True
    
    #Called by the "create" button in the "create new user" menu
    def create_user_button(self):
        username_field = self.get_element("create username field")
        password_field = self.get_element("create password field")
        confirm_password_field = self.get_element("create confirm password field")
        error_text = self.get_element("error message")

        username_text = username_field.get_text()
        password_text = password_field.get_text()
        confirm_password_text = confirm_password_field.get_text()

        _out = ""
        if self.validate_username(username_text) == False:
            _out += "Invalid Username. Username must be greater than 3 characters and less than 17 characters. "
            error_text.set_text(_out)
            return

        if self.validate_password(password_text) == False:
            _out += "Invalid Password\Password must be greater than 5 characters and less than 17 characters. "
            _out += "Password must contain a capital letter. "
            _out += "Password must contain a number. "
            _out += "Password must contain a special character. "
            error_text.set_text(_out)
            return

        if password_text != confirm_password_text:
            _out += "Passwords do not match. "
            error_text.set_text(_out)
            return


        #Add username and password to database
        users = self.users_database.execute_sql("SELECT id, Username FROM Logins")

        #Check if username exists
        for user in users:
            if user[1] == username_text:
                _out += "Username already exists. "
                error_text.set_text(_out)
                return

        password_hash = hashlib.sha256(password_text.encode()).hexdigest()
        
        #Add user to logins database
        highest_id = self.users_database.highest_entry("Logins", "id") #get the highest id
        next_id = highest_id + 1

        self.users_database.add_entry("Logins", id=next_id, Username=username_text, Password=password_hash)
        self.users_database.add_entry("UserSettings", id=next_id, vehicle_colour="#FF0000", track_colour="#000000", rock_colour="#FFFFFF", tree_colour="#FFFFFF", offroad_colour="#FFFFFF") #Apply default values to user settings

        #Create the results database
        results_database = fh.Database("Results"+str(next_id)+".db", "./databases/")
        self.users_database.add_entry("Results", id=next_id, database_name="Results"+str(next_id)+".db", database_dir="./databases/")

        results_database.create_table("Tests", id=int, test=int, maximum_velocity=int, acceleration_magnitude=int, deceleration_magnitude=int, turn_velocity=float, vehicle_width=int, vehicle_height=int, track_name=str)
        results_database.create_table("Vehicles", id=int, test_id=int, vehicle_no=int, completion_time=float, distance_travelled=int, errors_made=int)
        results_database.create_table("AStarTests", test_id=int, follow_strength=int)
        results_database.create_table("WanderingTests", test_id=int, follow_strength=int)
        results_database.create_table("GeneticAlgTests", test_id=int, population_size=int, mutation_rate=int, mutation_chance=int, existing_network=int)

        

    #login_menu_layer : layer name which the "login menu" button navigates to
    def create_UI(self, login_menu_layer):
        elements = self.elements
        win = self.surface
        
        #Username Field:
        _pos = ptc(12.13, 6.99)
        _size = ptc(9.6, 1.19)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "Username", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("create username field")
        elements.append(_element)

        #"Password" field:
        _pos = ptc(12.13, 9.76)
        _size = ptc(9.6, 1.19)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "Password", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("create password field")
        elements.append(_element)

        #"Confirm Password" field:
        _pos = ptc(12.13, 11.64)
        _size = ptc(9.6, 1.19)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "Confirm Password", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("create confirm password field")
        elements.append(_element)

        #"Create" button
        _pos = ptc(15.49, 13.51)
        _size = ptc(2.88, 1.19)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.create_user_button)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18), align="centre")
        _element.set_tag("create user button")
        _element.set_text("Create")
        elements.append(_element)

        #"Login" button
        _pos = ptc(15.92, 17.8)
        _size = ptc(2.1, 1.04)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.parent_layer.switch_layer, args=(login_menu_layer, True))
        _element.set_text("Login")
        _element.fgcol = COLOURS["txt-blue"]
        _element.bgcol = COLOURS["bg-lightgreen"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 24, italic=True)
        #_fnt.underline = True
        _element.set_font(_fnt, align="left")
        _element.draw_border = False
        elements.append(_element)

        #Error message:
        _pos = ptc(22.13, 9.76)
        _size = ptc(9.6, 2.63)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_tag("error message")
        # _element.set_text("Password must contain at least 1 special character. Username must be at least 4 characters.")
        elements.append(_element)
        
'''
Main menu
This is the base of the main menu
All sub-menus of the main menu will be seperate classes
'''
class MainMenu(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)

        layer.set_upon_visible(self.upon_visible)

    def upon_visible(self):
        #Show the first step of selecting a track only
        self.parent_layer.switch_layer("main menu select track select")

    def create_track_button(self):
        self.parent_layer.switch_layer("main menu track creator")

    def select_track_button(self):
        self.parent_layer.switch_layer("main menu select track")

    def settings_button(self):
        self.parent_layer.switch_layer("main menu settings")

    def create_UI(self):
        elements = self.elements
        win = self.surface

        #White box background:
        _pos = ptc(7.14, 1.43)
        _size = ptc(25.23, 16.6)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.draw_background = True
        _element.draw_border = True
        _element.size = _size
        _element.bgcol = COLOURS["white"]
        elements.append(_element)
        
        self.buttons = []
        #"Select track" button
        _pos = ptc(1.5, 1.43)
        _size = ptc(4.62, 2.01)
        _element = SelectionButton(win, _pos.x, _pos.y, _size.x, _size.y, self.select_track_button, COLOURS["lightgrey"], COLOURS["grey"], self.buttons)
        _element.set_text("Select Track")
        _fnt = pygame.font.SysFont("Comic Sans MS", 24)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #"Create track" button
        _pos = ptc(1.5, 4.52)
        _size = ptc(4.62, 2.01)
        _element = SelectionButton(win, _pos.x, _pos.y, _size.x, _size.y, self.create_track_button, COLOURS["lightgrey"], COLOURS["grey"], self.buttons)
        _element.set_text("Create Track")
        _fnt = pygame.font.SysFont("Comic Sans MS", 24)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #"Settings" button
        _pos = ptc(1.5, 16.01)
        _size = ptc(4.62, 2.01)
        _element = SelectionButton(win, _pos.x, _pos.y, _size.x, _size.y, self.settings_button, COLOURS["lightgrey"], COLOURS["grey"], self.buttons)
        _element.set_text("Settings")
        _fnt = pygame.font.SysFont("Comic Sans MS", 24)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #"Username text"
        _pos = ptc(30, 18.02)
        _size = ptc(3.67, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18, italic=True))
        _element.fgcol = COLOURS["grey"]
        _element.draw_border = False
        _element.set_text("Username")
        _element.set_tag("Username Text")
        elements.append(_element)

        #"Username: " pre-text
        _pos = ptc(28.44, 18.02)
        _size = ptc(3.67, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.fgcol = COLOURS["grey"]
        _element.draw_border = False
        _element.set_text("User:")
        elements.append(_element)

'''
Settings menu within the main menu
This is useful for chaging colours etc.

'''
class MainMenuSettings(UICreator):
    def __init__(self, surface, layer, simulation_obj):
        super().__init__(surface, layer)

        self.simulation_obj = simulation_obj

        #These are changed by the login menu
        self.user_id = 0
        self.users_database = None 


    #Returns dictionary of settings from menu
    def get_settings(self):
        #Mainly tuples of rgb values
        settings = {
            "vehicle-colour" : (int(self.get_element("Vehicle Colour: text input r").get_text()), int(self.get_element("Vehicle Colour: text input g").get_text()), int(self.get_element("Vehicle Colour: text input b").get_text())),
            "track-colour" : (int(self.get_element("Track Colour: text input r").get_text()), int(self.get_element("Track Colour: text input g").get_text()), int(self.get_element("Track Colour: text input b").get_text())),
            "rock-colour" : (int(self.get_element("Rock Colour: text input r").get_text()), int(self.get_element("Rock Colour: text input g").get_text()), int(self.get_element("Rock Colour: text input b").get_text())),
            "tree-colour" : (int(self.get_element("Tree Colour: text input r").get_text()), int(self.get_element("Tree Colour: text input g").get_text()), int(self.get_element("Tree Colour: text input b").get_text())),
            "offroad-colour" : (int(self.get_element("Offroad Colour: text input r").get_text()), int(self.get_element("Offroad Colour: text input g").get_text()), int(self.get_element("Offroad Colour: text input b").get_text())),
        }

        return settings

    def delete_account_button(self):
        print(self.get_settings())

    #Sets the user settings to the given settings
    #   settings : dictionary of all the settings values to change
    #       keys:settings tag, value:value to hold
    def set_settings(self, settings):
        for key in settings.keys():
            #Get the element with the key and set value
            _element = self.get_element(key)
            _element.set_text(str(settings[key]))

        self.simulation_obj.apply_main_settings(**self.get_settings())

    def save_settings(self):
        if self.users_database != None:
            settings = self.get_settings()

            def rgb_to_hex(rgb):
                _hex="#"
                for col in rgb:
                    _hex_val = hex(col).replace("0x","")

                    #If hex value is less than 2 digits
                    #   concatenate a 0 on the start of the code
                    if len(_hex_val) < 2:
                        _hex_val = "0" + _hex_val

                    _hex += _hex_val
                return _hex

            #Apply settings to database
            #   needs to convert the rgb code to a hex code for storage
            self.users_database.execute_sql(f'''
                UPDATE UserSettings 
                SET 
                vehicle_colour="{rgb_to_hex(settings["vehicle-colour"])}",
                track_colour="{rgb_to_hex(settings["track-colour"])}",
                rock_colour="{rgb_to_hex(settings["rock-colour"])}",
                tree_colour="{rgb_to_hex(settings["tree-colour"])}",
                offroad_colour="{rgb_to_hex(settings["offroad-colour"])}"
                WHERE id = {self.user_id}
            ''')

        self.simulation_obj.apply_main_settings(**self.get_settings())



    def create_UI(self):
        elements = self.elements
        win = self.surface

        headings = [["Vehicle Colour:", (255,0,0)], ["Track Colour:", (0,0,0)], ["Rock Colour:", (255,255,255)], ["Tree Colour:", (255,255,255)], ["Offroad Colour:", (255,255,255)]]

        for heading_i in range(len(headings)):
            heading = headings[heading_i][0] #Get the heading name

            #heading
            _pos = ptc(7.67, 2.78 + 1.8 * heading_i)
            _size = ptc(4.68, 1.8)
            _element = TextBox(win, _pos.x, _pos.y)
            _element.size = _size
            _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
            _element.fgcol = COLOURS["txt-red"]
            _element.draw_border = False
            _element.set_text(heading)
            elements.append(_element)

            #Input boxes
            colours = ["r","g","b"]
            for colour_i in range(len(colours)):
                default = headings[heading_i][1][colour_i] #Get the default colour

                #Number input field:
                _pos = ptc(27.09 + colour_i*1.6, 2.78 + 1.8 * heading_i)
                _size = ptc(1.48, 1.11)
                _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, str(default), 16)
                _element.set_font(pygame.font.SysFont("Comic Sans MS", 16))
                _element.set_tag(heading + " text input " + colours[colour_i])
                _element.set_text(str(default))
                _element.bgcol = COLOURS["lightgrey"]
                elements.append(_element)

        #Delete account button
        _pos = ptc(28.68, 16.64)
        _size = ptc(3.36, 0.98)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.delete_account_button)
        _element.set_text("Delete Account")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 14)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #Save settings button
        _pos = ptc(7.67, 16.64)
        _size = ptc(3.36, 0.98)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.save_settings)
        _element.set_text("Save Settings")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 14)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)


'''
Header of the simulation menu route
'''
class MainMenuSelectTrack(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)

        layer.set_upon_visible(self.upon_visible)

    def upon_visible(self):
        #Show the first step of selecting a track only
        self.parent_layer.switch_layer("main menu select track select")


'''
Select the track of the main menu
'''
class MainMenuSelectTrackSelect(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)
        self.track_name = ""
        self.track_name = ""

        self.users_database = None
        self.user_id = 0

    def get_track(self):
        return self.track_name

    #Called when a track button is pressed
    def track_button(self, track_name, track_path):
        self.track_path = track_path
        self.track_name = track_name
        self.parent_layer.switch_layer("select track physics settings", from_parent=True)
    
    def create_UI(self, physics_menu_layer):
        elements = self.elements
        win = self.surface

        track_names = ["Meander", "Square", "Straight Line", "Rectangle", "Turns"]
        for track_i in range(len(track_names)):
            track_name = track_names[track_i]

            #Select Track 1 Button:
            _pos = ptc(7.57 + track_i * 5, 1.84)
            _size = ptc(3.76, 2.26)
            _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.track_button, args=(track_name, "./tracks/"))
            _element.set_text(track_name)
            _element.bgcol = COLOURS["darkgrey"]
            _element.fgcol = COLOURS["white"]
            _fnt = pygame.font.SysFont("Comic Sans MS", 24)
            _element.set_font(_fnt, align="centre")
            elements.append(_element)



'''
Physics settings for the main menu
'''
class SelectTrackPhysicsSettings(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)

##    def next_button(self, algorithm_settings_layer, change_parent):
##        self.parent_layer.switch_layer(algorithm_settings_layer, change_parent)
##
##        layer = self.parent_layer.find_layer("select track algorithm settings header")[1].tail()
##        print(layer.layer_name)
##        layer.set_visibility(False)
    
    def get_settings(self):
        settings = {
            "maximum-velocity" : int(self.get_element("Maximum Velocity: text input").get_text()),
            "acceleration-magnitude" : int(self.get_element("Acceleration Magnitude: text input").get_text()),
            "deceleration-magnitude" : int(self.get_element("Deceleration Magnitude: text input").get_text()),
            "turn-velocity" : float(self.get_element("Turn Velocity: text input").get_text()),
            "vehicle-width" : int(self.get_element("Vehicle Width: text input").get_text()),
            "vehicle-height" : int(self.get_element("Vehicle Height: text input").get_text()),
            "elasticity" : int(self.get_element("Elasticity: text input").get_text()),
            "friction" : int(self.get_element("Friction: text input").get_text())
        }
        return settings

    def create_UI(self, select_track_layer, algorithm_settings_layer):
        elements = self.elements
        win = self.surface

        #"Motion" title:
        _pos = ptc(7.59, 1.92)
        _size = ptc(4.68, 1.11)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Motion:")
        elements.append(_element)

        headings = [["Maximum Velocity:", 300], ["Acceleration Magnitude:", 600], ["Deceleration Magnitude:", 90], ["Turn Velocity:", 3.141/2], ["Vehicle Width:", 25], ["Vehicle Height:", 12]]

        #Titles
        for heading_i in range(0, len(headings)):
            heading = headings[heading_i][0]
            default = headings[heading_i][1]

            #Heading for input
            _pos = ptc(7.59, 3.44+heading_i*1.43)
            _size = ptc(8, 1.11)
            _element = TextBox(win, _pos.x, _pos.y)
            _element.size = _size
            _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
            _element.fgcol = COLOURS["txt-red"]
            _element.draw_border = False
            _element.set_text(heading)
            elements.append(_element)

            #Number input field:
            _pos = ptc(29.74, 3.44+heading_i*1.43)
            _size = ptc(1.91, 1.11)
            _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, str(default), 16)
            _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
            _element.set_text(str(default))
            _element.set_tag(heading + " text input")
            elements.append(_element)

        #"Physics" title:
        _pos = ptc(7.59, 12.74)
        _size = ptc(4.68, 1.11)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Physics:")
        elements.append(_element)

        headings2 = [["Elasticity:", 100], ["Friction:", 100]]

        for heading_i in range(0, len(headings2)):
            heading = headings2[heading_i][0]
            default = headings2[heading_i][1]

            #Heading for input
            _pos = ptc(7.59, 14.07+heading_i*1.43)
            _size = ptc(8, 1.11)
            _element = TextBox(win, _pos.x, _pos.y)
            _element.size = _size
            _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
            _element.fgcol = COLOURS["txt-red"]
            _element.draw_border = False
            _element.set_text(heading)
            elements.append(_element)

            #Number input field
            _pos = ptc(29.74, 14.07+heading_i*1.43)
            _size = ptc(1.91, 1.11)
            _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, str(default), 16)
            _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
            _element.set_tag(heading + " text input")
            _element.set_text(str(default))
            elements.append(_element)

        #Back button:
        _pos = ptc(7.51, 16.74)
        _size = ptc(1.65, 0.98)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.parent_layer.switch_layer, args=(select_track_layer, True))
        _element.set_text("Back")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #Next button:
        _pos = ptc(30.39, 16.74)
        _size = ptc(1.65, 0.98)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.parent_layer.switch_layer, args=(algorithm_settings_layer, True))
        _element.set_text("Next")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

'''
Algorithm settings for the simulation

simulation_object : the object which handles the simulation
track_selection_ui : the ui in main menu where the track is chosen
track_creator : the track creator object
bgcol : reference of the background colour
main_menu_settings_ui : the main menu settings ui
'''
class SelectTrackAlgorithmSettings(UICreator):
    def __init__(self, surface, layer, simulation_object, root_layer, track_selection_ui, track_creator, bgcol, physics_settings_ui):
        super().__init__(surface, layer)

        self.simulation_object = simulation_object
        self.track_selection_ui = track_selection_ui
        self.track_creator = track_creator
        self.root_layer = root_layer
        self.bgcol = bgcol
        self.physics_settings_ui = physics_settings_ui
        self.results_database = None

    def upon_visible(self, first_button, header_layer):
        header_layer.set_visibility(False, set_self=False)
        first_button.force_event()

    #Set the algorithm for the simulation
    #   algorithm_setttings_ui : the UI creator class containing the specific algorithm settings
    #   algorithm_name : the name of the algorithm (used in the simulation object to create the population)
    def set_algorithm(self, header_layer, algorithm_settings_ui, algorithm_name):
        self.algorithm_settings_ui = algorithm_settings_ui
        self.algorithm_name = algorithm_name

        header_layer.switch_layer(algorithm_settings_ui.parent_layer.layer_name)

    #Start simulation button function
    def start_simulation(self):
        algorithm_name = self.algorithm_name
        simulation_obj = self.simulation_object
        algorithm_settings_ui = self.algorithm_settings_ui
        physics_settings_ui = self.physics_settings_ui


        #Fetch track name and create track
        self.track_creator.load_track(file_name=self.track_selection_ui.track_name+".txt", file_dir=self.track_selection_ui.track_path)
        track_pieces = self.track_creator.track_pieces.get_list()

        self.root_layer.switch_layer(simulation_obj.layer.layer_name, False)

        #Initialise the simulation
        #   **algorithm_settings_ui.get_settings() : gets the specific settings from the UI input fields
        simulation_obj.set_results_database(self.results_database)
        simulation_obj.apply_algorithm_settings(algorithm_name, track_pieces, self.track_selection_ui.track_name, **algorithm_settings_ui.get_settings())
        simulation_obj.apply_physics_settings(**physics_settings_ui.get_settings())
        simulation_obj.initialise_simulation()

        #Set background colour
        self.bgcol[0] = simulation_obj.main_settings["offroad-colour"]


    def create_UI(self, physics_settings_layer, header_layer, astar_ui, genetic_ui, obstacle_ui, greedy_ui):
        elements = self.elements
        win = self.surface

        self.buttons = []
        
        #"A* Pathfinding" button
        _fnt_size = 18
        _pos = ptc(10.9, 1.67)
        _size = ptc(3.9, 1.86)
        _element = SelectionButton(win, _pos.x, _pos.y, _size.x, _size.y, self.set_algorithm, COLOURS["lightgrey"], COLOURS["grey"], self.buttons, args=(header_layer, astar_ui, "Astar"))
        self.parent_layer.set_upon_visible(self.upon_visible, args=(_element, header_layer)) #Reveal this button first
        _element.set_text("A* Pathfinding")
        _fnt = pygame.font.SysFont("Comic Sans MS", _fnt_size)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #"Genetic Algorithm" button
        _pos = ptc(15.17, 1.67)
        _size = ptc(3.9, 1.86)
        _element = SelectionButton(win, _pos.x, _pos.y, _size.x, _size.y, self.set_algorithm, COLOURS["lightgrey"], COLOURS["grey"], self.buttons, args=(header_layer, genetic_ui, "Genetic"))
        _element.set_text("Genetic Algorithm")
        _fnt = pygame.font.SysFont("Comic Sans MS", _fnt_size)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #"Obstacle Avoidance" button
        _pos = ptc(19.45, 1.67)
        _size = ptc(3.9, 1.86)
        _element = SelectionButton(win, _pos.x, _pos.y, _size.x, _size.y, self.set_algorithm, COLOURS["lightgrey"], COLOURS["grey"], self.buttons, args=(header_layer, obstacle_ui, "Obstacle Avoidance"))
        _element.set_text("Obstacle Avoidance")
        _fnt = pygame.font.SysFont("Comic Sans MS", _fnt_size)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #"Greedy Best First" button
        _pos = ptc(23.72, 1.67)
        _size = ptc(3.9, 1.86)
        _element = SelectionButton(win, _pos.x, _pos.y, _size.x, _size.y, self.set_algorithm, COLOURS["lightgrey"], COLOURS["grey"], self.buttons, args=(header_layer, greedy_ui, "AStar"))
        _element.set_text("Greedy Best First")
        _fnt = pygame.font.SysFont("Comic Sans MS", _fnt_size)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #"Algorithms:" header
        _pos = ptc(7.33, 2.09)
        _size = ptc(3.57, 1.8)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Algorithm:")
        elements.append(_element)

        #Back button
        _pos = ptc(7.51, 15.74)
        _size = ptc(1.65, 0.98)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.parent_layer.switch_layer, args=(physics_settings_layer, True))
        _element.set_text("Back")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #Start Simulation button
        _pos = ptc(27.69, 16.64)
        _size = ptc(4.2, 0.98)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.start_simulation)
        _element.set_text("Start Simulation")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

'''
Algorithm settings for the simulation
'''
class AlgorithmSettingsAstar(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)

    def get_settings(self):
        settings = {
            "population-size":1,
            "follow-strength":int(self.get_element("Follow Strength").get_text()),
        }
        
        return settings

    def create_UI(self):
        elements = self.elements
        win = self.surface

        #Follow strength
        _pos = ptc(8.39, 4.19)
        _size = ptc(7.54, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Follow Strength")
        elements.append(_element)

        #Number input field
        _pos = ptc(29.46, 4.17)
        _size = ptc(1.65, 1.11)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "100", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("Follow Strength")
        _element.set_text("100")
        elements.append(_element)

        


'''
Algorithm settings for the simulation
'''
class AlgorithmSettingsGenetic(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)

    def get_settings(self):
        settings = {
            "population-size": int(self.get_element("Population Size: text input").get_text()),
            "mutation-rate": int(self.get_element("Mutation Rate: text input").get_text()),
            "mutation-chance": int(self.get_element("Mutation Chance: text input").get_text()),
            "existing-network": self.get_element("Existing Network: text input").get_text(),
        }
        
        return settings

    def create_UI(self):
        elements = self.elements
        win = self.surface        

        headings = [["Population Size:", 20], ["Mutation Rate:", 100], ["Mutation Chance:", 80]]

        for heading_i in range(0, len(headings)):
            heading = headings[heading_i][0]
            default = headings[heading_i][1]

            #Heading for input
            _pos = ptc(8.39, 4.17+heading_i*1.43)
            _size = ptc(8, 1.11)
            _element = TextBox(win, _pos.x, _pos.y)
            _element.size = _size
            _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
            _element.fgcol = COLOURS["txt-red"]
            _element.draw_border = False
            _element.set_text(heading)
            elements.append(_element)

            #Number input field
            _pos = ptc(29.46, 4.17+heading_i*1.43)
            _size = ptc(1.65, 1.11)
            _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, str(default), 16)
            _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
            _element.set_tag(heading + " text input")
            _element.set_text(str(default))
            elements.append(_element)

        #Existing network:
        _pos = ptc(8.39, 9.19)
        _size = ptc(7.54, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Existing Network:")
        elements.append(_element)

        #Input field
        _pos = ptc(8.59, 10.62)
        _size = ptc(22.52, 1.11)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "/../.../..", 128)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("Existing Network: text input")
        elements.append(_element)

'''
Algorithm settings for the simulation
'''
class AlgorithmSettingsObstacles(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)

    def get_settings(self):
        settings = {
            "population-size":1,
            "follow-strength":int(self.get_element("Follow Strength").get_text()),
        }
        
        return settings

    def create_UI(self):
        elements = self.elements
        win = self.surface        

        #Follow strength
        _pos = ptc(8.39, 4.19)
        _size = ptc(7.54, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Follow Strength")
        elements.append(_element)

        #Number input field
        _pos = ptc(29.46, 4.17)
        _size = ptc(1.65, 1.11)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "100", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("Follow Strength")
        _element.set_text("100")
        elements.append(_element)



'''
Algorithm settings for the simulation
'''
class AlgorithmSettingsGreedy(UICreator):
    def __init__(self, surface, layer):
        super().__init__(surface, layer)

    def get_settings(self):
        settings = {
            "population-size":1,
            "follow-strength":int(self.get_element("Follow Strength").get_text()),
        }
        
        return settings

    def create_UI(self):
        elements = self.elements
        win = self.surface        

        #Follow strength
        _pos = ptc(8.39, 4.19)
        _size = ptc(7.54, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Follow Strength")
        elements.append(_element)

        #Number input field
        _pos = ptc(29.46, 4.17)
        _size = ptc(1.65, 1.11)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "100", 16)
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        _element.set_tag("Follow Strength")
        _element.set_text("100")
        elements.append(_element)

        #TEMPORARY ("test" text box)
        _pos = ptc(8.39, 5.19)
        _size = ptc(7.54, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Test - Greedy Best First")
        elements.append(_element)

'''
main menu track creator ui path
'''
class MainMenuTrackCreator(UICreator):

    
    #Validate a given track name
    #   track_name : track name to validate
    #returns True/False if allowed/not allowed
    def validate_track_name(self, track_name):

        #Used to check if password has a character with ascii code in given range (inclusive)
        def has_ASCII(inp, _min, _max):
            for char_i in range(len(inp)):
                
                #ord(char) converts to ascii
                if _min <= ord(inp[char_i]) <= _max:
                    return True
                
            return False


        #Contains a "special character"
        #   character which isnt a number, lower or upper case letter
        _found= False
        for char_i in range(len(track_name)):
            _code = ord(track_name[char_i])
            
            #if charcter is number or capital or lowercase == False
            if (48 <= _code <= 57 or 65 <= _code <= 90 or 97 <= _code <= 122) == False:
                _found = True

        if _found == False:
            return True

        #Return false if name contains a special character
        return False
        

    #"Start track creator" button code
    #   initiates the track creator and sets the track name
    def start_track_creator(self, root_layer, track_creator_layer, bgcol, track_creator_obj):
        track_name = self.get_element("track name field").get_text()

        #Apply default name
        if track_name == "":
            track_name = "Track1"

        if self.validate_track_name(track_name) == False:
            return
        
        bgcol[0] = COLOURS["white"]
        root_layer.switch_layer(track_creator_layer)
    
        track_creator_obj.set_name(track_name)

    def create_UI(self, root_layer, track_creator_layer, bgcol, track_creator_obj):
        elements = self.elements
        win = self.surface        

        #"Track name:"
        _pos = ptc(7.71, 1.86)
        _size = ptc(7.54, 1.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("Track Name:")
        elements.append(_element)

        #Track name input field
        _pos = ptc(7.71, 2.95)
        _size = ptc(22.52, 1.11)
        _element = TextInput(win, _pos.x, _pos.y, _size.x, _size.y, "Track1", 16)
        _element.bgcol = COLOURS["lightgrey"]
        _element.set_tag("track name field")
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 18))
        elements.append(_element)

        #Explanation
        _pos = ptc(7.89, 4.53)
        _size = ptc(23.42, 11.03)
        _element = TextBox(win, _pos.x, _pos.y)
        _element.size = _size
        _element.set_font(pygame.font.SysFont("Comic Sans MS", 24))
        _element.fgcol = COLOURS["txt-red"]
        _element.draw_border = False
        _element.set_text("The Track Creator lets you design a custom 'track'/path for the vehicles to follow. A track can be saved and output to a file, which is named via the input field above.")
        elements.append(_element)

        #Start track creator button
        _pos = ptc(27.68, 16.64)
        _size = ptc(4.2, 0.98)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.start_track_creator, args=(root_layer, track_creator_layer, bgcol, track_creator_obj))
        _element.set_text("Start Creator")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

'''
Track Creator UI (buttons for track placement)
'''
class TrackCreatorUI(UICreator):
    def __init__(self, surface, layer, bgcol):
        super().__init__(surface, layer)

        self.user_id = 0
        self.users_database = None
        self.bgcol = bgcol

    #Save track externally and in the tracks database
    def save_track(self, track_creator):
        path = track_creator.save_track(file_dir="./tracks/")

        #Add track to database
        if self.users_database != None:
            next_id = self.users_database.highest_entry("Tracks", "id") + 1

            self.users_database.add_entry("Tracks", id=next_id, user_id=self.user_id, track_dir="./tracks/", track_name=track_creator.track_name)

    #Switch layer to the main menu
    def end_creator(self):
        self.bgcol[0] = COLOURS["bg-lightblue"]
        self.parent_layer.parent_layer.switch_layer("main menu")


    def create_UI(self, track_creator):
        elements = self.elements
        win = self.surface        

        #Straight piece button:
        _pos = ptc(0.14, 17.33)
        _size = ptc(1.72, 1.72)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, track_creator.place_piece, args=("straight",))
        _element.set_image("./sprites/TrackStraight.png")
        elements.append(_element)

        #Curve small right piece button
        _pos = ptc(2.12, 17.33)
        _size = ptc(1.72, 1.72)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, track_creator.place_piece, args=("curve-right",))
        _element.set_image("./sprites/TrackCurveRightSmall.png")
        elements.append(_element)

        #Curve small left piece button
        _pos = ptc(6.1, 17.33)
        _size = ptc(1.72, 1.72)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, track_creator.place_piece, args=("curve-left",))
        _element.set_image("./sprites/TrackCurveLeftSmall.png")
        elements.append(_element)

        #End position piece button
        _pos = ptc(30.12, 17.33)
        _size = ptc(1.72, 1.72)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, track_creator.place_piece, args=("end",))
        _element.set_image("./sprites/TrackEndPiece.png")
        elements.append(_element)

        #Save track button
        _pos = ptc(30.98, 0)
        _size = ptc(2.88, 1.19)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.save_track, args=(track_creator, ))
        _element.set_text("Save Track")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #Back button
        _pos = ptc(0, 0)
        _size = ptc(2.88, 1.19)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.end_creator)
        _element.set_text("Back")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

'''
Simulation UI
'''
class SimulationUI(UICreator):
    def __init__(self, surface, layer, bgcol, simulation_object):
        super().__init__(surface, layer)

        self.user_id = 0
        self.users_database = None
        self.bgcol = bgcol
        self.simulation_object = simulation_object
        self.leaderboard = []
        self.performance_history = []

    #Switch layer to the main menu
    def end_simulation(self):
        self.bgcol[0] = COLOURS["bg-lightblue"]
        self.parent_layer.parent_layer.switch_layer("main menu")

    #Update the leaderboard's text with the leaderboard list
    # def update_leaderboard(self, leaderboard):
    #     self.leaderboard = leaderboard.copy()

    #     for entry_i in range(leaderboard):
    #         entry = self.get_element("leaderboard" + f"{entry_i+1}")
    #         entry.set_text(f"{entry_i+1}. "+leaderboard[entry_i])


    def create_UI(self):
        elements = self.elements
        win = self.surface        

        #End Simulation Button
        _pos = ptc(0, 0)
        _size = ptc(2.88, 1.19)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.end_simulation, args=())
        _element.set_text("End Simulation")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #Restart Simulation Button
        _pos = ptc(30.98, 0)
        _size = ptc(2.88, 1.19)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.simulation_object.restart_simulation, args=())
        _element.set_text("Restart Simulation")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)

        #Save simulation button
        _pos = ptc(27.97, 0)
        _size = ptc(2.88, 1.19)
        _element = Button(win, _pos.x, _pos.y, _size.x, _size.y, self.simulation_object.save_simulation, args=())
        _element.set_text("Save Last Simulation")
        _element.bgcol = COLOURS["darkgrey"]
        _element.fgcol = COLOURS["white"]
        _fnt = pygame.font.SysFont("Comic Sans MS", 16)
        _element.set_font(_fnt, align="centre")
        elements.append(_element)


        #Leaderboard Text
        # _pos = ptc(1, 10.4)
        # _size = ptc(6.3, 2)
        # _element = TextBox(win, _pos.x, _pos.y)
        # _element.size = _size
        # _element.set_font(pygame.font.SysFont("Comic Sans MS", 14))
        # _element.fgcol = COLOURS["txt-red"]
        # _element.draw_border = False
        # _element.set_text("Leaderboard")
        # elements.append(_element)

        # for i in range(10):
        #     self.leaderboard.append(None)
        #     _pos = ptc(1, 10.4 + (i+1) * 0.5)
        #     _size = ptc(6.3, 2)
        #     _element = TextBox(win, _pos.x, _pos.y)
        #     _element.size = _size
        #     _element.set_font(pygame.font.SysFont("Comic Sans MS", 14))
        #     _element.fgcol = COLOURS["black"]
        #     _element.draw_border = False
        #     _element.set_text(f"{i+1}.")
        #     _element.set_tag("leaderboard "+f"{i+1}")
        #     elements.append(_element)






if __name__ == "__main__":
    username = 'qwertyuiopasdfgh'
    print(CreatenewUserMenu.validate_username(CreatenewUserMenu, username))

