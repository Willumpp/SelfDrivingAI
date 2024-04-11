
import pygame
import random
from CustomStructures import Vector, Queue 

COLOURS = {
    "bg-lightblue": (214, 220, 229),
    "bg-lightgreen":(214, 220, 229),
    "white":        (255,255,255),
    "txt-red":      (192, 0, 0),
    "black":        (0, 0, 0),
    "darkgrey":     (64, 64, 64),
    "grey":         (175, 171, 171),
    "lightgrey":    (242, 242, 242),
}

'''
UI Element class
inherit from this when creating a UI element

parameters:
    surface : the pygame surface to draw onto
    xpos : the x-coordinate of the UI element
    ypos : the y-coordinate of the UI element
    width : the width of the bounding box
    height : the height of the bounding box
    font : the font for drawing text
    font_size : the size of the font
methods:
    get_pos : returns the postion vector
    set_pos : sets the x and y coordinate of the position vector
    get_bbox : returns the bottom-right corner of the bounding box
    update : placeholder for update method
    draw : placeholder for draw method
    get/set text : get/set method for draw text
    get/set tag : get/set tag for object's tag
    require_visible : decorator to only call a function if the UI element is visible
    set_font(font) : changes the font of the drawable text with the passed pygame font
    _draw_background : draw the backbround rectangle of colour self.bgcol
    _draw_text : draw text stored in self._text
    _draw_border : draw the bounding box of the element
    _draw_sprite : draw the sprite set via "set image"
'''
class UIElement:
    def __init__(self, surface, xpos, ypos, width, height, font="Comic Sans MS", font_size=14):
        self.surface = surface
        self._pos = Vector(xpos, ypos) #Screen position of the object
        self.visible = True #False so the element is invisible AND does not update
        self.layer = None
        self.bgcol = (255, 255, 255) #usually background colour
        self.fgcol = (0, 0, 0) #usually text colour
        self._font = pygame.font.SysFont(font, font_size)
        self.size = Vector(width, height)
        self._bbox = Vector(self._pos.x + self.size.x, self._pos.y + self.size.y) #bottom-right corner of the collision box
        #self.require_events = False #require pygame events to be passed to the "update" method
        self.draw_border = True #draw the collision box border
        self._text = ""
        self.font_align = "left"
        self._tag="" #this is the id of the element, used to easily fetch the element
        self.sprite_image = None
        self.draw_background = True


    #Get/set for position (returns Vector)
    def get_pos(self):
        return self._pos

    def set_pos(self, xpos, ypos):
        self.pos.set_pos(xpos, ypos)

    #Set the visiblity of the element
    #   active : true/false visibility
    def set_visible(self, active):
        self.visible = active

    #Return the bottom-right corner of the collision box
    def get_bbox(self):
        self._bbox.set_pos(self._pos.x + self.size.x, self._pos.y + self.size.y)
        return self._bbox

    #Set the sprite image to draw
    #   image_dir : the directory of the image to draw
    #   width : the width to scale the image
    #   height : the height to scale the image
    def set_image(self, image_dir, width=0, height=0):

        #Set default width and height to UI width and height
        if width == 0: width = self.size.x
        if height == 0: height = self.size.y

        #Create the sprite surface
        #   Scale the image with pygame.transform
        self.sprite_image = pygame.transform.scale(pygame.image.load(image_dir), (int(width), int(height)))

    #update/draw placeholders
    def update(self, events=[]):
        pass

    def draw(self):
        pass

    #get/set method for tag
    #   tag : the ID of the UI element
    def set_tag(self, tag):
        self._tag = tag

    def get_tag(self):
        return self._tag

    #get/set method for text
    #   text : the text being drawn over the UI element
    def set_text(self, text):
        self._text = text

    def get_text(self):
        return self._text

    #set the font, including font align
    #   pygame_font : must be a pygame.font.SysFont()
    def set_font(self, pygame_font, align="left"):
        self._font = pygame_font
        self.font_align = align

    #Decorator which only calls the function if the object is visible
    def require_visible(function):

        #"inner" function, "function" parameters are passed through here
        def inner(self, *args):

            if self.visible == True:
                return function(self, *args)

        return inner

        
    #Draw the background of the UI element
    def _draw_background(self):
        if self.draw_background:
            pygame.draw.rect(self.surface, self.bgcol, [*self._pos.get_pos(), *self.size.get_pos()])

    #Draw "_text" over the UI element
    #   applies font and font aligning
    def _draw_text(self, custom_text=""):
        _draw_text = custom_text

        #optional custom text functionality
        if custom_text == "":
            _draw_text = self._text
        
        #Dont call rest of function if drawing nothing
        if _draw_text == "" : return
            
        #Render text
        #self.text_surface = self._font.render(_draw_text, True, self.fgcol)
        text_surfaces = []
        _text_height = 0
        _text_width = 0
        font_size = self._font.size("A") #Get approximate font width and height
        
        #Wrap text

        #Wrap detection
        #   line limit = width of line / width of each character
        _out = ""
        for char_i in range(0, len(_draw_text)):
            _out += _draw_text[char_i]

            #If the length of the given text exceeds the boundary
            #   length of text is given from "font.size(text)" returned as (width, height)
            if self._font.size(_out)[0] > (self.size.x - 25):

                #Add to list of text to draw and increment the total height
                # _out[:_out.rfind(" ") = string up until the final space
                if " " in _out:
                    text_surfaces.append(self._font.render((_out[:_out.rfind(" ")]), True, self.fgcol))
                    _out = _out[_out.rfind(" ")+1:]
                else:
                    text_surfaces.append(self._font.render((_out), True, self.fgcol))
                    _out = ""

                _text_height += text_surfaces[-1].get_height()
                _text_width += text_surfaces[-1].get_width()
                

        #Add rest of string (which wasn't included in final iteration)
        if _out != "":
            text_surfaces.append(self._font.render((_out), True, self.fgcol))
            _text_height += text_surfaces[-1].get_height()
            _text_width += text_surfaces[-1].get_width()

        #Get the average width of all the lines
        if len(text_surfaces) != 0:
            _text_width = _text_width / len(text_surfaces)


        #Centre and align text
        #   Text should usually be verically centred to the UI element
        _xoffset = 10
        _yoffset = abs(self.size.y - _text_height)//2
        
        if self.font_align == "centre":
            # _xoffset = abs(self.size.x - self.text_surface.get_width())//2
            _xoffset = abs(self.size.x - _text_width)//2

        #Draw the text - applying the offset
        # self.surface.blit(self.text_surface, (self._pos + Vector(_xoffset, _yoffset)).get_pos())
        for index, text_surface in enumerate(text_surfaces):
            self.surface.blit(text_surface, (self._pos + Vector(_xoffset, _yoffset) + Vector(0, index*font_size[1])).get_pos())

    #Draw the collision box
    def _draw_border(self):
        if self.draw_border == True:
            _bbox = self.get_bbox()

            #List is the coordinate of each corner of the element
            pygame.draw.lines(self.surface, COLOURS["black"], True, (
                self._pos.get_pos(), 
                (_bbox.x, self._pos.y), 
                (_bbox.x, _bbox.y),
                (self._pos.x, _bbox.y)
            ))

    #Draw the sprite
    #   draws nothing if "sprite_image" is "None"
    def _draw_sprite(self):
        if self.sprite_image != None:
            self.surface.blit(self.sprite_image, self._pos.get_pos())


