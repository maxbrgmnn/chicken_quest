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

