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

asyncio.run(main())

from settings import *
from sprites import Sprite, AnimatedSprite, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import *
from os.path import join
from timer import Timer
from support import *

class Level:
    def __init__(self, tmx_map, level_frames, data, level_sounds, level_particles):
        self.display_surface = pygame.display.get_surface()
        self.data = data

        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.goal_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()

        self.level_frames = level_frames
        self.level_sounds = level_sounds
        self.particle_frames = level_frames['particle1']
        self.particles = level_particles


        self.hit_timer = Timer(2000)

        self.setup(tmx_map, level_frames)


        self.camerashake = False
        self.goal_reached = False



        # Load the goal reached image
        self.goal_image = pygame.image.load(join('Graphics','ui','you-win.png')).convert_alpha()
        self.goal_image_rect = self.goal_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))


    def setup(self, tmx_map, level_frames):

        #tiles
        for layer in ['Behind','BG', 'layer1', 'layer2']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                z = Z_LAYERS[layer]
                groups = (self.all_sprites)
                if layer == 'layer1':

                    # Only 'layer1' should be part of collision handling
                    Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites), z)
                else:
                    # Other layers like 'BG' should not have collisions
                    Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites,), z)
        #objects
        for obj in tmx_map.get_layer_by_name('objects'):
            #print(f"Object name: {obj.name}")
            if obj.name == 'chicken1':
                self.player = Player(
                    pos = (obj.x, obj.y),
                    groups = self.all_sprites,
                    collision_sprites = self.collision_sprites,
                    frames = level_frames['player'],
                    sounds = self.level_sounds,
                    data = self.data,
                    particles = self.particles)
            elif obj.name == 'goal':
                frames = level_frames['goal']
                AnimatedSprite((obj.x, obj.y), frames, (self.all_sprites, self.goal_sprites))


            else:
                frames = level_frames[obj.name]
                #print(f"{obj.name} frames count: {len(frames)}")
                AnimatedSprite((obj.x, obj.y), frames, (self.all_sprites, self.damage_sprites))

        #enemies
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'tooth':
                Tooth((obj.x, obj.y), {'tooth': level_frames['tooth'], 'particle1': level_frames['particle1']}, (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collision_sprites)
            if obj.name == 'shell':
                Shell(
                    (obj.x,obj.y),
                    frames = level_frames['shell'],
                    groups = self.all_sprites,
                    reverse= obj.properties['reverse'],
                    player= self.player,
                    create_pearl = self.create_pearl)
            if obj.name == 'bat':
                Bat((obj.x, obj.y), level_frames['bat'], self.level_sounds, (self.all_sprites, self.damage_sprites, self.attack_sprites), self.player)
            if obj.name == 'shroom':
                Shroom((obj.x, obj.y), level_frames['shroom'], (self.all_sprites, self.damage_sprites), self.player)

        #items
        for obj in tmx_map.get_layer_by_name('Items'):
            Item(obj.name, (obj.x + TILE_SIZE/2,obj.y + TILE_SIZE/2),  level_frames['items'][obj.name], (self.all_sprites, self.item_sprites), self.data)

    def goal_collision(self):
        for sprite in self.goal_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                print('WIN WIN WIN WIN WIN WIN WIN')
                self.goal_reached = True

    def create_pearl(self, pos, direction):
        Pearl( pos, (self.all_sprites, self.damage_sprites, self.pearl_sprites), self.level_frames['pearl'], direction, 150)
    def pearl_collision(self):
        for sprite in self.collision_sprites:
            sprite = pygame.sprite.spritecollide(sprite, self.pearl_sprites, True)
            if sprite:
                ParticleEffectSprite((sprite[0].rect.center), self.particle_frames, self.all_sprites)



    def hit_collision(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                if hasattr(sprite, 'is_flickering') and sprite.is_flickering:
                    pass
                elif not self.player.block:
                    #print('player damage')
                    self.player.get_damage()
                    self.camerashake = True
                    self.level_sounds['chicken call'].play()
                    if hasattr(sprite, 'pearl'):
                        sprite.kill()
                        ParticleEffectSprite((sprite.rect.center), self.particle_frames, self.all_sprites)

    def item_collision(self):
        if self.item_sprites:
            #needs a better way of collision detection because sprite is too big
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                item_sprites[0].activate()
                self.level_sounds['power up'].play()
                ParticleEffectSprite((item_sprites[0].rect.center), self.particle_frames, self.all_sprites)

    def attack_collision(self):
        for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites() + self.attack_sprites.sprites():
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or\
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target and not self.hit_timer.active:
                ParticleEffectSprite((target.rect.centerx - 80, target.rect.centery),
                                     self.particles['effects']['blood'], self.all_sprites)
                target.reverse()

                self.hit_timer.activate()




    def run(self, dt):
        self.display_surface.fill('#1c061b')
        #print(self.particles)






        self.all_sprites.draw(self.player.hitbox_rect.center, self.camerashake)
        self.all_sprites.update(dt)
        self.pearl_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        self.goal_collision()
        self.camerashake = False
        self.hit_timer.update()
        if self.goal_reached:
            self.display_surface.blit(self.goal_image, self.goal_image_rect)

from settings import *
from support import*


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        self.bg_frames = []
        self.raw_frames = []
        self.scaled_frames = []
        self.import_bg()

    def import_bg(self):
        self.raw_frames = import_folder('Graphics','background')
        self.scaled_frames= [pygame.transform.scale(frame, (WINDOW_WIDTH*1.2, WINDOW_HEIGHT*1.5)) for frame in self.raw_frames]
        self.bg_frames = self.scaled_frames #[::-1]  # Reverse the list of frames

        print('bg frames:', self.bg_frames)




    def draw(self, target_pos, camera_shake):

        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        if camera_shake:
            shake_strength = 5  # or whatever fits your game
            parallax_x += random.randint(-shake_strength, shake_strength)
            parallax_y += random.randint(-shake_strength, shake_strength)

        layer_depth = 0.1  # Starting depth for the farthest layer
        for frame in self.bg_frames:
            parallax_x = self.offset.x * layer_depth
            layer_depth += 0.05  # Increase depth effect for closer layers

            # Draw the background frame multiple times to fill the screen horizontally
            for x in range(-1, int(WINDOW_WIDTH / frame.get_width()) + 5):
                self.display_surface.blit(frame, (x * frame.get_width() + parallax_x, -300))

        for sprite in sorted(self, key = lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_pos)

from settings import *

class Menu:
    def __init__(self, display_surface, background_frames, button_normal, button_hover):
        self.display_surface = display_surface
        self.background_frames = background_frames
        self.button_normal = button_normal
        self.button_hover = button_hover
        self.button_rect = self.button_normal.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.frame_index = 0
        self.animation_speed = 1

    def update(self, dt):
        # Update background animation
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.background_frames):
            self.frame_index = 0
        current_background = self.background_frames[int(self.frame_index)]

        # Draw background
        self.display_surface.blit(current_background, (0, 0))

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Check if mouse is over the button
        if self.button_rect.collidepoint(mouse_pos):
            self.display_surface.blit(self.button_hover, self.button_rect)
            if pygame.mouse.get_pressed()[0]:  # Check for left mouse button click
                return 'start_game'
        else:
            self.display_surface.blit(self.button_normal, self.button_rect)

        return 'menu'

    def draw(self):
        pygame.display.update()

from settings import *
from timer import Timer
from math import sin
from groups import AllSprites
from sprites import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, frames, sounds, data, particles):
        #general setup
        super().__init__(groups) #gets stuff from the sprite base class
        self.z = Z_LAYERS['layer1']
        self.level_sounds = sounds
        self.data = data

        #image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]

        #rects
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-90, -60)

        #particles
        self.particles = particles
        self.all_sprites = groups
        self.air = False






        self.old_rect=self.hitbox_rect.copy()



        #movement

        self.direction = vector()
        self.speed = PLAYER_SPEED

        #new movement variables
        self.max_speed = 400  # The maximum speed the player can reach
        self.acceleration = 500  # The rate of acceleration until reaching max speed
        self.current_speed = 0  # Starting speed of the player

        self.jump = False
        self.jump_height = 700
        self.attacking = False
        self.space = False
        self.space_was_true = False
        self.double_jump = False
        self.dash = False


        #collision
        self.collision_sprites = collision_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}

        self.block = False

        #timer
        self.timers = {
            'wall jump': Timer(400),
            'jump delay': Timer(250),
            'attack block' : Timer(500),
            'hit': Timer(400),
            'gravity-delay': Timer(2500),
            'db-jump-delay': Timer (200),
            'dash-delay': Timer (2000),


        }
        self.timers['gravity-delay'].activate()

    def update_jump_heigth(self):
        if self.space == True:
            self.start_time = pygame.time.get_ticks()
            self.space_was_true = True
        if self.space == False and self.space_was_true == True:
            print('second phase init')
            self.end_time = pygame.time.get_ticks()
            self.space_duration = self.end_time - self.start_time
            self.space_was_true = False

            # Define the maximum duration that corresponds to the maximum output value
            max_duration = 1500  # maximum time in milliseconds
            max_output_value = 1000  # maximum value in the mapped range

            # Map the duration to the range 0 to 1000
            if self.space_duration > max_duration:
                self.space_duration = max_output_value


            #does not work so reset this until it works


            self.jump_height = 700


    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0,0)
        if not self.timers['wall jump'].active:

            if keys[pygame.K_RIGHT]:
                input_vector.x += 1
                self.facing_right = True

            if keys[pygame.K_LEFT]:
                input_vector.x -= 1
                self.facing_right = False
            if keys[pygame.K_x]:
                self.attack()
            self.direction.x = input_vector.normalize().x if input_vector else 0

        if keys[pygame.K_SPACE]:
            self.jump = True
            self.timers['wall jump'].activate()
            self.space = True
            self.level_sounds['flap'].set_volume(0.2)
            self.level_sounds['flap'].play()

            #print('selfjump is true')
        else:
            self.space = False

        if keys[pygame.K_p]:
            ParticleEffectSprite((self.hitbox_rect.midbottom), self.particles['effects']['test'], self.all_sprites)

            #print(self.particles)

        if keys[pygame.K_b]:
            self.block = True
        else:
            self.block = False

        if keys[pygame.K_d]:
            self.dash = True
            self.level_sounds['schwing'].set_volume(0.5)
            self.level_sounds['schwing'].play()
        else:
            self.dash = False

        #not working, needs to be removed later
        if not self.timers['gravity-delay'].active:
            set_player_gravity(1300)  # This changes the gravity globally in settings
            PLAYER_GRAVITY = 1111
            #print('Gravity set to 1000')

    def attack(self):
        if not self.timers['attack block'].active:
            self.attacking = True
            if self.on_surface['floor']:
                self.level_sounds['sword'].set_volume(0.5)
                self.level_sounds['sword'].play()
            else:
                self.level_sounds['air swing'].set_volume(0.5)
                self.level_sounds['air swing'].play()
            self.frame_index = 0
            self.timers['attack block'].activate()

    def move(self, dt):
        # Horizontal movement with acceleration
        if self.direction.x != 0:
            if (self.direction.x > 0 and self.current_speed < 0) or (self.direction.x < 0 and self.current_speed > 0):
                self.current_speed = 0  # Reset speed if direction changes

            # Accelerate the player's movement
            self.current_speed += self.acceleration * dt * self.direction.x
            # Clamp the speed to not exceed max speed in either direction
            self.current_speed = max(-self.max_speed, min(self.current_speed, self.max_speed))

        else:
            # Gradually decrease speed to zero if no input is detected
            if self.current_speed > 0:
                self.current_speed -= self.acceleration * dt
                if self.current_speed < 0:
                    self.current_speed = 0
            elif self.current_speed < 0:
                self.current_speed += self.acceleration * dt
                if self.current_speed > 0:
                    self.current_speed = 0
        if self.block:
            self.current_speed = 0

        # Apply horizontal movement
        self.hitbox_rect.x += self.current_speed * dt
        self.collision('horizontal')

        # Vertical movement logic (unchanged)
        if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not \
        self.timers['jump delay'].active:
            self.direction.y = 0
            self.hitbox_rect.y += self.gravity / 10 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt

        if self.jump:
            if self.on_surface['floor'] and not self.timers['jump delay'].active:

                self.direction.y = -self.jump_height
                self.timers['jump delay'].activate()
                self.hitbox_rect.bottom -= 1
                self.double_jump = True
                self.space = False
                print('original jump')
                self.timers['db-jump-delay'].activate()

            elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['jump delay'].active:
                self.timers['wall jump'].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface['left'] else -1
                self.current_speed = self.max_speed * (
                    1 if self.on_surface['left'] else -1)  # Set to max speed to ensure wall jump is effective
                self.jump = False

        #double jump and dash functionality -------------------------------------------

        if not self.on_surface['floor'] and self.double_jump == True and self.space == True and not self.timers['db-jump-delay'].active:
            self.direction.y = -400
            self.double_jump = False
        if not self.on_surface['floor'] and self.dash == True and not self.timers['dash-delay'].active:
            if self.facing_right == True:
                self.current_speed = 800
                self.timers['dash-delay'].activate()
            else:
                self.current_speed = -800
                self.timers['dash-delay'].activate()



        self.collision('vertical')
        self.jump = False
        self.rect.center = self.hitbox_rect.center


    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        # right_rect
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height/4), (2, self.hitbox_rect.height/2))

        # left_rect
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height/4), (2, self.hitbox_rect.height/2))

        display_surface = pygame.display.get_surface()
        #pygame.draw.rect(display_surface, (255, 0, 0), floor_rect, 1)
        #pygame.draw.rect(display_surface, (255, 0, 0), left_rect, 1)
        #pygame.draw.rect(display_surface, (255, 0, 0), right_rect, 1)

        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        #collisions
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False

    def draw_particles(self):
        if self.state == 'jump':
            self.air = True

        if self.on_surface['floor'] == True and self.air == True:
            ParticleEffectSprite((self.rect.centerx, self.rect.centery -15), self.particles['effects']['grass'], self.all_sprites)
            print('PARTICEL')
            self.air = False

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
                    #left
                    if self.hitbox_rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.hitbox_rect.left = sprite.rect.right
                    #right
                    if self.hitbox_rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.hitbox_rect.right = sprite.rect.left
                else: #vertical
                    #top
                    if self.hitbox_rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.hitbox_rect.top = sprite.rect.bottom
                    #bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.hitbox_rect.bottom = sprite.rect.top
                        if not self.jump:
                            self.direction.y = 0
                    if self.on_surface['floor'] and self.jump == False:
                        self.direction.y = 0

    def animate(self, dt):
        if self.state == 'slash':
            self.frame_index += ANIMATION_SPEED * 4 * dt
        if self.state == 'air attack':
            self.frame_index += ANIMATION_SPEED * 4 * dt
        else:
            self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'slash' and self.frame_index >= len(self.frames[self.state]):
            self.state = 'idle'
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def get_state(self):
        if self.on_surface['floor']:
            if self.attacking:
                self.state = 'slash'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if any((self.on_surface['left'], self.on_surface['right'])):
                self.state = 'wall'

            else:
                if self.attacking:
                    self.state = 'air attack' #add air attack here
                else: self.state = 'jump' if self.direction.y < 0 else 'air'
        if self.dash:
            self.state = 'dash'
        if self.block:
            self.state = 'block'

    def get_damage(self):
        if not self.timers['hit'].active and not self.block:
            self.data.health -= 1
            print('player damage')
            self.timers['hit'].activate()

    def flicker(self):
        if self.timers['hit'].active and sin(pygame.time.get_ticks() / 30) >= 0:
            red_mask = pygame.mask.from_surface(self.image)
            red_surf = red_mask.to_surface()
            red_surf.set_colorkey('black')

            red_surf.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            self.image = red_surf


    def update(self, dt):
        self.old_rect = self.hitbox_rect.copy()
        self.gravity = get_player_gravity()
        self.update_jump_heigth()
       # print(self.jump_height)
        #print(self.particles)
        self.draw_particles()
        print(self.air)

        if self.state == 'wall':
            self.level_sounds['wall'].set_volume(0.5)
            self.level_sounds['wall'].play()
        else:
            self.level_sounds['wall'].stop()



        #self.all_sprites.update(dt)




        self.input()
        self.check_contact()
        self.move(dt)

        self.update_timers()
        self.get_state()
        self.animate(dt)
        self.flicker()

       # print(self.on_surface)
        #print(self.timers['wall jump'].active)
        #print(self.direction.y)

        #pygame.display.get_surface()
       # pygame.draw.rect(self.display_surface, (255, 0, 0), floor_rect, 1)

