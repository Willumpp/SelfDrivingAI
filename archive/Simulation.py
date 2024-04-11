import pygame
import CustomStructures as cs
import math

def sign(val):
    if val < 0:
        return -1
    if val > 0:
        return 1
    
    return 0

#Assumed global settings
class Settings:
    def __init__(self):
        self.maximum_velocity = 300
        self.acceleration_mag = 10
        self.decelleration_mag = 1000
        self.turn_velocity = 1000
        self.vehicle_width = 50
        self.vehicle_height = 25

class Camera():
    def __init__(self, xpos, ypos):
        self.global_pos = cs.Vector(xpos, ypos)

class Vehicle:
    def __init__(self, xpos, ypos, direction, width, height, colour, max_velocity, cam):
        self.global_pos = cs.Vector(xpos, ypos) #Where it is in the world (used for movement, collisions etc)
        self.__screen_pos = cs.Vector(xpos, ypos) #Where it is on the screen (relative to camera)
        self.direction = direction
        self.__width = width
        self.__height = height
        self.colour = colour
        self.visible = True
        self.max_velocity = max_velocity
        self.cam = cam

        self.velocity = cs.Vector(0, 0)
        self.acceleration = cs.Vector(0, 0)
        self.deceleration = cs.Vector(0, 0)

        self.surface = pygame.Surface((width, height)) #Create the rect as a surface, this allows rotation
        #Set the background colour of the surface, this removes a coloured background in rotation
        self.surface.set_colorkey((255, 255, 255)) 

        self.moving = False

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        _acc = self.acceleration
        _dcc = self.deceleration

        self.direction = math.atan2((self.__screen_pos.y-mouse_pos[1]), (mouse_pos[0]-self.__screen_pos.x))

        self.__screen_pos.set_pos(self.global_pos.x - self.cam.global_pos.x + window_size[0]/2, self.global_pos.y - self.cam.global_pos.y + window_size[1]/2)

        #Movement psuedocode:
        _acc.x = math.cos(self.direction) * settings.acceleration_mag * delta_time
        _acc.y = math.sin(self.direction) * settings.acceleration_mag * delta_time

        #new (from pseudo)
        #_dcc.x = math.cos(self.direction - math.pi) * settings.decelleration_mag * delta_time
        #_dcc.y = math.sin(self.direction - math.pi) * settings.decelleration_mag * delta_time

        if True:
            if self.moving == True:
                if self.velocity.get_mag() < settings.maximum_velocity:
                    #self.velocity.x += _acc.x
                    #self.velocity.y += _acc.y
                    self.velocity = self.velocity + _acc
                else:
                    self.velocity.x = settings.maximum_velocity * math.cos(self.direction) * sign(self.velocity.x)
                    self.velocity.y = settings.maximum_velocity * math.sin(self.direction) * sign(self.velocity.y)
            else:
                #if self.velocity.get_mag() > 0: #Issue here
                # if self.velocity.get_mag() > 0:
                #     self.velocity.x -= _acc.x 
                #     self.velocity.y -= _acc.y 
                # else:
                #     self.velocity.x = 0
                #     self.velocity.y = 0
                #Issue here
                # if self.velocity.x > 0:
                #     self.velocity.x -= _acc.x
                # else:
                #     self.velocity.x = 0
                # if self.velocity.y > 0:
                #     self.velocity.y -= 100 * delta_time
                # else:
                #     self.velocity.y = 0
                #Issue here
                # if self.velocity.get_mag() > 0:
                #     self.velocity.x += _dcc.x 
                #     self.velocity.y += _dcc.y 
                # else:
                #     self.velocity.x = 0
                #     self.velocity.y = 0
                #Damping, not subtraction
                # if abs(self.velocity.x) > 0:
                #     self.velocity.x *= 0.9
                # else:
                #     self.velocity.x = 0
                # if abs(self.velocity.y) > 0:
                #     self.velocity.y *= 0.9
                # else:
                #     self.velocity.y = 0
                if self.velocity.get_mag() > 0:
                    self.velocity = 0.9 * self.velocity

        self.global_pos.x += self.velocity.x
        self.global_pos.y -= self.velocity.y

    def draw(self):
        drawpos = self.get_drawpos()
        screenpos = self.get_screenpos()
        img_copy = pygame.transform.rotate(self.surface, self.direction*180/math.pi) #Save the image to get the width etc
        win.blit(img_copy, drawpos.get_pos())

        
        pygame.draw.circle(win, (255,0,0), screenpos.int().get_pos(), 2)

        # self.draw_bbox(img_copy.get_width(), img_copy.get_height())
        #self.draw_bbox()
        #pygame.draw.rect(win, self.colour, [*self.screen_pos.get_pos(), self.width, self.height])

    #This applies the matrix transformation on the width and height of the area
    #   take the size/corner of the object
    #   width, height = size.x, size.y
    #Rotating the object rotates the corner of the object also
    #   apply matrix (cos, -sin, sin, cos) * (width, height) to get vector of new corner (and therefore width, height)
    def get_width(self):
        return abs(self.__width * math.cos(self.direction)) + abs(self.__height * math.sin(self.direction))
        #return math.sqrt(self.width**2 + self.height**2) * math.sin(math.atan(self.width/self.height) + self.direction)

    def get_height(self):
        return abs(self.__width * math.sin(self.direction)) + abs(self.__height * math.cos(self.direction))

    def get_screenpos(self):
        return self.__screen_pos

    def get_drawpos(self):
        #if self.direction >= math.pi: self.direction = 0
        #self.direction = self.direction % (2*math.pi)

        #if 0 < self.direction < math.pi/2 or math.pi < self.direction < 3*math.pi/2:
        # if True:
        #     _w_offset = abs(self.width * math.cos(self.direction)) + abs(self.height * math.sin(self.direction))
        #     _h_offset = abs(self.width * math.sin(self.direction)) + abs(self.height * math.cos(self.direction))
        # else:
        #     _alpha = math.pi - self.direction
        #     _w_offset = self.width * math.cos(_alpha) + self.height * math.sin(_alpha)
        #     _h_offset = self.width * math.sin(_alpha) + self.height * math.cos(_alpha)
    
        return cs.Vector(self.__screen_pos.x - self.get_width()/2, self.__screen_pos.y - self.get_height()/2)


    # def draw_bbox(self, width, height):
        
    #     pygame.draw.lines(win, (255,0,0), True, [
    #         (self.screen_pos.x, self.screen_pos.y),
    #         (self.screen_pos.x + width, self.screen_pos.y),
    #         (self.screen_pos.x + width, self.screen_pos.y + height),
    #         (self.screen_pos.x, self.screen_pos.y + height)
    #     ])

    def draw_bbox(self):
        screen_pos = self.get_drawpos()
        width = self.get_width()
        height = self.get_height()

        pygame.draw.lines(win, (255,0,0), True, [
            (screen_pos.x, screen_pos.y),
            (screen_pos.x + width, screen_pos.y),
            (screen_pos.x + width, screen_pos.y + height),
            (screen_pos.x, screen_pos.y + height)
        ])


if __name__ == "__main__":
    pygame.init()


    room_size = (2000,2000)
    window_size = (1000, 900)
    win = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Simulation test")

    game_exit = False

    settings = Settings()
    cam = Camera(room_size[0]/2, room_size[1]/2)
    processes = []

    framerate = 60
    delta_time = 1 / framerate
    clock = pygame.time.Clock()

    

    for x in range(10):
        for y in range(10):

            vehicle = Vehicle(
                room_size[0]/2 + x * 10, 
                room_size[1]/2 + y * 10, 
                0, 
                settings.vehicle_width, 
                settings.vehicle_height, 
                (255, 0, 0), 
                settings.maximum_velocity, 
                cam)

            processes.append(vehicle)

    while game_exit == False:

        win.fill((255,255,255))

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                game_exit = True
            if event.type==pygame.KEYDOWN:
                if event.type == pygame.K_SPACE:
                    print("Found")

        keys=pygame.key.get_pressed()
        

        for obj in processes:
            obj.update()
            obj.draw()

            if keys[pygame.K_SPACE]:
                obj.moving = True
            else:
                obj.moving = False

        pygame.display.update()

        clock.tick(framerate)

    pygame.quit()