'''
Textbox class
Draws text to the screen
Inherits from "UIElement"

methods:
    draw : draws "_text" to the screen
'''
class TextBox(UIElement):
    def __init__(self, surface, xpos, ypos, font="Comic Sans MS", font_size=14):
        super().__init__(surface, xpos, ypos, 0, 0, font, font_size)

        self.draw_border = False
        self.draw_background = False

    @UIElement.require_visible
    def draw(self):
        self._draw_background()
        self._draw_text()
        self._draw_border()


'''
Button class
Inherits from "UIElement" class

parameters:
    function : the function called when the button is pressed
    args : the arguments for the function to call with
'''
class Button(UIElement):
    def __init__(self, surface, xpos, ypos, width, height, function, args=()):
        super().__init__(surface, xpos, ypos, width, height)

        self.function = function #function to call upon button press
        self.image = None #sprite to draw over the button
        self.args = args

        #upon mouse press and function call, this is set to true
        #   when true the function cannot be called again
        #   this remains true until the mouse button is released
        #   prevents the function from being called every frame
        self.called_event = False

        #Imply the "update" method requires events
        #self.require_events = True

    #Calls the function in "function" attribute
    def call_event(self):
        if self.called_event == False:
            self.function(*self.args)
            
            #cannot call event again until mouse release
            self.called_event = True

    #Artificially call the event without considering the button press
    def force_event(self):
        self.called_event = False
        self.call_event()
        # self.function(*self.args)

    @UIElement.require_visible
    def draw(self):
        self._draw_background()
        self._draw_sprite()
        self._draw_text()
        self._draw_border()
        
    @UIElement.require_visible
    def update(self, events=[]):        
        mouse_pos = pygame.mouse.get_pos()
        _bbox = self.get_bbox()

        #Mouse button detection
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:

                #Check if mouse coordinates are inside the bounding box
                if self._pos.x < mouse_pos[0] < _bbox.x and self._pos.y < mouse_pos[1] < _bbox.y:
                    self.call_event()

            if event.type == pygame.MOUSEBUTTONUP:
                self.called_event = False


