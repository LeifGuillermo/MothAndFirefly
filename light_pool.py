class LightPool:
    def __init__(self):
        self.light_level = 100
        self.decrease_rate = 0.2778  # Default rate of decrease
        self.critical_threshold = 20  # Below this value, warnings should be triggered

    def decrease(self, amount):
        self.light_level -= amount
        # Ensure light doesn't drop below 0
        self.light_level = max(0, self.light_level)

        # If light level falls below the critical threshold
        if self.light_level <= self.critical_threshold:
            print("low light! play sound")

    # Play a warning sound or show visual cue
    # TODO: play_sound('warning_alarm.wav')

    def increase(self, amount, distance):
        # You can adjust the formula based on the game balance
        bonus_multiplier = max(1 - 0.01*distance, 0.1)
        effective_increase = amount * bonus_multiplier
        self.light_level += effective_increase

    def is_empty(self):
        return self.light_level <= 0

    def is_critical(self):
        return self.light_level <= self.critical_threshold

    def update(self, player_distance):
        # Decrease light with the default rate
        self.decrease(self.decrease_rate)
        # Check for regeneration based on the players' proximity
        if player_distance < 10:  # Assuming a suitable distance metric
            self.increase(0.5, player_distance)  # Small regeneration
