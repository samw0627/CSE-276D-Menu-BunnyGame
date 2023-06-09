import pygame
import os
import random
import sys
from pygame import mixer
from pygame.locals import *
from utils import *
from buttons import menuButton
import menu as mainMenu
import RPi.GPIO as GPIO  


clock = pygame.time.Clock() #set up the clock
_display_surf = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
GPIO.setup(21, GPIO.IN)    # set GPIO 21 as input  
GPIO.setup(20, GPIO.IN)    # set GPIO 20 as input                                      

#A class that stores the bunny image and rectangle object
class bunny:
    def __init__(self, speed):
        self.img = pygame.image.load(BUNNY_IMG)
        self.rect = self.img.get_rect()
        self.x_pos = STARTING_POS_X_BUNNY
        self.y_pos = STARTING_POS_Y_BUNNY
        self.speed = speed
    
    #method that moves the bunny left and right
    def move(self, direction):
        if direction == RIGHT:
            self.x_pos += self.speed
        else:
            self.x_pos -= self.speed
        self.rect.topleft = (self.x_pos, self.y_pos)
    
    #method that prevents bunny from moving out of screen        
    def checkBorder(self):
        if self.x_pos < 0:
            self.x_pos = 0
        if self.x_pos > (WIDTH-BUNNY_SIZE*2):
            self.x_pos = WIDTH-BUNNY_SIZE*2
    
    #render the bunny on screen 
    def draw(self, screen):
        screen.blit(self.img, (self.x_pos, self.y_pos))

class meteor:
    def __init__(self, speed):
        self.speed = speed
        self.img = pygame.image.load(METEOR_IMG)
        self.rect = self.img.get_rect()
        self.x_pos = random.randint(0,WIDTH-METEOR_SIZE*2)
        self.y_pos = STARTING_POS_Y_METEOR
    
    def checkBorder(self):
        if self.y_pos > GROUND_POS_Y:
            self.reset()
    
    def reset(self):
        self.y_pos = 0
        self.x_pos = random.randint(0,WIDTH-METEOR_SIZE*2)
        
    def drop(self):
        self.y_pos += self.speed
        self.rect.topleft = (self.x_pos, self.y_pos)
    
    def draw(self, screen):
        screen.blit(self.img, (self.x_pos, self.y_pos))    
    
#A class that stores the carrot image and rectangle object   
class carrot:
    def __init__(self, speed):
        self.speed = speed
        self.img = pygame.image.load(CARROT_IMG)
        self.rect = self.img.get_rect()
        self.x_pos = random.randint(0,WIDTH-CARROT_SIZE*2)
        self.y_pos = STARTING_POS_Y_CARROT
    
    #check if carrot hits the ground
    def checkBorder(self):
        if self.y_pos > GROUND_POS_Y:
            self.reset()
    
    #reset the carrot to starting positions
    def reset(self):
        self.y_pos = 0
        self.x_pos = random.randint(0,WIDTH-CARROT_SIZE*2)
    
    #setting the position of the carrot based on the dropping speed  
    def drop(self):
        self.y_pos += self.speed
        self.rect.topleft = (self.x_pos, self.y_pos)
    
    #render the carrot on corresponding position
    def draw(self, screen):
        screen.blit(self.img, (self.x_pos, self.y_pos))

#A class that stores the number of points a user scores
class score_board:
    def __init__(self):
        self.scores = 0
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.img = pygame.image.load(SCORE_BOARD_IMG)
        self.text = None
        self.rect = None
    
    #render the score board 
    def draw(self, screen):
        text = self.font.render(':' + str(self.scores), True, CARROT_COLOR)
        rect = text.get_rect()
        rect.center = (900, 40)
        screen.blit(text, rect)
        screen.blit(self.img, (860, 20))

#A class that stores the number of lives users have 
#reset the game if the number of hearts equals to zero
class hearts:
    def __init__(self, num_hearts):
        self.num_hearts = num_hearts     
        self.img = pygame.image.load(HEART_IMG)
        
    def draw(self, screen):
        for i in range(self.num_hearts):
            screen.blit(self.img, (STARTING_POS_X_HEART + HEART_SIZE*i, STARTING_POS_Y_HEART))

