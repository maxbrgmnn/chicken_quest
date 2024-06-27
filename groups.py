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

