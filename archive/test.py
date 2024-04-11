import pygame, random

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

room_size = (2000,2000)
win = pygame.display.set_mode((800,600))
pygame.display.set_caption("My Project")

game_exit = False

win.fill(BLUE)
pygame.display.update()

'''
This system alows for camera movement
Works by using two coordinate systems:
    - Global position = Normal pygame coordiantes
    - Screen position = Coordinate relative to the centre of the window
    
Screen position should be used for drawing.
Global position should be used for movement, collision, etc.


Screen position = obj.x - screen.x + offset (usually screen centre)
Subtracting the screen x makes the object relative to the camera.

'''
class Vector():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get(self):
        return self.x, self.y

    def set(self, x, y):
        self.x = x
        self.y = y

    

class Camera():
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        

class Rectangle():
    def __init__(self, xpos, ypos, size, col):
        self.screen_pos = Vector(xpos - cam.xpos, ypos - cam.ypos)
        self.global_pos = Vector(xpos, ypos)
        self.size = size
        self.col = col

    def update(self):
        self.screen_pos.set(self.global_pos.x - cam.xpos + 400, self.global_pos.y - cam.ypos + 300)
        

    def collide_check(self, pos):
        _xpos = self.global_pos.x
        _ypos = self.global_pos.y
        if pos.x < _xpos + self.size and pos.x > _xpos and pos.y < _ypos + self.size and pos.y > _ypos:
            return True
    
    def draw(self):
        pygame.draw.rect(win, (self.col[0]//2, self.col[1]//2, self.col[2]//2), [*self.global_pos.get(), self.size, self.size])
        pygame.draw.rect(win, self.col, [*self.screen_pos.get(), self.size, self.size])

def point_check(pos, objs):
    for obj in objs:
        if obj.collide_check(pos):
            return True
    return False
        
        
cam = Camera(400,300)
recs = []
for i in range(100):
    recs.append(Rectangle(random.randint(0,2000), random.randint(0,2000), 50, (255,0,0)))

cam_rec = Rectangle(cam.xpos, cam.ypos, 5, (0,255,0))
cam_vel = Vector(0,0)

while game_exit == False:
    win.fill((0,0,255))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            game_exit = True

    keys = pygame.key.get_pressed()

    cam_vel.x = 0
    cam_vel.y = 0
    if keys[pygame.K_RIGHT]:
        cam_vel.x = 10 * 1/60
        #cam.xpos += 
    if keys[pygame.K_UP]:
        cam_vel.y = -10 * 1/60
    if keys[pygame.K_DOWN]:
        cam_vel.y = 10 * 1/60
    if keys[pygame.K_LEFT]:
        cam_vel.x = -10 * 1/60

    if point_check(Vector(cam_vel.x + cam.xpos, cam.ypos), recs) == False:
        cam.xpos += cam_vel.x
    if point_check(Vector(cam.xpos, cam_vel.y + cam.ypos), recs) == False:
        cam.ypos += cam_vel.y
    
    cam_rec.global_pos.set(cam.xpos, cam.ypos)
    cam_rec.draw()
    cam_rec.update()


    #pygame.draw.line(win, (255,255,0), room_size[0], room_size[1])
    

    for rec in recs:
        rec.draw()
        rec.update()

    
    pygame.display.update()

pygame.quit()
