import pygame as p
import pygame_gui as pg
import sys
import random
import math


FPS = 60
WIDTH = 1700
HEIGHT = 900
BOIDS = 20

PREDATOR_SPEED = 3
BOID_MAX_SPEED = 5
MAX_FORCE = 0.4

SEPERATION_FORCE_MULTI = 1
COHESION_FORCE_MULTI = 1
ALLIGNEMENT_FORCE_MULTI = 1

SEPERATION_NEIGHBORS = 30
COHESION_NEIGHBORS = 30
ALLIGNEMENT_NEIGHBORS = 30
WALL_NEIGHBORS = 100
PREDATOR_NEIGHBORS = 150


class wall(p.sprite.Sprite):
    def __init__(self,g,pos):
        self.game = g
        self._layer = 1
        self.groups = self.game.walls, self.game.all_sprites
        p.sprite.Sprite.__init__(self,self.groups)

        self.width = 50
        self.height = 50

        self.image = spritesheet("wall.png").get_sprite(0,0,self.width,self.height)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - self.width//2
        self.rect.y = pos[1] - self.height//2

    def update(self):
        pass

class boid(p.sprite.Sprite):
    def __init__(self,g,x,y):
        self.game = g
        self.groups = self.game.boids , self.game.all_sprites
        p.sprite.Sprite.__init__(self,self.groups)

        self.width = 15
        self.height = 15
        #self.image = spritesheet("boid.png").get_sprite(0,0,self.width,self.height)
        self.image = p.Surface((self.width, self.height))
        p.draw.circle(self.image, (255,255,255),(self.width/2,self.height/2),self.width/2)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        
        self.position = p.math.Vector2(x,y)
        self.velocity = p.math.Vector2(random.randint(-BOID_MAX_SPEED, BOID_MAX_SPEED),random.randint(-BOID_MAX_SPEED, BOID_MAX_SPEED))
        self.acceleration = p.math.Vector2(0,0)
        

    def flock(self):

        cohesion_neighbors = self.get_neighbors(COHESION_NEIGHBORS)
        aligenement_neighbors = self.get_neighbors(ALLIGNEMENT_NEIGHBORS)
        separation_neighbors = self.get_neighbors(SEPERATION_NEIGHBORS)
        wall_neigbors = self.get_close_walls(WALL_NEIGHBORS)

        alignement_force = self.alignement(aligenement_neighbors)
        cohesion_force = self.cohesion(cohesion_neighbors)
        separation_force = self.separation(separation_neighbors)
        wall_force = self.wall_seperation(wall_neigbors)
        predator_force = self.predator_seperation()

        self.acceleration += cohesion_force
        self.acceleration += alignement_force
        self.acceleration += separation_force
        self.acceleration += wall_force
        self.acceleration += predator_force

    def update(self):
        self.acceleration = p.math.Vector2(0,0)
        self.flock()

        self.velocity += self.acceleration
        #self.image = self.rotate_image()

        if self.velocity.x > BOID_MAX_SPEED:
                self.velocity.x = BOID_MAX_SPEED
        elif self.velocity.x < -BOID_MAX_SPEED:
            self.velocity.x = -BOID_MAX_SPEED

        if self.velocity.y > BOID_MAX_SPEED:
            self.velocity.y = BOID_MAX_SPEED
        elif self.velocity.y < -BOID_MAX_SPEED:
            self.velocity.y = -BOID_MAX_SPEED

    
        self.position += self.velocity
    
        
        self.edges()
        self.rect.x = self.position.x - self.width//2
        self.rect.y = self.position.y - self.height//2
        

    def alignement(self,neighbors):
        force = p.math.Vector2(0,0)

        if len(neighbors)>0:
            for i in neighbors:
                force += i.velocity

            force /= len(neighbors)
            if force.x != 0 and force.y != 0:  
                force = force.normalize()
            force = force * BOID_MAX_SPEED * ALLIGNEMENT_FORCE_MULTI
            force -= self.velocity
            
            if force.x > MAX_FORCE:
                force.x = MAX_FORCE
            elif force.x < -MAX_FORCE:
                force.x = -MAX_FORCE

            if force.y > MAX_FORCE:
                force.y = MAX_FORCE
            elif force.y < -MAX_FORCE:
                force.y = -MAX_FORCE

        return(force)


    def cohesion(self, neighbors):
        force = p.math.Vector2(0,0)

        if len(neighbors)>0:
            for i in neighbors:
                force += i.position

            force /= len(neighbors)
            force -= self.position  

            if force.x != 0 and force.y != 0:  
                force = force.normalize()

            force = force * BOID_MAX_SPEED * COHESION_FORCE_MULTI
            force -= self.velocity

            if force.x > MAX_FORCE:
                force.x = MAX_FORCE
            elif force.x < -MAX_FORCE:
                force.x = -MAX_FORCE

            if force.y > MAX_FORCE:
                force.y = MAX_FORCE
            elif force.y < -MAX_FORCE:
                force.y = -MAX_FORCE

        return(force)

    def separation(self, neighbors):
        force = p.math.Vector2(0,0)

        if len(neighbors)>0:
            for i in neighbors:
                dist = math.sqrt((self.position.x - i.position.x)**2 + (self.position.y - i.position.y)**2)
                if dist ==0:
                    dist = 0.000001
                diff = self.position - i.position
                diff /= (dist**2)
                force += diff
            
            force /= len(neighbors)
            if force.x != 0 and force.y != 0:  
                force = force.normalize()
            force = force * BOID_MAX_SPEED * SEPERATION_FORCE_MULTI
            force -= self.velocity

            if force.x > MAX_FORCE:
                force.x = MAX_FORCE
            elif force.x < -MAX_FORCE:
                force.x = -MAX_FORCE

            if force.y > MAX_FORCE:
                force.y = MAX_FORCE
            elif force.y < -MAX_FORCE:
                force.y = -MAX_FORCE
            
        return(force)
            
    def wall_seperation(self, neighbors):
        force = p.math.Vector2(0,0)

        if len(neighbors)>0:
            for i in neighbors:
                dist = math.sqrt((self.position.x - i.rect.x)**2 + (self.position.y - i.rect.y)**2)
                if dist ==0:
                    dist = 0.000001
                diff = self.position - p.math.Vector2(i.rect.x,i.rect.y)
                diff /= (dist**1.5)
                force += diff
            
            force /= len(neighbors)
            if force.x != 0 and force.y != 0:  
                force = force.normalize()
            force = force * BOID_MAX_SPEED
            force -= self.velocity

            if force.x > MAX_FORCE*1.25:
                force.x = MAX_FORCE*1.25
            elif force.x < -MAX_FORCE*1.25:
                force.x = -MAX_FORCE*1.25

            if force.y > MAX_FORCE*1.25:
                force.y = MAX_FORCE*1.25
            elif force.y < -MAX_FORCE*1.25:
                force.y = -MAX_FORCE*1.25
            
        return(force)
    
    def predator_seperation(self):
        force = p.math.Vector2(0,0)
        dist = math.sqrt((self.position.x - self.game.predator.rect.x)**2 + (self.position.y - self.game.predator.rect.y)**2)
        if dist < PREDATOR_NEIGHBORS:
            if dist == 0:
                dist = 0.000001
            force = (self.position - p.math.Vector2(self.game.predator.rect.x, self.game.predator.rect.y))/(dist**1.5)
        
        if force.x != 0 and force.y != 0:  
                force = force.normalize()
        force = force * BOID_MAX_SPEED

        if force.x > MAX_FORCE*1.5:
            force.x = MAX_FORCE*1.5
        elif force.x < -MAX_FORCE*1.5:
            force.x = -MAX_FORCE*1.5

        if force.y > MAX_FORCE*1.5:
            force.y = MAX_FORCE*1.5
        elif force.y < -MAX_FORCE*1.5:
            force.y = -MAX_FORCE*1.5
        
        return(force)
    
            
    def get_neighbors(self, radius):
        res = []
        for i in self.game.boids.sprites():
            if math.sqrt((self.position.x - i.position.x)**2 + (self.position.y - i.position.y)**2) <= radius and i!=self:
                res.append(i)
        return(res)
    
    def get_close_walls(self,radius):
        res = []
        for i in self.game.walls.sprites():
            if math.sqrt((self.position.x - i.rect.x)**2 + (self.position.y - i.rect.y)**2) <= radius:
                res.append(i)
        return(res)

    def edges(self):
        if self.position.x <430:
            self.position.x = WIDTH
        elif self.position.x >WIDTH:
            self.position.x = 430

        if self.position.y <0:
            self.position.y = HEIGHT
        elif self.position.y >HEIGHT:
            self.position.y = 0

    def rotate_image(self):
        rect = self.image.get_rect() 
        angle = math.degrees(math.atan2(self.velocity.y - self.position.y, self.velocity.x - self.position.x) %2*math.pi)
        new_image = p.transform.rotate(self.image, -angle + self.angle)
        print(-self.angle + angle)
        self.angle = angle
        
        new_rect = rect.copy()
        new_rect.center = new_image.get_rect().center
        new_image = new_image.subsurface(new_rect).copy()
        return(new_image)
        

