
from SimulationObjects import StraightLinePiece, CurvePieceLeft, CurvePieceRight, EndPiece, StartPiece, SimulationObject
from CustomStructures import *
from FileHandlers import *
import pygame 

'''
Track creator object
Used to create, load, and save tracks
'''
class TrackCreator(SimulationObject):
    def __init__(self, surface, camera, layer, simulation_handler, track_name):
        super().__init__(surface, camera, None, 0, 0) #New
        self.selected_piece = None

        self.track_pieces = Stack(-1) #Track OBJECTS in simulation
        self.track_structure = Stack(-1) #Track COMPONENTS (((x, y), direction, track type)) in simulation

        self.surface = surface
        self.camera = camera
        self.layer = layer
        self.simulation_handler = simulation_handler

        self.name_to_obj = {
            "straight" : StraightLinePiece,
            "curve-right" : CurvePieceRight,
            "curve-left" : CurvePieceLeft,
            "end" : EndPiece, 
            "start" : StartPiece,
        }
        
        #Create obj to name dictionary (reverse of name to obj)
        self.obj_to_name = {}
        for key in self.name_to_obj.keys():
            self.obj_to_name[self.name_to_obj[key]] = key

        self.add_structure((0, 0), 0, "start")

        self.track_name = track_name

    #Set the name of the track to create
    def set_name(self, name):
        self.track_name = name

    #Adds track piece to "track pieces"
    #   does not create component!
    #track_piece : piece object
    def add_piece(self, track_piece):        
        self.track_pieces.push(track_piece)
        self.layer.add_objects(single_obj=track_piece)
    
    
    #Appends structure to "track structure"
    #   pos : coordiantes (not vector) of the track piece (x, y)
    #   direction : the rotation of the track piece
    #   track_type : the object type
    #Creates piece object and adds it to piece stack
    def add_structure(self, pos, direction, track_type):
        structure = (pos, direction, track_type)
        self.track_structure.push(structure)

        #Convert structure to object and append to piece list
        _obj = self.name_to_obj[structure[2]]
        _piece = _obj(self.surface, self.camera, self.simulation_handler, structure[0][0], structure[0][1])
        _piece.set_direction(structure[1])
    
        #Apply tag
        # if self.track_pieces.get_size() > 0:
        #     _piece.add_tag(f"{len(self.track_pieces)}")

        #     #Add the tag (id) to the track piece
        # else:
        #     _piece.add_tag(f"0")

        # _piece.add_tag(f"{self.track_pieces.get_size()}")

        #Add piece to track stack
        self.add_piece(_piece)



    #Set the "track structure" to the given list and creates objects
    def set_structure(self, track_structure):
        self.track_structure = Stack(-1)
        self.track_pieces = Stack(-1)

        for structure in track_structure:
            self.add_structure(*structure)


    #Place a piece on the end of the track
    #   piece_name : the (string) name of the track object
    def place_piece(self, piece_name):
        _obj = self.name_to_obj[piece_name]
        _front_piece = self.track_pieces.peek()
        _direction = _front_piece.direction

        #If front piece is a curved piece
        if _front_piece.has_tags(tags=["curve-right"]):
            _direction = _direction + math.pi/2
            
        if _front_piece.has_tags(tags=["curve-left"]):
            _direction = _direction - math.pi/2

        self.add_structure(_front_piece.get_end_pos().get_pos(), _direction, piece_name)


    #Loads the track from the given text file
    #   file name : name of the file to load
    #   file dir : folder directory to file to load
    #required to call "create track"
    def load_track(self, file_name, file_dir):
        file = TextFile(file_name, file_dir)
        self.track_name = file_name.replace(".txt", "")

        track_structure = file.read_serialised()

        self.set_structure(track_structure)

    #Save the current track on the screen
    #   file_name : name of the file to save the track in
    #   file_dir : the folder directory to save the track to
    #returns the path the file was created
    def save_track(self, file_name="", file_dir=""):
        if file_name == "":
            file_name = self.track_name + ".txt"
        if file_dir == "":
            file_dir = "./output/"

        file = TextFile(file_name, file_dir)
        file.write_serialised(self.track_structure.get_list())
        return file_dir + file_name

    #Remove the most recently placed piece
    def undo_piece(self):
        piece = self.track_pieces.pop()
        piece_structure = self.track_structure.pop()

        self.layer.remove_objects(tags=piece.tags)
        return piece


    def get_pieces(self):
        return self.track_pieces

    def update(self, events):

        #Undo when pressed key
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.undo_piece()