'''
Selection button class
inherits from button class

parameters:
    selection_col : background colour when the button is pressed and selected
    default_col : background colour when the button is not selected
    buttons : list containing the other selection button objects to be paired with

methods:
    call_event : call the function stored in "function". Also changes the colour of the paired buttons
'''
class SelectionButton(Button):
    def __init__(self, surface, xpos, ypos, width, height, function, selection_col, default_col, buttons, args=()):
        super().__init__(surface, xpos, ypos, width, height, function, args=args)

        self.default_col = default_col
        self.selection_col = selection_col
        self.bgcol = default_col
        self.buttons = buttons
        self.buttons.append(self)


    def call_event(self):
        super().call_event()

        #Change the background colour of all colours (including self)
        for button in self.buttons:
            button.bgcol = self.default_col

        #Change own background colour to the selection colour
        self.bgcol = self.selection_col


'''
Text Input class
UI Element which you can click and then type into

Parameters:
    default_text : the text which is displayed when the text box is empty (the text is not retrieved with get_text)
    max_characters : the maximum number of characters the textbox holds

Methods:
    has_text() : returns if the textbox has text within
    get_text() : returns the text typed within the text box
'''
class TextInput(UIElement):
    def __init__(self, surface, xpos, ypos, width, height, default_text, max_characters):
        super().__init__(surface, xpos, ypos, width, height)
        self._default_text = default_text
        self._max_char = max_characters #different from CD
        self.selected = False
        self.called_event = False
        #self.require_events = True
        self.hide_text = False

    #Returns if there is text in the text box
    def has_text(self):
        return (len(self._text) != 0)

    def call_event(self):
        if self.called_event == False:
            self.selected = True
            self.called_event = True

    @UIElement.require_visible
    def update(self, events=[]):
        mouse_pos = pygame.mouse.get_pos()
        _bbox = self.get_bbox()


        for event in events:

            #Standart click detection (look for button class for more info)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._pos.x < mouse_pos[0] < _bbox.x and self._pos.y < mouse_pos[1] < _bbox.y:
                    self.call_event()
                else:
                    self.selected = False

            if event.type == pygame.MOUSEBUTTONUP:
                self.called_event = False

            #Keyboard input
            if event.type == pygame.KEYDOWN and self.selected == True:
                #Backspace functionality
                if event.key == pygame.K_BACKSPACE and self.has_text():
                    self._text = self._text[:-1] #remove last chacter
                #This is here to avoid backspace even when the string is empty
                elif event.key == pygame.K_BACKSPACE:
                    continue
                #Character limit
                elif len(self._text) >= self._max_char:
                    continue
                else:
                    #Add character to draw text
                    self._text += event.unicode

    @UIElement.require_visible
    def draw(self):
        self._draw_background()

        #Default text display (only show when not selected and empty)
        if self.has_text() == True and self.hide_text == True:
            self._draw_text("*"*len(self._text))
        elif self.has_text() == False and self.selected == False:
            self._draw_text(self._default_text)
        else:
            #This draws the text as normal
            self._draw_text()

        self._draw_border()

