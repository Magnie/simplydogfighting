from math import cos, sin, radians
from entity import Entity
from weapon import Weapon


class Player(Entity):
    
    def __init__(self, functions):
        Entity.__init__(self, functions)
        self.health = 10
        self.ignore_list = []
        
        self.type = 'player'
        
        self.live_weapons = []
        self.weapon_cooldown = 0.5
        self.cooldown = self.weapon_cooldown
        
        self.name = 'Observer'
        self.controls = {
            'thrust': 0,
            'turning': 0,
            'attack': 0,
        }
    
    def get_info(self):
        "Return information regarding the player."
        data = {
            'id': self.object_id,
            'health': self.health,
            'turn_rate': self.turn_rate,
            'accel': self.accel,
            'max_speed': self.max_speed,
            'collide_size': self.collide_size,
        }
        return data
    
    def new_controls(self, controls):
        "Update the current controls being pressed."
        if 'thrust' in controls:
            self.controls['thrust'] = controls['thrust']
        
        if 'turning' in controls:
            self.controls['turning'] = controls['turning']
        
        if 'attack' in controls:
            self.controls['attack'] = controls['attack']
    
    def test_collision(self, other):
        "Check if a collision with another polygon exists."
        if other in self.ignore_list:
            return False
            
        distance = self.polygon.distance(other)
        distance = abs(distance[0]) + abs(distance[1])
        if (distance) < (self.collide_size):
            collision = self.polygon.collidepoly(other)
            if collision.any():
                return True
        return False
    
    def new_collide_size(self, size):
        "Set new collision box size."
        self.collide_size = size
        
    def update(self, delta_time):
        if self.cooldown <= 0 and self.controls['attack']:
            self.cooldown = self.weapon_cooldown
            weapon = Weapon(self.functions)
            weapon.pos_x = self.pos_x
            weapon.pos_y = self.pos_y
            weapon.angle = self.angle
            weapon.max_speed = 100 + self.speed
            weapon.controls['thrust'] = 1
            self.ignore_list.append(weapon.polygon)
            
            self.functions['add_entity'](weapon, etype='collider')
        
        else:
            self.cooldown -= self.weapon_cooldown * delta_time
            
        return Entity.update(self, delta_time)
