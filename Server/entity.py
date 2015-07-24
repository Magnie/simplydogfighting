from math import cos, sin, radians
from pylygon.polygon import Polygon

class Entity(object):
    
    def __init__(self, functions):
        self.functions = functions
        # Defaults
        self.pos_x = 0
        self.pos_y = 0
        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0
        self.vel_angle = 0
        
        
        self.old_angle = -1
        self.max_x = 0
        self.max_y = 0
        
        self.turn_rate = 180 # Degrees per second
        self.accel = 25
        self.max_speed = 50
        self.speed = 0
        
        self.health = 10
        
        collide_size = 10 # In pixels
        self.collide_size = collide_size
        new_box = []
        new_box.append((self.pos_y + collide_size, self.pos_x - collide_size))
        new_box.append((self.pos_y + collide_size, self.pos_x + collide_size))
        new_box.append((self.pos_y - collide_size, self.pos_x + collide_size))
        new_box.append((self.pos_y - collide_size, self.pos_x - collide_size))
        self.polygon = Polygon(new_box)
        
        self.type = 'entity'
        
        self.object_id = -1
        if 'new_id' in self.functions:
            self.object_id = self.functions['new_id']()
        
        self.name = 'Observer'
        self.controls = {
            'thrust': 0,
            'turning': 0,
        }
    
    def hit_by(self, other):
        "What to do when hit by another object"
        print self, 'hit'
    
    def test_collision(self, other):
        "Check if a collision with another polygon exists"
        distance = self.polygon.distance(other)
        distance = abs(distance[0]) + abs(distance[1])
        if (distance) < (self.collide_size):
            collision = self.polygon.collidepoly(other)
            if collision.any():
                return True
        return False
    
    def move(self, x, y):
        "Moves the object and it's collision layer"
        self.polygon.C = x, y
        self.pos_x = x
        self.pos_y = y
    
    def rotate(self, angle):
        "Rotate the entity and the collision box"
        self.angle = angle
        self.polygon.rotate(radians(angle))
        
    def update(self, delta_time):
        "Update ship position and direction"
        controls = self.controls
        accel = self.accel * delta_time
        angle = self.angle + 90 # 0 is up.
        
        if self.old_angle != angle:
            self.old_angle = angle
            temp_vx = 0
            temp_vy = 0
            while abs(temp_vx) + abs(temp_vy) < self.max_speed:
                temp_vx += cos(radians(angle)) * accel
                temp_vy += sin(radians(angle)) * accel
            
            self.max_x = temp_vx
            self.max_y = temp_vy
        
        max_x = self.max_x
        max_y = self.max_y
        
        if controls['thrust'] == 1:
            # Calculate what the future velocities will be. If they are greater
            # than the max speeds calculated earlier, ignore it.
            future_x = self.vel_x + cos(radians(angle)) * accel
            future_y = self.vel_y + sin(radians(angle)) * accel
            
            if (future_y < max_y) if max_y > 0 else (future_y > max_y):
                self.vel_y = future_y
            
            if (future_x < max_x) if max_x > 0 else (future_x > max_x):
                self.vel_x = future_x
        
        if controls['turning'] == 1:
            self.vel_angle = self.turn_rate
        
        elif controls['turning'] == 2:
            self.vel_angle = self.turn_rate * -1
        
        else:
            self.vel_angle = 0
        
        # Update stats
        new_x = self.pos_x + (self.vel_x * delta_time)
        new_y = self.pos_y + (self.vel_y * delta_time)
        self.move(new_x, new_y)
        
        new_angle = self.angle + (self.vel_angle * delta_time)
        if new_angle < 0:
            new_angle += 360
        self.rotate(new_angle)
        
        self.speed = abs(self.vel_x) + abs(self.vel_y)

        data = {
            'object_id': self.object_id,
            'type': self.type,
            'pos_x': self.pos_x,
            'pos_y': self.pos_y,
            'angle': self.angle,
            'vel_x': self.vel_x,
            'vel_y': self.vel_y,
            'vel_angle': self.vel_angle, # Turning "velocity"
        }
        return data
