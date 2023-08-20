from player import Moth, Firefly
from light_pool import LightPool
from graphics_manager import GraphicsManager
import pygame  # Assuming you're using pygame
import math
import random
from obstacle import Tree, Bat, Rock, Owl


class Game:
    def __init__(self):
        pygame.init()

        self.screen_width = 800  # Assuming a screen width of 800 for this example
        self.screen_height = 600  # Assuming a screen height of 600 for this example

        self.moth = Moth(self.screen_width, self.screen_width)
        self.firefly = Firefly(self.screen_width, self.screen_width)
        self.light_pool = LightPool()
        self.graphics_manager = GraphicsManager()

        self.obstacles = []  # List to store all the obstacles
        self.cooldown_timer = 0
        self.max_cooldown = (
            100  # Adjust this to control the maximum time between spawns
        )

    def generate_obstacle(self):
        obstacle_types = [Tree, Bat, Rock, Owl]
        chosen_obstacle = random.choice(obstacle_types)
        x = self.screen_width - 50  # Start from the right end of the screen
        y = random.randint(20, self.screen_height - 100)  # Adjust as per your needs
        new_obstacle = chosen_obstacle(x, y)
        self.obstacles.append(new_obstacle)

    def run(self):
        clock = pygame.time.Clock()

        while not self.game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            # Update the cooldown timer
            if self.cooldown_timer > 0:
                self.cooldown_timer -= 1

            self.handle_input()
            self.update()
            self.draw()
            for obstacle_object in self.obstacles:
                obstacle_object.reveal(self.moth)
                obstacle_object.reveal(self.firefly)
                obstacle_object.interact(self.moth)
                obstacle_object.interact(self.firefly)
                obstacle_object.update([self.moth, self.firefly])

            # Check obstacle generation condition
            if self.cooldown_timer <= 0:
                generation_speed = 5
                if random.randint(0, 100) > (100 - generation_speed):
                    self.generate_obstacle()

                    # Reset the cooldown timer with a randomized delay
                    self.cooldown_timer = random.randint(
                        30, self.max_cooldown
                    )  # Random delay between 30 and max_cooldown

            clock.tick(60)  # 60 FPS

    def game_over(self):
        return self.light_pool.is_empty()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Moth controls
        if keys[pygame.K_LEFT]:
            self.moth.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.moth.move(1, 0)
        if keys[pygame.K_UP]:
            self.moth.move(0, -1)
        if keys[pygame.K_DOWN]:
            self.moth.move(0, 1)

        # Firefly controls
        if keys[pygame.K_a]:
            self.firefly.move(-1, 0)
        if keys[pygame.K_d]:
            self.firefly.move(1, 0)
        if keys[pygame.K_w]:
            self.firefly.move(0, -1)
        if keys[pygame.K_s]:
            self.firefly.move(0, 1)

        # Moth can activate a shield with the space bar
        if keys[pygame.K_SPACE]:
            self.moth.use_shield()

        # Firefly emits a quick burst of light with the E key based on distance to Moth
        if keys[pygame.K_e]:
            distance = self.calculate_distance(self.moth, self.firefly)
            self.light_pool.increase(
                5, distance
            )  # Using a base amount of 5, which will get modified inside
            # the increase method based on distance

    def calculate_distance(self, player1, player2):
        return math.sqrt((player1.x - player2.x) ** 2 + (player1.y - player2.y) ** 2)

    def calculate_light_bonus(self, distance):
        # Assuming the maximum bonus is 10 units of light when players are very close (distance=0),
        # and it linearly decreases to a minimum bonus of 1 unit of light at a distance of 100 units or more.
        return max(10 - 0.09 * distance, 1)

    def update(self):
        self.moth.update()
        self.firefly.update()
        distance = self.calculate_distance(self.moth, self.firefly)
        self.light_pool.update(distance)

        # Checking if firefly is near the moth to potentially transfer light
        if (
            abs(self.moth.x - self.firefly.x) < 10
            and abs(self.moth.y - self.firefly.y) < 10
        ):
            self.light_pool.increase(5, distance)

    def draw(self):
        self.graphics_manager.draw(
            self.moth, self.firefly, self.light_pool, self.obstacles
        )
        pygame.display.flip()
