from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from PodSixNet.Connection import ConnectionListener, connection
from time import time, sleep
from math import cos, sin, radians

FPS = 30.0

class ClientChannel(Channel):
    
    def __init__(self, *args, **kwargs):
        Client.__init__(self, *args, **kwargs)
        # Defaults
        self.pos_x = 0
        self.pos_y = 0
        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0
        
        self.turn_rate = 180 # Degrees per second
        self.accel = 5
        self.max_speed = 20
        
        self.health = 10
        
        self.collide_size = 10 # In pixels
        
        self.player_id = -1
        self.name = 'Observer'
        self.controls = {
            'thrust': 0,
            'turning': 0,
            'attack': 0,
        }
    
    def update(self, fps):
        "Update ship position and direction"
        controls = self.controls
        if controls['thrust'] == 1:
            future_x = self.vel_x + cos(radians(self.angle)) * self.accel
            future_y = self.vel_y + sin(radians(self.angle)) * self.accel
            
            if (future_x + future_y < self.max_speed):
                self.vel_x = future_x
                self.vel_y = future_y
        
        if controls['turning'] == 1:
            self.vel_angle = self.turn_rate
        
        elif controls['turning'] == 2:
            self.vel_angle = self.turn_rate * -1
        
        # Update stats
        self.pos_x += self.vel_x / fps
        self.pos_y += self.vel_y / fps
        self.angle += self.vel_angle / fps
        if self.angle < 0:
            self.angle += 360

        data = {
            'player_id': self.player_id,
            'type': 'player',
            'pos_x': self.pos_x,
            'pos_y': self.pos_y,
            'angle': self.angle,
            'vel_x': self.vel_x,
            'vel_y': self.vel_y,
            'vel_angle': self.vel_angle, # Turning "velocity"
        }
        return data
    
    def new_id(self, player_id):
        self.player_id = player_id

    def Network(self, data):
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
        for c in clients:
            action = {
                'action': 'update',
                'updates': updates,
            }
            c.Send(action)

    def Connected(self, channel, addr):
        self.id_inc += 1
        channel.new_id(self.id_inc)
        self.clients.append(channel)
        print 'new connection:', channel, addr


running = True
server = DFServer()
dyn_fps = FPS
while running:
    current_time = time()
    # Tick Update
    connection.Pump()
    server.Pump()
    server.tick(dyn_fps)
    
    time_taken = time() - current_time
    time_left = (1.0 / dyn_fps) - time_taken
    
    # If lagging behind, adjust FPS to handle the load.
    if time_left < 0:
        time_left = 0
        dyn_fps -= 1
    
    else:
        dyn_fps += 0.5

    sleep(time_left)