'''
Layers class
Add objects and UI elements to the layer and have control over them
    Allows for menu control etc.

Parameters:
    layer_name : the UNIQUE name to call the layer (used for searching for the layer)
    parent_layer : the parent layer of THIS layer

Methods:
    add_objects : Can add a singular object or multiple objects to a layer for handling
    add_UIelements : Can add a singular UI element or multiple UI elements to a layer for handling
    add_child : Add a child layer to self
    set_visible(active) : Sets the visibility of exclusively this layer (so not child layers; hidden layers dont draw AND update)
    set_visibility(active) : Sets the visibility of self AND all the child layers
    update : Updates all UI elements AND objects in layer
    draw : Draws all UI elements AND objects in layer
    find_layer(layer_name) : Finds the layer with the layer name and returns the object AND queue of path to layer
'''
class Layer:
    def __init__(self, layer_name, parent_layer=None):
        self.child_layers = [] #Contains every sub-layer (everything that happens to this layer happens to child layers)
        self.objects = [] #Meant for object handling
        self.UIelements = [] #Meant for UI element handling
        self.visible = True #Reveals/Hides layers , when hidden "update/draw" isnt called
        self.layer_name = layer_name
        self.parent_layer = parent_layer

        self.upon_visible = self.placeholder #This function is called when layer is set to visible
        self.upon_visible_args = ()

        self._path = Queue(64)

    #Set the function and arguments for the function call when set to visible
    def set_upon_visible(self, func, args=()):
        self.upon_visible = func
        self.upon_visible_args = args

    def placeholder(self):
        pass

    #Adds an object to the layer
    #   single_obj : single game object to add to the layer
    #   obj_list : list of objects to add to the layer
    def add_objects(self, single_obj=None, obj_list=[]):
        if single_obj != None:
            self.objects.append(single_obj)
        
        for obj in obj_list:
            self.objects.append(obj)
    
    #Clear layer of all objects
    def clear_objects(self):
        self.objects.clear()

    #Clear layer of all ui elements
    def clear_ui(self):
        self.UIelements.clear()

    #Remove object from the layer
    #   obj_list : list of objects to remove
    #   tag : remove object with specific tag
    def remove_objects(self, obj_list=[], tags=[]):
        for obj in obj_list:
            if obj in self.objects:
                self.objects.remove(obj)

        _objects = self.objects.copy()
        for obj in _objects:
            if obj.has_tags(tags):
                self.objects.remove(obj)

    

    #Adds UI elements to the layer
    #   single_element : single UI element to add to the layer
    #   element_list : list of elements to add to the layer
    def add_UIelements(self, single_element=None, element_list=[]):
        if single_element != None:
            self.UIelements.append(single_element)
        
        for element in element_list:
            self.UIelements.append(element)


    #Add a sub-layer to this layer
    #   layer : the layer object to add
    def add_child(self, layer):
        self.child_layers.append(layer)
        layer.parent_layer = self
        

    #Set the visibility of the layer (but not child layers)
    #   active : boolean to hide or show the layer
    def set_visible(self, active):
        self.visible = active

        #Set visiblity of all objects
        for obj in self.objects:
            obj.set_visible(active)

        #Set visibility of all UI elements
        for element in self.UIelements:
            element.set_visible(active)


    #Set the visibility of the layer (including child layers)
    #   active : boolean to hide or show the layer
    def set_visibility(self, active, set_self=True):
        
        #Perform a depth-first / in-order traversal
        for layer in self.child_layers:
            layer.set_visibility(active)

        #When at a leaf node..

        #Set the visibility of self
        if set_self == True:
            self.set_visible(active)

            #Set visiblity of all objects
            for obj in self.objects:
                obj.set_visible(active)

            #Set visibility of all UI elements
            for element in self.UIelements:
                element.set_visible(active)

            #Call upon visible when set to active
            if active == True:
                self.upon_visible(*self.upon_visible_args)

    #Update all objects in layer and in child layers
    #Executes when visible
    def update(self, events):
        if self.visible == True:

            #Perform a depth-first / in-order traversal
            for layer in self.child_layers:
                layer.update(events)
                

            #When at a leaf node..
            #Update all objects
            for obj in self.objects:
                obj.update(events)

            #Update all UI elements
            for element in self.UIelements:
                element.update(events)

    #Draw all objects in layer and in child layers
    #Executes when visible
    def draw(self):
        if self.visible == True:
            # print(self.layer_name)

            #When at a leaf node..
            #Draw all objects
            for obj in self.objects:
                obj.draw()

            #Draw all UI elements
            for element in self.UIelements:
                element.draw()
                
            #Perform a depth-first / in-order traversal
            for layer in self.child_layers:
                layer.draw()

            
    


    #Find a layer with a given layer name , returns the layer object and the Queue of layers to the layer
    #   layer_name : the name of the layer to find (string)
    #   path : queue of preceding layers (not meant to be assigned upon first call)
    # def find_layer(self, layer_name, path=Queue(16)):
    def find_layer(self, layer_name, path=None):
        if path == None:
            self._path.clear()
            path = self._path

        path.enqueue(self)

        #Return the path to the layer when found
        if layer_name == self.layer_name:
            return True, path

        #Try to find layer through children
        for layer in self.child_layers:
            _out = layer.find_layer(layer_name, path=path)
            #_out = tuple containing the success of the find and the path to the layer

            if _out[0] == True:
                return _out

        return False, path


    #Reveals the given layer name (and hides all other children)
    #   layer name : name of layer to reveal
    #   from parent : switch from the parent layer instead of this layer
    def switch_layer(self, layer_name, from_parent=False):
        
        if from_parent == False:
            revealed_layer = self.find_layer(layer_name)[1].tail()

            self.set_visibility(False, set_self=False)
            revealed_layer.set_visibility(True)
        else:
            self.parent_layer.switch_layer(layer_name)
            



