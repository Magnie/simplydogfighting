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
        self.functions = {
            'new_id': self._server.get_id,
            'add_entity': self._server.add_entity,
            'remove_entity': self._server.remove_entity,
        }
        self.player = Player(self.functions)
        self.functions['add_entity'](self.player)
    
    def update(self, delta_time):
        return self.player.update(delta_time)
    
    def Close(self):
        "Called when a player disconnects."
        self.functions['remove_entity'](self.player)
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
        self.entities = []
        self.id_inc = 0
    
    def tick(self, fps):
        entities = self.entities
        
        # Update all the players.
        updates = []
        for e in entities:
            updates.append(e.update(fps))
        
        # Send the updates to everyone.
        action = {
            'action': 'update',
            'updates': updates,
        }
        self.send_all(action)
    
    def add_entity(self, entity):
        self.entities.append(entity)
    
    def remove_entity(self, entity):
        action = {
            'action': 'delete',
            'object_id': entity.object_id,
        }
        self.send_all(action)
        self.entities.remove(entity)
    
    def get_id(self):
        self.id_inc += 1
        return self.id_inc
    
    def send_all(self, action):
        clients = self.clients
        for c in clients:
            c.Send(action)

    def Connected(self, channel, addr):
        self.clients.append(channel)
        print 'new connection:', channel, addr
    
    def Disconnected(self, client):
        self.clients.remove(client)


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
