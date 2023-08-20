class FireflyCluster:
    def __init__(self):
        self.size = 10  # Number of fireflies in the cluster; adjust as necessary.
        self.light_boost = 20  # The amount of light energy gained when interacting with the cluster.
        self.is_collected = False  # To ensure the cluster isn't collected multiple times.

    def interact(self, firefly):
        """
        This method allows the main firefly to interact with the cluster,
        gaining light energy or other benefits.
        """
        if not self.is_collected:
            firefly.light_energy += self.light_boost  # Assuming the firefly class has a light_energy attribute.
            self.is_collected = True
            # If you want to include a sound effect when collecting, place it here.
            # pygame.mixer.Sound('collect_sound.wav').play()  # Assuming you have a sound file named 'collect_sound.wav'.
            self.size = 0  # Empties the cluster once it's interacted with.