import pygame
import sys
from pygame.math import Vector2 as vector

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 64
ANIMATION_SPEED = 6

PLAYER_SPEED = 200

# gravity reset
PLAYER_GRAVITY = 50
def set_player_gravity(value):
    global PLAYER_GRAVITY
    PLAYER_GRAVITY = value

def get_player_gravity():
    return PLAYER_GRAVITY





#layers
Z_LAYERS = {
    'Behind':-1,
    'BG': 0,
    'layer1': 1,
    'layer2': 2,
    'layer3': 3


}

from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = Z_LAYERS['layer1']):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect=self.rect.copy()
        self.z = z

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, z = Z_LAYERS['layer1'], animation_speed = ANIMATION_SPEED):
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed
        print(f"Sprite created at {pos} with size {self.image.get_size()}")
    def animate(self, dt):
        #print('ANIMAAAAAAATEEEE')
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
    def update(self, dt):
        self.animate(dt)

class Item(AnimatedSprite):
    def __init__(self, item_type, pos,  frames, groups, data):
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.item_type = item_type
        self.data = data
    def activate(self):
        if self.item_type == 'gold':
            self.data.coins += 5
        if self.item_type == 'silver':
            self.data.coins += 1
        if self.item_type == 'diamond':
            self.data.coins += 10
        if self.item_type == 'skull':
            self.data.coins += 100
        if self.item_type == 'potion':
            self.data.health += 2

