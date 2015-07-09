from math import cos, sin, radians
from entity import Entity


class Weapon(Entity):
    
    def __init__(self, functions):
        Entity.__init__(self, functions)
        self.damage = 2
    
    def get_info(self):
        "Return information regarding the player."
        data = {
            'id': self.object_id,
            'damage': self.damage,
            'turn_rate': self.turn_rate,
            'accel': self.accel,
            'max_speed': self.max_speed,
            'collide_size': self.collide_size,
        }
        return data
    
    def new_collide_size(self, size):
        "Set new collision box size."
        self.collide_size = size
        
    def update(self, delta_time):
        return Entity.update(self, delta_time)
