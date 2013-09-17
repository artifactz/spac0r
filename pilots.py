import world
import math

class AI_Pilot:
    def __init__(self, spacecraft, world):
        self.spacecraft = spacecraft
        self.world = world

class AI_Pilot_Basic(AI_Pilot):
    def __init__(self, spacecraft, world):
        AI_Pilot.__init__(self, spacecraft, world)
        # look up weapon with highest dps
        self.strongest_weapon = None
        dps_max = 0
        for part in filter(lambda x: x.stats.attack > 0, spacecraft.parts):
            dps = part.stats.attack / float(part.stats.attack_cooldown_max)
            if dps > dps_max:
                self.strongest_weapon = part
                dps_max = dps
        if self.strongest_weapon:
            self.shooting_range = self.strongest_weapon.stats.attack_speed * self.strongest_weapon.stats.attack_ttl
            self.optimal_distance = self.shooting_range * .667
        else:
            self.shooting_range = 0
            self.optimal_distance = 350

    def pilot(self):
        # face player
        dx = self.world.player.position[0] - self.spacecraft.position[0]
        dy = self.spacecraft.position[1] - self.world.player.position[1]
        angle_to_player = math.atan2(dy, dx)
        self.spacecraft.rotate(angle_to_player)
        # catch up
        dist_to_player = math.sqrt(dx**2 + dy**2)
        if dist_to_player > self.optimal_distance:
            self.spacecraft.steer_straight()
        elif dist_to_player < self.optimal_distance * 0.85:
            self.spacecraft.steer_back()
        # correct drifting
        speed_diff = [self.world.player.speed[0] - self.spacecraft.speed[0], self.spacecraft.speed[1] - self.world.player.speed[1]]
        sd_angle = math.atan2(speed_diff[1], speed_diff[0]) - self.spacecraft.rotation
        if abs(math.cos(sd_angle)) < .5:
            if math.sin(sd_angle) > 0:
                self.spacecraft.steer_left()
            else:
                self.spacecraft.steer_right()
        # shoot
        if dist_to_player <= self.shooting_range:
            self.spacecraft.shoot(self.world)