class ParticleEffectSprite(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.z = Z_LAYERS['layer3']

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

from os.path import join
import pygame
from os import walk
import re
import os

def import_image(*path, alpha = True, format = 'png'):
    full_path = join(*path) + f'.{format}'
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(fullpath).convert()

def import_folder(*path):
    frames = []
    for folder_path, subfolders, image_names in walk(join(*path)):
        for image_name in sorted(image_names, key = lambda name: int(re.search(r'\d+', name).group())):
            full_path = join(folder_path, image_name)
            frames.append(pygame.image.load(full_path).convert_alpha())


    return frames

def import_folder_dict(*path):
    frame_dict = {}
    for folder_path, _, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surface = pygame.image.load(full_path).convert_alpha()
            frame_dict[image_name.split('.')[0]] = surface
        return frame_dict

def import_sub_folders(*path):
    frame_dict = {}
    for _, sub_folders, __ in walk(join(*path)):
        if sub_folders:
            for sub_folder in sub_folders:
                frame_dict[sub_folder] = import_folder(*path, sub_folder)
    return frame_dict

from pygame.time import get_ticks

class Timer:
    def __init__(self, duration, func = None, repeat = False):
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False
        self.repeat = repeat

    def activate(self):
        self.active = True
        self.start_time = get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0
        if self.repeat:
            self.activate()

    def update(self):
        current_time = get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()

from settings import *
from sprites import AnimatedSprite
from random import randint
from timer import Timer

class UI:
    def __init__(self, font, frames):
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        #health / hearts
        self.heart_frames = frames['heart']


        #coins
        self.coin_amount = 0
        self.coin_timer = Timer(1000)
        self.coin_surf = frames['coin']

    def create_hearts(self, amount):
        for sprite in self.sprites:
            sprite.kill()
        for heart in range(amount):
            x = 10 + heart * 20
            y = 10
            Heart((x,y), self.heart_frames, self.sprites)

    def display_text(self):
        text_surf = self.font.render(str(self.coin_amount), False, 'white')
        text_rect = text_surf.get_frect(topleft = (35,34))
        self.display_surface.blit(text_surf, text_rect)

        coin_rect = self.coin_surf.get_frect(center = text_rect.bottomleft).move(-15,-15)
        self.display_surface.blit(self.coin_surf, coin_rect)

    def show_coins(self, amount):
        self.coin_amount = amount

    def update(self, dt):
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_text()

class Heart(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.active = False

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt):
        if self.active:
            self.animate(dt)
        else:
            if randint(0,200) == 1:
                self.active = True

import pygame.display
from settings import *
import random
from random import choice
from timer import Timer
import math
from sprites import *
from groups import AllSprites
from os.path import join



class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(*groups)
        self.frames = [frame.copy() for frame in frames['tooth']]
        self.original_images = [frame.copy() for frame in self.frames]  # Copy of original frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = Z_LAYERS['layer1']

        self.direction = choice((-1, 1))
        self.collision_rects = collision_sprites
        self.speed = 100
        self.hit_timer = Timer(250)
        self.death_timer = Timer(1000)
        self.is_flickering = False
        self.direction_change_timer = Timer(500)  # Timer to control direction change frequency, 500ms cooldown
        self.direction_change_timer.activate()  # Start with the ability to change direction

        # Sensor rectangles for collision detection
        self.side_sensor_size = (5, self.rect.height)  # Width, Height of the side sensors
        self.edge_sensor_size = (5, 5)  # Width, Height of the edge sensors
        self.update_sensors()

    def update_sensors(self):
        self.right_sensor = pygame.Rect(self.rect.right, self.rect.y, *self.side_sensor_size)
        self.left_sensor = pygame.Rect(self.rect.left - self.side_sensor_size[0], self.rect.y, *self.side_sensor_size)
        self.edge_left_sensor = pygame.Rect(self.rect.left, self.rect.bottom, *self.edge_sensor_size)
        self.edge_right_sensor = pygame.Rect(self.rect.right - self.edge_sensor_size[0], self.rect.bottom, *self.edge_sensor_size)


    def reverse(self):
        if not self.hit_timer.active:
            self.hit_timer.activate()
            self.death_timer.activate()
            self.is_flickering = True
            self.flicker_time = pygame.time.get_ticks()

    def update(self, dt):
        self.hit_timer.update()
        self.death_timer.update()
        self.direction_change_timer.update()
        #print(f"dt: {dt}, speed: {self.speed}, direction: {self.direction}, new_x: {new_x}")

        # Animation and image flipping
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.is_flickering:
            current_time = pygame.time.get_ticks()
            flicker_duration = 600  # Flicker duration in milliseconds

            if current_time - self.flicker_time <= flicker_duration:
                # Calculate sine wave value for current time
                # The frequency and amplitude of the sine wave can be adjusted as needed
                sine_value = math.sin((current_time - self.flicker_time) * math.pi * 2 / flicker_duration)

                # Generate a flickering effect using the absolute value of the sine wave
                intensity = abs(sine_value) * 255  # Scale factor for color intensity
                flicker_image = self.original_images[int(self.frame_index % len(self.frames))].copy()
                flicker_image.fill((int(intensity), 0, 0), None, pygame.BLEND_RGB_ADD)
                self.image = flicker_image
            else:
                self.kill()
                self.is_flickering = False
        else:
            self.image = self.original_images[int(self.frame_index % len(self.frames))].copy()

        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)



        self.update_sensors()
        self.move(dt)
        self.apply_gravity()

    def move(self, dt):
        if self.direction > 0:
            self.speed = 200
        else:
            self.speed = 100
        # Calculate potential new position
        new_x = self.rect.x + self.direction * self.speed * dt
        new_rect = pygame.Rect(new_x, self.rect.y, self.rect.width, self.rect.height)

        # Debug prints for current state
        #print(f"dt: {dt}, speed: {self.speed}, direction: {self.direction}, new_x: {new_x}")

        # Detect collisions using sensors
        if ((self.detect_collision(self.right_sensor) and self.direction > 0) or
            (self.detect_collision(
                self.left_sensor) and self.direction < 0)) and not self.direction_change_timer.active:
            #print(f"Wall collision detected. Current direction: {self.direction}")
            self.direction *= -1
            self.direction_change_timer.activate()

        if ((not self.detect_collision(self.edge_left_sensor) or not self.detect_collision(self.edge_right_sensor)) and
                not self.direction_change_timer.active):
            #print(f"Edge detected. Current direction: {self.direction}")
            self.direction *= -1
            self.direction_change_timer.activate()

        # Apply movement if no horizontal collision detected
        if not any(new_rect.colliderect(sprite.rect) for sprite in self.collision_rects):
            self.rect.x = new_x

    def detect_collision(self, sensor):
        return any(sensor.colliderect(sprite.rect) for sprite in self.collision_rects)

    def apply_gravity(self):
        gravity = 1
        future_rect = pygame.Rect(self.rect.x, self.rect.y + gravity, self.rect.width, self.rect.height)
        if not any(future_rect.colliderect(sprite.rect) for sprite in self.collision_rects):
            self.rect.y += gravity  # Apply gravity if no vertical collision
        else:
            while any(pygame.Rect(self.rect.x, self.rect.y + 1, self.rect.width, self.rect.height).colliderect(
                    sprite.rect) for sprite in self.collision_rects):
                self.rect.y -= 1  # Adjust up if penetrating a platform

