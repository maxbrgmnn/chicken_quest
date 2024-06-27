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
        self.rect = self.image.get_rect(topleft=pos)
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
