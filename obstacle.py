import random
import pygame


# ======== UTILITIES AND GENERAL FUNCTIONS ========


def create_pixel_art_image(pixel_data, pixel_size=10):
    width = len(pixel_data[0])
    height = len(pixel_data)
    image = pygame.Surface((width * pixel_size, height * pixel_size))

    for y, row in enumerate(pixel_data):
        for x, color in enumerate(row):
            if (
                color
            ):  # Only fill in the rectangle if there's a color (allows for transparent pixels)
                rect = pygame.Rect(
                    x * pixel_size, y * pixel_size, pixel_size, pixel_size
                )
                image.fill(color, rect)

    return image


# ======== OBSTACLE BASE CLASSES ========


class Obstacle(pygame.sprite.Sprite):
    def __init__(
        self,
        pixel_data,
        x=0,
        y=0,
        obstacle_type="static",
        special_ability=None,
        pixel_size=10,
        width=10,
        height=10,
    ):
        super().__init__()

        # Visual representation
        self.image = create_pixel_art_image(pixel_data, pixel_size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Game mechanics
        self.obstacle_type = obstacle_type
        self.special_ability = special_ability
        self.visible = True if obstacle_type != "hidden" else False
        self.interaction_cooldown = 0
        self.direction = 1  # Used for movement of dynamic obstacles
        self.sound_emission_cooldown = 100

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.rect.x, self.rect.y))

    def reveal(self, player):
        if self.obstacle_type == "hidden" and self.distance_to(player) < 5:
            self.visible = True

    def distance_to(self, player):
        return ((player.x - self.rect.x) ** 2 + (player.y - self.rect.y) ** 2) ** 0.5

    def interact(self, player):
        if not self.visible or self.interaction_cooldown > 0:
            return

        player.light -= 10
        player.light = max(0, player.light)

        if self.special_ability == "absorb":
            player.light -= 5
            player.light = max(0, player.light)
        elif self.special_ability == "stun":
            player.stunned_time = 5
            # Play stun sound
            # TODO: Add sound logic

        # Set interaction cooldown to prevent rapid interactions
        self.interaction_cooldown = 10

    def update(
        self, players=None
    ):  # Accepts a list of players to determine the closest one.
        # Cooldown logic
        if players is None:
            players = []
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= 1

        # Added cooldown for sound emission
        if (
            hasattr(self, "sound_emission_cooldown")
            and self.sound_emission_cooldown > 0
        ):
            self.sound_emission_cooldown -= 1

        if self.obstacle_type in ["bat", "owl"]:
            # Handle horizontal movement
            self.rect.x += 2 * self.direction

            # Check screen boundary for x position and adjust accordingly
            if self.rect.x >= 700:
                self.rect.x = 695  # Move it slightly inward
                self.direction *= -1
            elif self.rect.x <= 0:
                self.rect.x = 5  # Move it slightly inward
                self.direction *= -1

            # Owl unique behavior: Occasionally it will fly upwards
            if self.obstacle_type == "owl":
                if random.random() < 0.01:  # 1% chance every frame
                    self.rect.y -= 15  # Quick upwards movement
                if self.rect.y <= 0:  # top boundary for y
                    self.rect.y = 0

        # Sound emission ability
        if self.special_ability == "emit_sound" and (
            not hasattr(self, "sound_emission_cooldown")
            or self.sound_emission_cooldown == 0
        ):
            # Find closest player
            closest_player = None
            min_distance = float("inf")
            for player in players:
                dist = (
                    (player.x - self.rect.x) ** 2 + (player.y - self.rect.y) ** 2
                ) ** 0.5
                if dist < min_distance:
                    min_distance = dist
                    closest_player = player

            # Move towards the closest player
            if closest_player:
                dx = closest_player.x - self.rect.x
                dy = closest_player.y - self.rect.y
                mag = max(abs(dx), abs(dy))
                if mag > 0:
                    self.rect.x += dx / mag  # Normalize movement
                    self.rect.y += dy / mag
            # Set a cooldown so that this ability isn't used too frequently