#Only run as a test
if __name__ == "__main__":

    def say_hi():
        print("hi")

    def say_test():
        print("Test")

    def test_func():
        print(test_textinput.get_text())

    pygame.init()

    SCREEN_SIZE = Vector(480, 480)
    FPS = 30

    pygame.font.init()
    win = pygame.display.set_mode(SCREEN_SIZE.get_pos())
    pygame.display.set_caption("UI Test")
    clock = pygame.time.Clock()

    #Text box
    # test_text = TextBox(win, SCREEN_SIZE.x//2, SCREEN_SIZE.y//2)
    # test_text.set_text("Test text")
    # test_text.fgcol = COLOURS["txt-red"]

    #Button
    # test_button = Button(win, 100, 200, 150, 100, say_test)
    # test_button.set_text("Example button")
    # test_button.fgcol = (255,255,255)
    # test_button.bgcol = (0,0,0)

    #Text input
    test_textinput = TextInput(win, 100, 200, 150, 100, "Example Box", 100)
    test_textinput.set_font(pygame.font.SysFont("Comic Sans MS", 18), align="centre")

    # buttons = []
    # for i in range(4):
    #     buttons.append(SelectionButton(win, i*80, 300, 50, 50, say_hi, COLOURS["lightgrey"], COLOURS["darkgrey"], buttons))

    # win.fill(COLOURS["bg-lightblue"])

        # test_text.draw()

        # test_button.draw()
        # test_button.update(events)

        # test_textinput.draw()
        # test_textinput.update(events)

        # for button in buttons:
        #     button.draw()
        #     button.update(events)

    running = True
    while running:

        clock.tick(FPS)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     print(pygame.mouse.get_pos())
            
            if event.type == pygame.KEYDOWN:
                print(event.unicode)
        

        win.fill((255,255,255))

        #Draw and update button
        test_textinput.draw()
        test_textinput.update(events)

        pygame.display.update()

    pygame.quit()