class Slider:
    def __init__(self,g,x,y,min,max,initValue,text):
        self.game = g
        self.initValue = initValue
        self.min = min
        self.max = max
        self.width = 200
        self.height = 30
        self.text = text
        self.rect = p.Rect((x,y),(self.width,self.height))
        self.textRect = p.Rect((x +self.width ,y), (self.width,self.height))
        self.sliderElement = pg.elements.UIHorizontalSlider(self.rect,self.initValue,(self.min,self.max),self.game.manager)
        self.textElement = pg.elements.UILabel(self.textRect, text, self.game.manager)
    
    def update(self):
        if self.sliderElement.left_button.held :
            self.sliderElement.current_value -= 0.1
        elif self.sliderElement.right_button.held :
            self.sliderElement.current_value += 0.1

        self.textElement.kill()
        self.textElement = pg.elements.UILabel(self.textRect, self.text + str(round(self.sliderElement.current_value,3)), self.game.manager)

        return self.sliderElement.current_value

    def reset(self):
        self.sliderElement.kill()
        self.sliderElement.current_value = 0.5
        self.sliderElement = pg.elements.UIHorizontalSlider(self.rect,self.initValue,(self.min,self.max),self.game.manager)

class button:
    def __init__(self,g,x,y):
        self.game = g
        self.width = 100   
        self.height = 30
        rect = p.Rect((x,y),(self.width,self.height))
        self.button = pg.elements.UIButton(rect, text="Reset",manager=self.game.manager)