# ======== SPECIFIC OBSTACLE CLASSES ========


class Tree(Obstacle):
    TREE_PIXELS = [
        [None, None, None, (0, 128, 0), None, None, None],
        [None, None, (0, 128, 0), (0, 128, 0), (0, 128, 0), None, None],
        [None, (0, 128, 0), (0, 128, 0), (0, 128, 0), (0, 128, 0), (0, 128, 0), None],
        [None, (0, 128, 0), (0, 128, 0), (0, 128, 0), (0, 128, 0), (0, 128, 0), None],
        [None, (0, 128, 0), (0, 128, 0), (0, 128, 0), (0, 128, 0), (0, 128, 0), None],
        [None, None, (139, 69, 19), (139, 69, 19), (139, 69, 19), None, None],
        [None, None, (139, 69, 19), (139, 69, 19), (139, 69, 19), None, None],
    ]

    def __init__(self, x, y):
        super().__init__(self.TREE_PIXELS, x, y)
        self.special_ability = "stun"

    def draw(self, screen):
        super().draw(screen)


class Bat(Obstacle):
    BAT_PIXELS = [
        [None, (105, 105, 105), (105, 105, 105), (105, 105, 105), None],
        [(105, 105, 105), (255, 0, 0), (0, 0, 0), (255, 0, 0), (105, 105, 105)],
        [(105, 105, 105), (0, 0, 0), (0, 0, 0), (0, 0, 0), (105, 105, 105)],
        [
            (105, 105, 105),
            (255, 255, 255),
            (0, 0, 0),
            (255, 255, 255),
            (105, 105, 105),
        ],
        [None, (105, 105, 105), (105, 105, 105), (105, 105, 105), None],
    ]

    def __init__(self, x, y):
        super().__init__(self.BAT_PIXELS, x, y, obstacle_type="bat")
        self.speed = random.randint(1, 3)
        self.special_ability = "emit_sound"

    def draw(self, screen):
        super().draw(screen)


class Rock(Obstacle):
    ROCK_PIXELS = [
        [None, None, (169, 169, 169), (169, 169, 169), None, None],
        [
            None,
            (169, 169, 169),
            (128, 128, 128),
            (128, 128, 128),
            (169, 169, 169),
            None,
        ],
        [
            (169, 169, 169),
            (128, 128, 128),
            (112, 128, 144),
            (112, 128, 144),
            (128, 128, 128),
            (169, 169, 169),
        ],
        [
            (169, 169, 169),
            (128, 128, 128),
            (112, 128, 144),
            (112, 128, 144),
            (128, 128, 128),
            (169, 169, 169),
        ],
        [
            None,
            (169, 169, 169),
            (128, 128, 128),
            (128, 128, 128),
            (169, 169, 169),
            None,
        ],
        [None, None, (169, 169, 169), (169, 169, 169), None, None],
    ]

    def __init__(self, x, y):
        super().__init__(self.ROCK_PIXELS, x, y)
        self.special_ability = "stun"

    def draw(self, screen):
        super().draw(screen)


class Owl(Obstacle):
    OWL_PIXELS = [
        [None, (139, 69, 19), (139, 69, 19), (139, 69, 19), None],
        [
            (139, 69, 19),
            (210, 180, 140),
            (255, 255, 255),
            (210, 180, 140),
            (139, 69, 19),
        ],
        [(139, 69, 19), (255, 255, 255), (0, 0, 0), (255, 255, 255), (139, 69, 19)],
        [
            (139, 69, 19),
            (210, 180, 140),
            (255, 255, 255),
            (210, 180, 140),
            (139, 69, 19),
        ],
        [None, (139, 69, 19), (139, 69, 19), (139, 69, 19), None],
        [None, (139, 69, 19), None, (139, 69, 19), None],
    ]

    def __init__(self, x, y):
        super().__init__(self.OWL_PIXELS, x, y, obstacle_type="owl")
        self.speed = random.randint(1, 3)
        self.special_ability = "absorb"

    def draw(self, screen):
        super().draw(screen)