class Shell(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, reverse, player, create_pearl):
        super().__init__(groups)

        if reverse:
            #flip all frames
            self.frames = {}
            for key, surfs in frames.items():
                self.frames[key] = [pygame.transform.flip(surf, True, False) for surf in surfs]
            self.bullet_direction = -1
        else:
            self.frames = frames
            self.bullet_direction = 1

        self.frame_index =  0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft=(pos[0], pos[1] + 15))
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS['layer1']
        self.player = player
        self.shoot_timer = Timer(1000)
        self.has_fired = False
        self.create_pearl = create_pearl

    def state_management(self):
        player_pos, shell_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
        player_near = shell_pos.distance_to(player_pos) < 500
        player_front = shell_pos.x < player_pos.x if self.bullet_direction > 0 else shell_pos.x > player_pos.x
        player_level = abs(shell_pos.y - player_pos.y) < 30

        if player_near and player_level and player_front and not self.shoot_timer.active:
            self.state = 'fire'
            self.frame_index = 0
            self.shoot_timer.activate()

    def update(self, dt):
        self.shoot_timer.update()
        self.state_management()

        #animation/attack
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames[self.state]):
            self.image = self.frames[self.state][int(self.frame_index)]

            #fire
            if self.state == 'fire' and int(self.frame_index) == 3 and not self.has_fired:
                self.create_pearl(self.rect.center, self.bullet_direction)
                self.has_fired = True

        else:
            self.frame_index = 0
            if self.state == 'fire':
                self.state = 'idle'
                self.has_fired = False

