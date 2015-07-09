from math import cos, sin, radians


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
        
        self.collide_size = 10 # In pixels
        
        self.object_id = -1
        if 'new_id' in self.functions:
            self.object_id = self.functions['new_id']()
        
        self.name = 'Observer'
        self.controls = {
            'thrust': 0,
            'turning': 0,
        }
        
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
        self.pos_x += self.vel_x * delta_time
        self.pos_y += self.vel_y * delta_time
        self.angle += self.vel_angle * delta_time
        if self.angle < 0:
            self.angle += 360

        data = {
            'object_id': self.object_id,
            'type': 'player',
            'pos_x': self.pos_x,
            'pos_y': self.pos_y,
            'angle': self.angle,
            'vel_x': self.vel_x,
            'vel_y': self.vel_y,
            'vel_angle': self.vel_angle, # Turning "velocity"
        }
        return data
