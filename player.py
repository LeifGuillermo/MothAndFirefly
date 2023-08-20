class Player:
    def __init__(self, screen_width, screen_height):
        self.x = screen_width/2
        self.y = screen_height/2
        self.dx = 0   # Change in x-direction
        self.dy = 0   # Change in y-direction
        self.light = 100
        self.speed = 3
        self.stunned_time = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self, dx, dy):
        self.dx = dx
        self.dy = dy
        if self.stunned_time <= 0:
            self.x += dx
            self.y += dy
        else:
            self.x += dx * 0.5  # Reduced speed when stunned
            self.y += dy * 0.5

    def update(self):
        # Recover from being stunned over time
        if self.stunned_time > 0:
            self.stunned_time -= 1


class Moth(Player):
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.shield_active = False
        self.shield_cooldown = 0

    def use_shield(self):
        # Can only use shield if not in cooldown and if enough light is available
        if not self.shield_active and self.shield_cooldown <= 0 and self.light >= 10:
            self.shield_active = True
            self.light -= 10  # Consume light for shield
            self.shield_cooldown = 5  # Example: 5 updates/seconds cooldown

    def update(self):
        super().update()
        if self.shield_active:
            self.light -= 0.3  # increased light drain when shield is active
            self.light = max(0, self.light)  # Ensure light doesn't drop below 0%

        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1


class Firefly(Player):
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.intensity = 1  # Default full intensity

    def boost_light(self, amount):
        self.light += amount
        self.light = min(100, self.light)  # Ensure light doesn't exceed 100%

    def adjust_intensity(self, factor):
        # Adjust intensity between 0.5 (half) and 1 (full)
        self.intensity = max(0.5, min(factor, 1))

    def update(self):
        super().update()
        # Depending on intensity, adjust the light consumption
        self.light -= 0.1 * self.intensity
        self.light = max(0, self.light)  # Ensure light doesn't drop below 0%
