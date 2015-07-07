from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from PodSixNet.Connection import ConnectionListener, connection
from time import time, sleep

from player import Player

FPS = 30
DEBUG = False

class ClientChannel(Channel):
    
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.player = Player()
        self.object_id = -1
    
    def update(self, delta_time):
        return self.player.update(delta_time)
    
    def new_id(self, object_id):
        self.player.object_id = object_id
        self.object_id = object_id
    
    def Close(self):
        "Called when a player disconnects."
        self._server.Disconnected(self)

    def Network(self, data):
        if DEBUG:
            print data
    
    def Network_player(self, data):
        action = {
            'action': 'player',
            'info': self.player.get_info(),
        }
        self.Send(action)

    def Network_name(self, data):
        if 'name' in data:
            self.player.name = data['name']
    
    def Network_collide(self, data):
        if 'size' in data:
            if type(data['size'], int) and data['size'] > 9:
                self.new_collide_size(data['size'])
    
    def Network_controls(self, data):
        if 'controls' in data:
            controls = data['controls']
            self.player.new_controls(controls)


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
frame_time = real_fps()
while running:
    current_time = time()
    # Tick Update
    server.Pump()
    server.tick(frame_time)
    #Simulate server lag:
    #sleep(0.2) # 200MS! Ridiculous!
    
    time_taken = time() - current_time
    time_left = real_fps() - time_taken
    
    # If lagging behind, adjust FPS to handle the load.
    if time_left < 0:
        dyn_fps -= 0.5
        frame_time = real_fps() + abs(time_left)
        print 'Warning, lagging:', frame_time
        continue
    
    else:
        if dyn_fps < FPS:
            dyn_fps += 0.5

    sleep(time_left)
