import pygame
import random


from player import Moth

character_pixel_size = 5
_ = (0, 0, 0, 0)  # Transparent
M = (60, 255, 100)  # Moth color
F_base = (255, 255, 100)  # Base Firefly color
moth_base_pixels = [
    [_, _, M, M, M, M, _, _],
    [_, M, M, M, M, M, M, _],
    [M, M, M, M, M, M, M, M],
    [_, M, M, M, M, M, M, _],
    [_, _, M, M, M, M, _, _],
]
firefly_base_pixels = [
    [_, _, F_base, F_base, _, _],
    [_, F_base, F_base, F_base, F_base, _],
    [F_base, F_base, F_base, F_base, F_base, F_base],
    [_, F_base, F_base, F_base, F_base, _],
    [_, _, F_base, F_base, _, _],
]


class GraphicsManager:
    def __init__(self):
        self.particles = None
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Moth and Firefly")

        # Moth animation state
        self.moth_wing_state = 1
        self.moth_wing_direction = 1

        # Firefly animation state
        self.firefly_intensity = 1
        self.firefly_intensity_direction = 1

        # Stars in the background
        self.stars = [
            (
                random.randint(0, self.screen_width),
                random.randint(0, self.screen_height),
            )
            for _ in range(100)
        ]

    def draw_background(self, light_level):
        darkness_factor = (100 - light_level) / 100
        blue_value = int(255 * (1 - darkness_factor))
        blue_value = max(0, min(255, blue_value))
        bg_color = (0, 0, blue_value)
        self.screen.fill(bg_color)

        # Draw stars
        for star in self.stars:
            star_intensity_raw = random.randint(150, 255) * (1 - darkness_factor)
            star_intensity = max(0, min(255, int(star_intensity_raw)))
            pygame.draw.circle(
                self.screen, (star_intensity, star_intensity, star_intensity), star, 1
            )

    def draw_character(self, character, color, size_modifier=1.0):
        if isinstance(character, Moth):
            self.draw_moth(character, color, size_modifier)
        else:
            self.draw_pixel_character(character, self.get_firefly_pixels())
            # Adjusting the intensity for animation
            if self.firefly_intensity >= 1 or self.firefly_intensity <= 0.5:
                self.firefly_intensity_direction *= -1
            self.firefly_intensity += 0.05 * self.firefly_intensity_direction

    def draw_moth(self, character, color, size_modifier):
        pixel_data = moth_base_pixels
        if character.dx != 0 and character.dy == 0:
            # Horizontal movement
            pixel_data = self.get_moth_pixels_horizontal()  # Wings adjust horizontally
        elif character.dx == 0 and character.dy != 0:
            # Vertical movement
            pixel_data = self.get_moth_pixels_vertical()  # Wings adjust vertically
        elif character.dx != 0 and character.dy != 0:
            # Diagonal movement
            # Wings adjust based on diagonal movement
            pixel_data = self.get_moth_pixels_diagonal(character)

        self.draw_pixel_character(character, pixel_data)

        # Adjusting the wing state for animation
        if self.moth_wing_state >= 1.2 or self.moth_wing_state <= 0.8:
            self.moth_wing_direction *= -1
        self.moth_wing_state += 0.01 * self.moth_wing_direction

    def get_moth_pixels_vertical(self):
        # Wings adjust vertically
        expanded_top_rows = int(1.5 * self.moth_wing_state)
        expanded_bottom_rows = int(1.5 * self.moth_wing_state)
        return (
            [moth_base_pixels[0]] * expanded_top_rows
            + moth_base_pixels[1:4]
            + [moth_base_pixels[4]] * expanded_bottom_rows
        )

    def get_moth_pixels_horizontal(self):
        # Wings adjust horizontally
        expanded_rows = int(3 * self.moth_wing_state)
        return (
            moth_base_pixels[:2]
            + [moth_base_pixels[2]] * expanded_rows
            + moth_base_pixels[3:]
        )

    def get_moth_pixels_diagonal(self, character):
        # Depending on the direction, we'll adjust the wing contraction and expansion.

        # Up and Left OR Down and Right
        if (character.dx < 0 and character.dy < 0) or (
            character.dx > 0 and character.dy > 0
        ):
            expanded_top_right = [M for _ in range(int(2 * self.moth_wing_state))]
            expanded_bottom_left = [M for _ in range(int(2 * self.moth_wing_state))]

            return (
                moth_base_pixels[:2]
                + [moth_base_pixels[1] + expanded_top_right]
                + [moth_base_pixels[2] + expanded_top_right]
                + [expanded_bottom_left + row for row in moth_base_pixels[3:]]
            )

        # Up and Right OR Down and Left
        else:
            expanded_top_left = [M for _ in range(int(2 * self.moth_wing_state))]
            expanded_bottom_right = [M for _ in range(int(2 * self.moth_wing_state))]

            return (
                moth_base_pixels[:2]
                + [expanded_top_left + row for row in moth_base_pixels[1:3]]
                + [moth_base_pixels[3] + expanded_bottom_right]
                + [moth_base_pixels[4] + expanded_bottom_right]
            )

    def draw_pixel_character(self, character, pixel_data):
        # Calculate starting point to ensure the character is centered
        start_x = self.get_character_start_x(character, pixel_data)
        start_y = self.get_character_start_y(character, pixel_data)

        # Iterate over each pixel in the pixel_data
        for row_index, row in enumerate(pixel_data):
            for col_index, pixel in enumerate(row):
                if pixel != (0, 0, 0, 0):  # If not transparent
                    pygame.draw.rect(
                        self.screen,
                        pixel,
                        (
                            start_x + col_index * character_pixel_size,
                            start_y + row_index * character_pixel_size,
                            character_pixel_size,
                            character_pixel_size,
                        ),
                    )

    def get_character_start_x(self, character, pixel_data):
        return character.x - (len(pixel_data[0]) * character_pixel_size) // 2

    def get_character_start_y(self, character, pixel_data):
        return character.y - (len(pixel_data) * character_pixel_size) // 2

    def draw(self, moth, firefly, light_pool, obstacles_list):
        self.draw_background(light_pool.light_level)
        self.draw_character(moth, color=(150, 100, 255), size_modifier=2)
        self.draw_character(firefly, color=(255, 255, 100))
        self.draw_light(moth, light_pool)
        self.draw_light(firefly, light_pool)
        self.draw_firefly_particles(firefly)

        for obstacle in obstacles_list:
            self.draw_obstacle(obstacle)

        self.draw_critical_warning(light_pool.light_level)
        pygame.display.flip()  # Refresh the screen

    def draw_obstacle(self, obstacles):
        """
        Draw all obstacles onto the screen.
        :param screen: Pygame screen object to render on.
        :param obstacles: List or pygame.sprite.Group of obstacles to render.
        """
        obstacles.draw(self.screen)

    def compute_intensity(self, distance, max_distance):
        """Compute the intensity of light based on the distance from the light source.

        Args:
        - distance (float): The distance from the light source.
        - max_distance (float): The maximum distance that light will reach.

        Returns:
        - float: The intensity of the light, ranging from 0 (no light) to 1 (full light).
        """
        if distance > max_distance:
            return 0
        # For simplicity, use a linear fall-off.
        # You can use other functions (e.g., quadratic) for different effects.
        return 1 - (distance / max_distance)

    def draw_light(self, character, light_pool):
        light_radius = (light_pool.light_level / 100) * 150  # Max light radius is 150
        light_radius = max(0, min(150, light_radius))

        if isinstance(character, Moth):
            char_pixels = moth_base_pixels
            shift = self.moth_wing_state
        else:
            char_pixels = firefly_base_pixels
            shift = 1  # shift of 1 is no shift

        center_x = (
            self.get_character_start_x(character, char_pixels)
            + (len(char_pixels[0]) * character_pixel_size / 2) * shift
        )
        center_y = self.get_character_start_y(character, char_pixels) + (
            (len(char_pixels) * character_pixel_size) / 2
        )

        # Save the areas of the screen where the characters are
        character_rect = pygame.Rect(
            self.get_character_start_x(character, char_pixels),
            self.get_character_start_y(character, char_pixels),
            len(char_pixels[0]) * character_pixel_size,
            len(char_pixels) * character_pixel_size,
        )
        character_surface = self.screen.subsurface(character_rect).copy()

        # Create a surface for the light effect
        light_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(
            light_surface,
            (255, 255, 100, 128),
            (int(center_x), int(center_y)),
            int(light_radius),
        )

        # Dim the entire screen with reduced opacity
        dim_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 127))  # 50% opacity

        # Combine the light surface with the dimming overlay
        dim_surface.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        # Apply the combined effect to the main screen
        self.screen.blit(dim_surface, (0, 0))

        # Blit the saved character surfaces to ensure they remain fully illuminated
        self.screen.blit(character_surface, character_rect.topleft)

    def draw_firefly_particles(self, firefly):
        # We'll create a list to store particles. Each particle will have a position and a lifetime.
        if not hasattr(self, "particles"):
            self.particles = []

            # Remove particles that are no longer visible
            self.particles = [p for p in self.particles if p["lifetime"] > 0]

            for particle in self.particles:
                particle_intensity = max(0, min(255, particle["lifetime"]))
                particle_color = (255, 255, 100, particle_intensity)
                pygame.draw.circle(self.screen, particle_color, particle["pos"], 3)
                particle["lifetime"] -= 5

    def draw_critical_warning(self, light_level):
        if light_level < 20:  # Warning appears when light level is below 20
            warning_font = pygame.font.SysFont(None, 55)
            warning_text = warning_font.render("Light Critical!", True, (255, 0, 0))
            text_rect = warning_text.get_rect(center=(self.screen_width / 2, 50))
            self.screen.blit(warning_text, text_rect)

    def close(self):
        pygame.quit()

    def get_moth_pixels(self):
        expanded_rows = int(3 * self.moth_wing_state)
        return (
            moth_base_pixels[:2]
            + [moth_base_pixels[2]] * expanded_rows
            + moth_base_pixels[3:]
        )

    def get_firefly_pixels(self):
        brightness_adjustment = self.firefly_intensity
        F = (
            int(F_base[0] * brightness_adjustment),
            int(F_base[1] * brightness_adjustment),
            100,
        )
        return [
            [F if pixel == F_base else pixel for pixel in row]
            for row in firefly_base_pixels
        ]
