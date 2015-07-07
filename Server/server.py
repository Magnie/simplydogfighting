from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from PodSixNet.Connection import ConnectionListener, connection
from time import time, sleep
from math import cos, sin, radians

FPS = 30
DEBUG = False

class ClientChannel(Channel):
    
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
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
        
        self.health = 10
        
        self.collide_size = 10 # In pixels
        
        self.object_id = -1
        self.name = 'Observer'
        self.controls = {
            'thrust': 0,
            'turning': 0,
            'attack': 0,
        }
    
    def update(self, fps):
        "Update ship position and direction"
        controls = self.controls
        accel = self.accel * fps
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
        self.pos_x += self.vel_x * fps
        self.pos_y += self.vel_y * fps
        self.angle += self.vel_angle * fps
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
    
    def new_id(self, object_id):
        self.object_id = object_id
    
    def Close(self):
        "Called when a player disconnects."
        self._server.Disconnected(self)

    def Network(self, data):
        if DEBUG:
            print data

    def Network_name(self, data):
        if 'name' in data:
            self.name = data['name']
    
    def Network_collide(self, data):
        if 'size' in data:
            if type(data['size'], int) and data['size'] > 9:
                self.collide_size = data['size']
    
    def Network_controls(self, data):
        if 'controls' in data:
            controls = data['controls']
            if 'thrust' in controls:
                self.controls['thrust'] = controls['thrust']
            
            if 'turning' in controls:
                self.controls['turning'] = controls['turning']
            
            if 'attack' in controls:
                self.controls['attack'] = controls['attack']


class DFServer(Server):

    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.clients = []
        self.id_inc = 0
    
    def tick(self, fps):
        clients = self.clients
        
        # Update all the players.
        updates = []
        for c in clients:
            updates.append(c.update(fps))
        
        # Send the updates to everyone.
        action = {
            'action': 'update',
            'updates': updates,
        }
        self.send_all(action)
    
    def get_id(self):
        self.id_inc += 1
        return self.id_inc
    
    def send_all(self, action):
        clients = self.clients
        for c in clients:
            c.Send(action)

    def Connected(self, channel, addr):
        channel.new_id(self.get_id())
        self.clients.append(channel)
        print 'new connection:', channel, addr
    
    def Disconnected(self, player_obj):
        action = {
            'action': 'delete',
            'object_id': player_obj.object_id,
        }
        self.send_all(action)
        self.clients.remove(player_obj)


running = True
server = DFServer(localaddr=('127.0.0.1', 34002))
dyn_fps = FPS
real_fps = lambda: 1.0 / dyn_fps
while running:
    current_time = time()
    # Tick Update
    server.Pump()
    server.tick(real_fps())
    
    time_taken = time() - current_time
    time_left = real_fps() - time_taken
    
    # If lagging behind, adjust FPS to handle the load.
    if time_left < 0:
        time_left = 0
        dyn_fps -= 1
    
    else:
        if dyn_fps < FPS:
            dyn_fps += 0.5

    sleep(time_left)