#A control class that represents the pygame 
class control:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = WIDTH, HEIGHT
        
        #set the size of the window 
        self._display_surf = _display_surf
        pygame.display.set_caption(GAME_NAME)
        
        #create all the objects of the game 
        self.background = pygame.image.load(BACKGROUND_IMG)  
        self.bunny = bunny(BUNNY_SPEED)
        self.carrots = [carrot(random.randint(MIN_CARROT_SPEED, MAX_CARROT_SPEED)) for i in range(NUMBER_CARROT)]
        self.carrots_rect = [carrot.rect for carrot in self.carrots]
        self.meteors = [meteor(random.randint(MIN_METEOR_SPEED, MAX_METEOR_SPEED)) for i in range(NUMBER_METEOR)]
        self.meteors_rect = [meteor.rect for meteor in self.meteors]
        self.hearts = hearts(NUM_HEARTS)
        self.score_board = score_board()
        self._mixer = None
        self.points = 0
        
        # create button menu object
        self.menuButtonObj = menuButton("test_hamburg_menu.png")
        
    def on_init(self):
        self._running = True
 
    #detects all the keyboard/touch screen input to the game 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.on_cleanup()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_cleanup()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos  # gets mouse position
            if self.menuButtonObj.button.collidepoint(mouse_pos):
                self._running = False
                mainMenu.main()
            
    def on_loop(self):
        # #Debugging code, used with keyboard input
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     self.bunny.move(LEFT)
        # if keys[pygame.K_RIGHT]:
        #     self.bunny.move(RIGHT)
        
        
        # Based on the input from raspberry pi GPIO pins
        # move the bunny to left or right 
        if GPIO.input(21): # if port 21 == 1  
            print ("Port 21 is 1/GPIO.HIGH/True - left ear pressed")
            self.bunny.move(LEFT)
        elif GPIO.input(20): # if port 20 == 1  
            print ("Port 20 is 1/GPIO.HIGH/True - right ear pressed")
            self.bunny.move(RIGHT)
        else:  
            print ("Nothing is pressed")  
            
        #check if bunny is still inside the boarder
        self.bunny.checkBorder()
        #move the carrots while checking it's boarder
        for carrot in self.carrots:
            carrot.drop()
            carrot.checkBorder()
        
        #move the meteor while checking it's boarder
        for meteor in self.meteors:
            meteor.drop()
            meteor.checkBorder()
        
        #collision test for the bunny and the carrots
        collide_idx = self.bunny.rect.collidelist(self.carrots_rect)
        if collide_idx != -1:
            self.score_board.scores += 1 #increae the score if bunny catches carrots
            self.carrots[collide_idx].reset()
            
        #collision test for the bunny and the meteors
        collide_idx = self.bunny.rect.collidelist(self.meteors_rect)
        if collide_idx != -1:
            self.hearts.num_hearts -= 1 #decrease the heart number if meteor hits bunny
            self.meteors[collide_idx].reset()

    def on_render(self):
        #render all the images of the game based on given positions
        self._display_surf.blit(self.background, TOP_LEFT)
        self.score_board.draw(self._display_surf)
        for carrot in self.carrots:
            carrot.draw(self._display_surf) 
        for meteor in self.meteors:
            meteor.draw(self._display_surf) 
        self.bunny.draw(self._display_surf)
        self.hearts.draw(self._display_surf)
        self._display_surf.blit(self.menuButtonObj.img, self.menuButtonObj.img.get_rect(center = self.menuButtonObj.button.center))
        pygame.display.flip()
 
    #function that call other functions once user start the game
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        #enter a while loop once the game starts
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            clock.tick(FPS)
            #Reset the game after all the hearts running out
            if self.hearts.num_hearts == 0:
                self._running = False
        
        show_menu(0,self.score_board.scores)    

    #exist pygame 
    def on_cleanup(self):
        pygame.quit()
        self._running = False
        sys.exit()

#start page for the game
def show_menu(num_hearts,scores):
    running = True
    menuButtonObj = menuButton("test_hamburg_menu.png")
    while running:
        #render the background and the start text
        _display_surf.fill(MENU_BACKGROUND)
        font = pygame.font.Font('freesansbold.ttf', 30)
        
        if num_hearts == 0:#distinguish a new start from a restart 
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(scores), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (WIDTH // 2, HEIGHT // 2 + 50)
            _display_surf.blit(score, scoreRect)
            
        else: #only display the instruction in a new start 
            _display_surf.fill((135, 206, 235))
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        
        #render all the text on screen
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, HEIGHT // 2)
        _display_surf.blit(text, textRect)
        _display_surf.blit(pygame.image.load(BUNNY_IMG), (WIDTH // 2 - 20, HEIGHT // 2 - 140))
        _display_surf.blit(menuButtonObj.img, menuButtonObj.img.get_rect(center = menuButtonObj.button.center))
        pygame.display.update()
        #Add delay for displaying the score 
        pygame.time.wait(DISPLAY_DURATION)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #if user pressed the screen 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position
                # if user pressed the menu button 
                if menuButtonObj.button.collidepoint(mouse_pos):
                    mainMenu.main() #go back to menu 
                else:
                    _control = control()
                    _control.on_execute()  
                    
        clock.tick(FPS)
     
    pygame.quit()
    sys.exit()

       
# if __name__ == "__main__" :
#     show_menu(NUM_HEARTS, 0)  