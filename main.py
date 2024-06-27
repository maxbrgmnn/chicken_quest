# /// script
# dependencies = [
#  "pytmx",
#  "pygame-ce",
#  "pyscroll",
# ]
# ///



import sys
import asyncio
from data import Data
from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from debug import debug
from ui import UI
from timer import Timer
from menu import Menu
from enemies import *
from groups import *
from player import *
from sprites import *
import pytmx




from support import *
class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Chicken Quest')
        self.clock = pygame.time.Clock()
        self.import_assets()
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)

        self.gravity_delay = Timer(2000)
        self.gravity_delay.activate()




        self.tmx_maps = {0: load_pygame("Data/level1.tmx")}
        self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.data, self.level_sounds, self.level_particles)

        self.menu_active = True
        self.menu = Menu(
            self.display_surface,
            self.menu_background_frames,
            self.menu_button_normal,
            self.menu_button_hover
        )

    def import_assets(self):
        self.level_frames = {
            'saw' :import_folder('Graphics', 'saw', 'animation'),
            'player': import_sub_folders('Graphics', 'player'),
            'chicken1' : import_folder('Graphics', 'Chicken Walks'),
            'MeowKnight': import_folder('Graphics', 'Meow Knight'),
            'tooth': import_folder('Graphics', 'enemies', 'tooth'),
            'shell': import_sub_folders('Graphics', 'enemies', 'shell'),
            'pearl': import_image('Graphics', 'enemies', 'bullets', 'pearl1'),
            'items': import_sub_folders( 'Graphics', 'items'),
            'particle1': import_folder( 'Graphics', 'effects','particle'),
            'goal': import_folder( 'Graphics','ui', 'goal'),
            'bat': import_sub_folders( 'Graphics', 'enemies', 'bat'),
            'shroom': import_sub_folders( 'Graphics', 'enemies', 'shroom'),


        }
        self.font = pygame.font.Font(join('Graphics','ui', 'runescape_uf.ttf'), 30)
        self.ui_frames = {
            'heart': import_folder( 'Graphics','ui', 'heart'),
            'coin': import_image('Graphics','ui', 'coin'),

        }
        # soundstuff

        music_sound = pygame.mixer.Sound(join('Audio', 'blade.ogg'))
        music_sound.play()

        self.level_sounds = {

            'jump': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'hit': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'coin': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'blade': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'power up': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'chicken call': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'sword': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'schwing': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'flap': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'gas': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'air swing': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'bat': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'flap': pygame.mixer.Sound(join('Audio', 'blade.ogg')),
            'wall': pygame.mixer.Sound(join('Audio', 'blade.ogg')),




        }
        self.level_particles = {
            'effects': import_sub_folders('Graphics', 'effects', 'particles')
        }
        # Load menu assets
        self.menu_background_frames = import_folder('Graphics', 'ui', 'title screen')
        self.menu_background_frames = [pygame.transform.scale(frame, (WINDOW_WIDTH, WINDOW_HEIGHT)) for frame in self.menu_background_frames]
        self.menu_button_normal = import_image('Graphics', 'ui', 'button')
        self.menu_button_hover = import_image('Graphics', 'ui', 'button-active')

    def reset_game(self):
        # Reset player health, position, and other game states
        self.data.reset()  # Assuming Data class has a reset method to reset the game state
        self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.data, self.level_sounds, self.level_particles)
        self.gravity_delay.activate()

    def update_player_gravity(self):

        global PLAYER_GRAVITY
        keys = pygame.key.get_pressed()
        #print('I am Updating')

        # Check if the G key (pygame.K_g) is pressed
        if keys[pygame.K_g]:

            PLAYER_GRAVITY = 1000
        if not self.gravity_delay.active:
            PLAYER_GRAVITY = 1200

    async def run(self):
        while True:
            dt=self.clock.tick(60) / 1000
            #print(self.level_particles)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.menu_active:
                result = self.menu.update(dt)
                if result == 'start_game':
                    self.menu_active = False
                self.menu.draw()
            else:
                self.current_stage.run(dt)
                self.ui.update(dt)
                self.update_player_gravity()
                #print(PLAYER_GRAVITY)

                #debug(self.data.health)
                if self.data.health <= 0:
                    debug('YOU LOST')
                    #pygame.time.wait(2000)
                    self.reset_game()

                if self.gravity_delay.active:
                    #print('TIMER TIMER TIMER')
                    pass
                self.gravity_delay.update()

            await asyncio.sleep(0)

            pygame.display.update()


async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
