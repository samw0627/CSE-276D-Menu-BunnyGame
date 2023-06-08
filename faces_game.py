# from facialExpression import facialExpression
# from touchPad import touchPad
# from sound import sound
import pygame
from pygame import mixer
from pygame.locals import *
from utils import *
import sys
import os
from buttons import menuButton
import menu as mainMenu
import RPi.GPIO as GPIO  




class facialExpression:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.happy = {}
        self.silly = {}
        self.curious = {}
        self.smile = {}
        self.storeFaces()
        
    def storeFaces(self):
        dir = os.getcwd()+self.dir_path
        for img_path in os.listdir(dir):
            img = os.path.join(dir, img_path)
            if os.path.isfile(img):
                # file_name, _ = os.path.splitext(img)
                if 'happy' in img:
                    if '1' in img:
                        self.happy[OPEN] = img
                    else:
                        self.happy[BLINK]= img
                    
                elif 'silly' in img:
                    if '1' in img:
                        self.silly[OPEN] = img
                    else:
                        self.silly[BLINK]= img
                elif 'curious' in img:
                    if '1' in img:
                        self.curious[OPEN] = img
                    else:
                        self.curious[BLINK]= img
                else:
                    if '1' in img:
                        self.smile[OPEN] = img
                    else:
                        self.smile[BLINK]= img
    
    def getHappyFace(self):
        return self.happy
    def getSillyFace(self):
        return self.silly
    def getCuriousFace(self):
        return self.curious
    def getSmileFace(self):
        return self.smile
    
import os
from utils import *

class sound:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.happy = None
        self.silly = None
        self.curious = None
        self.smile = None
        self.storeSound()
    
    def storeSound(self):
        dir = os.getcwd() + self.dir_path 
        for Sound_path in os.listdir(dir):
            Sound = os.path.join(dir,Sound_path)
            if os.path.isfile(Sound):
                if 'happy' in Sound:
                    self.happy = Sound
                elif 'silly' in Sound:
                    self.silly = Sound
                elif 'curious' in Sound:
                    self.curious = Sound
                else:
                    self.smile = Sound
            
    def getHappySound(self):
        return pygame.mixer.Sound(self.happy)
    def getSillySound(self):
        return pygame.mixer.Sound(self.silly)
    def getCuriousSound(self):
        return pygame.mixer.Sound(self.curious)
    def getSmileSound(self):
        return pygame.mixer.Sound(self.smile)

class touchPad:
    def __init__(self):
        self.state = HOME
    
    #TODO: getting the state from the touch sensor   
    def setState(self):
        pass
        
    def getState(self):
        return self.state

class control:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self._display = None
        self.size = self.width, self.height = WIDTH, HEIGHT
    
        self._count = 0
        self.faces = facialExpression(FACE_IMG_DIR)
        self.touch = touchPad()
        self.sound = sound(FACES_SOUND_DIR)
        
        self._face = None
        self.display_face = None
        self.face_count = 0
        self.home_state = True
        
        self._mixer = None

        # menu button
        self.menuButtonObj = menuButton("test_hamburg_menu.png")
        
        
    def on_init(self):
        pygame.init()
        
        self._display = pygame.display
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
                                                    
        GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
        GPIO.setup(21, GPIO.IN)    # set GPIO 21 as input  
        GPIO.setup(20, GPIO.IN)    # set GPIO 20 as input  
        
        self._running = True
        
        self.reset_state()  
        
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    
        elif event.type == pygame.KEYDOWN:
            
            # if event.key == pygame.K_a:
            #     self._face = self.faces.getSillyFace()
            #     pygame.mixer.Sound.play(self.sound.getSillySound())
            #     pygame.mixer.music.stop()
            #     # self._mixer.load(self.sound.getSillySound())
            #     # self._mixer.play(2)
                
            # elif event.key == pygame.K_s:
            #     self._face = self.faces.getCuriousFace() 
            #     pygame.mixer.Sound.play(self.sound.getCuriousSound())
            #     pygame.mixer.music.stop()
            #     # self._mixer.load(self.sound.getCuriousSound())
            #     # self._mixer.play(2)
            
            #Exit the game in fullscreen mode with escape key  
            if event.key == pygame.K_ESCAPE:
                self._running = False
                self.on_cleanup()
                
            # self.home_state = False 
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.menuButtonObj.button.collidepoint(mouse_pos):
                    self._running = False
                    mainMenu.main()
        
    def on_loop(self):
        #TODO: check for the input from touchPad
        if GPIO.input(21): # if port 21 == 1  
            print ("Port 21 is 1/GPIO.HIGH/True - left ear pressed")
            self._face = self.faces.getSillyFace()
            pygame.mixer.Sound.play(self.sound.getSillySound())
            pygame.mixer.music.stop()
            self.home_state = False
        elif GPIO.input(20): # if port 20 == 1  
            print ("Port 20 is 1/GPIO.HIGH/True - right ear pressed")
            self._face = self.faces.getCuriousFace()
            pygame.mixer.Sound.play(self.sound.getCuriousSound())
            pygame.mixer.music.stop()
            self.home_state = False 
        else:  
            print ("Nothing is pressed") 
        
        if not self.home_state:
            self._count += 1     
            if self._count == EXPRESSION_DURATION:
                self.home_state = True
                self.reset_state()
                
        # self._mixer.queue(self.sound.getSmileSound())
                
    def reset_state(self):
        self._face = self.faces.getHappyFace() 
        pygame.mixer.Sound.play(self.sound.getHappySound())
        pygame.mixer.music.stop()
        self._count = 0
        
        
    #Render the facial expression onto screen
    def on_render(self):
        self.anime_faces()
        self._display_surf.blit(self.display_face, TOP_LEFT)
        self._display_surf.blit(self.menuButtonObj.img, self.menuButtonObj.img.get_rect(center = self.menuButtonObj.button.center))
        self._display.update()
    
    def anime_faces(self):
        if self.face_count > OPEN_DURATION:
            self.display_face = pygame.image.load(self._face[BLINK])
            if self.face_count > OPEN_DURATION + BLINK_DURATION:
                self.face_count = 0
        else:
            self.display_face = pygame.image.load(self._face[OPEN])
        self.face_count += 1
        
    def on_cleanup(self):
        pygame.quit()
        sys.exit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    # faces = facialExpression(FACE_IMG_DIR)
    control = control()
    control.on_execute()



