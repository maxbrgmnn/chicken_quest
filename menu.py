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