class predator(p.sprite.Sprite):
    def __init__(self,g,x,y):
        self.game = g
        self.groups = self.game.all_sprites
        p.sprite.Sprite.__init__(self,self.groups)

        self.width = 20
        self.height = 20
        self.image = p.Surface((self.width, self.height))
        p.draw.circle(self.image, (100,255,100),(self.width/2,self.height/2),self.width/2)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x - self.width/2
        self.rect.y = y - self.height /2

        self.x_speed = 0
        self.y_speed = 0

    def update(self):
        self.keys()
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

    def keys(self):
        self.x_speed = 0
        self.y_speed = 0
        keys = p.key.get_pressed()
        if keys[p.K_z] and self.rect.y >0:
            self.y_speed -= PREDATOR_SPEED
        if keys[p.K_s] and self.rect.y <HEIGHT - self.height:
            self.y_speed += PREDATOR_SPEED
        if keys[p.K_q] and self.rect.x >410:
            self.x_speed -= PREDATOR_SPEED
        if keys[p.K_d] and self.rect.x <WIDTH - self.width:
            self.x_speed += PREDATOR_SPEED
            
        

class spritesheet:
    def __init__(self,file):
        self.image = p.image.load(file)

    def get_sprite(self,x,y,width,height):
        sprite = p.Surface([width,height])
        sprite.blit(self.image, (0,0),(x,y,width,height))
        sprite.set_colorkey((255,255,255))
        return(sprite)

class game:
    def __init__(self):
        p.init()
        self.screen = p.display.set_mode((WIDTH,HEIGHT))
        self.manager = pg.UIManager((WIDTH, HEIGHT))
        p.display.set_caption("Flocking Simulation")
        self.clock = p.time.Clock()
        self.running = True
        self.drawing = False


    def new(self):
        self.walls = p.sprite.LayeredUpdates()
        self.boids = p.sprite.LayeredUpdates()
        self.all_sprites = p.sprite.LayeredUpdates()
        for i in range(0,BOIDS):
            boid(self, random.randint(0,WIDTH), random.randint(0,HEIGHT))

        self.coheison_slider = Slider(self,5,200,0,1,0.5,"Coheision: ")
        self.seperation_slider = Slider(self,5,140,0,1,0.5, "Separation: ")
        self.allignement_slider = Slider(self,5,80,0,1,0.5, "Allignement: ")
        self.reset_button = button(self,60,240)
        self.predator = predator(self,WIDTH//2, HEIGHT//2)

    def reset(self):
        self.coheison_slider.reset()
        self.seperation_slider.reset()
        self.allignement_slider.reset()
        for wall in self.walls.sprites():
            wall.kill()

    def events(self):
        for event in p.event.get():
            if event.type == p.QUIT:
                self.running = False
                p.quit()
                sys.exit()

            if event.type == pg.UI_BUTTON_PRESSED:
                if event.ui_element == self.reset_button.button:
                    self.reset()
            
            elif event.type == p.MOUSEBUTTONDOWN:
                self.drawing = True
            elif event.type == p.MOUSEBUTTONUP:
                self.drawing = False
            
            self.manager.process_events(event)

    def update(self):
        self.addwalls()
        global ALLIGNEMENT_FORCE_MULTI
        global COHESION_FORCE_MULTI
        global SEPERATION_FORCE_MULTI
        
        self.all_sprites.update()

        COHESION_FORCE_MULTI = self.coheison_slider.update()
        SEPERATION_FORCE_MULTI = self.seperation_slider.update()
        ALLIGNEMENT_FORCE_MULTI = self.allignement_slider.update()

    def addwalls(self):
        if self.drawing:
            mouse_pos = p.mouse.get_pos()
            if mouse_pos[0] > 430:
                wall(self,mouse_pos)

    def draw(self):
        self.screen.fill((50,50,50))
        p.draw.rect(self.screen,(255,255,255),p.Rect(410,0,5,HEIGHT))
        self.all_sprites.draw(self.screen)
    
        self.manager.update(self.clock.tick(FPS)/1000.0)
        self.manager.draw_ui(self.screen)
        p.display.update()
    
    def main(self):
        while(self.running):
            self.events()
            self.update()
            self.draw()


g = game()
g.new()
g.main()