class Pearl(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surf, direction, speed):
        self.pearl = True
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos + vector(50  * direction,0))
        self.direction = direction
        self.speed = speed*1.5
        self.z = Z_LAYERS['layer1']
        self.timers = {'lifetime': Timer(2000), 'reverse': Timer(250)}
        self.timers['lifetime'].activate()


    def reverse(self):
        if not self.timers['reverse'].active:
            self.direction *= -1
            self.timers['reverse'].activate()

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()
        self.rect.x += self.direction * self.speed * dt
        if not self.timers['lifetime'].active:
            self.kill()


class Bat(pygame.sprite.Sprite):
    def __init__(self, pos, frames, sounds, groups, player):
        super().__init__(*groups)
        self.frames = frames
        self.level_sounds = sounds
        self.fly = False
        self.fly_off = False
        self.state = 'hanging'
        self.frame_index = 0
        self.image = self.frames[self.state][self.frame_index]
        #self.original_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.z = Z_LAYERS['layer1']
        self.player = player
        self.drop_speed = 100
        self.fly_speed = 200
        self.drop_distance = 50
        self.drop_timer = Timer(500)  # Time for drop state
        self.state_switch_distance = 200  # Distance to trigger from hanging to drop

    def reverse(self):
        self.kill()

    def update(self, dt):
        player_pos = vector(self.player.rect.center)
        bat_pos = vector(self.rect.center)
        self.drop_timer.update()

        distance = bat_pos.distance_to(player_pos)

        if self.state == 'hanging' and distance < self.state_switch_distance:
            self.state = 'drop'
            self.drop_timer.activate()

        if self.state == 'drop':
            if not self.drop_timer.active:
                self.state = 'fly'
            else:
                self.rect.y += self.drop_speed * dt

        if self.state == 'fly':
            self.fly = True
            if self.fly == True and self.fly_off == False:
                self.level_sounds['bat'].set_volume(0.5)
                self.level_sounds['bat'].play()
                self.fly_off = True
            direction = (player_pos - bat_pos).normalize()
            self.rect.x += direction.x * self.fly_speed * dt
            self.rect.y += direction.y * self.fly_speed * dt

        # Animation updates
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(self.frames[self.state]):
            self.frame_index = 0
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]

        # Rotate bat image towards the player in fly state
        if self.state == 'fly':
            angle = math.degrees(math.atan2(-direction.y, direction.x))
            self.image = pygame.transform.rotate(self.image, angle - 90)


