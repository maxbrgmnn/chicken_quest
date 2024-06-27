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