class Shroom(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player):
        super().__init__(*groups)
        self.frames = frames
        self.state = 'idle'
        self.frame_index = 0
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = Z_LAYERS['layer1']
        self.player = player


        self.burst_timer = Timer(random.randint(5000, 10000))
        self.interval_timer = Timer(random.randint(21000, 30000))
        self.interval_timer.activate()
        self.burst_timer.activate()
        self.fog_image = pygame.image.load(join('Graphics', 'enemies', 'fog.png'))  # Load the image file for the fog

    def update(self, dt):
        self.burst_timer.update()
        self.interval_timer.update()
        if not self.interval_timer.active:
            self.state = 'burst'

        if self.state == 'idle' and not self.burst_timer.active:
            self.state = 'burst'
            self.frame_index = 0
            self.spawn_fog()
            self.burst_timer = Timer(random.randint(5000, 6000))  # Reset timer
            self.burst_timer.activate()

        if self.state == 'burst':
            self.frame_index += ANIMATION_SPEED/2 * dt
            if self.frame_index >= len(self.frames):
                self.burst_timer.activate()
                self.frame_index = 0  # Loop or stop animation


    def spawn_fog(self):
        # Create a Fog instance
        fog_groups = (self.groups())  # Use the first group from Shroom or specify as needed
        Fog(self.rect.center, self.fog_image, fog_groups, 2000, 10000, self.player)
        self.interval_timer.activate()

class Fog(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups, damage_interval, duration, player):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.player = player
        self.z = Z_LAYERS['layer1']

        self.lifetime_timer = Timer(duration)  # Timer for how long the fog lasts

        self.lifetime_timer.activate()

    def update(self, dt):

        self.lifetime_timer.update()



        if not self.lifetime_timer.active:
            self.kill()  # Remove the fog after the duration expires









