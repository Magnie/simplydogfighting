from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from PodSixNet.Connection import ConnectionListener, connection
from time import time, sleep

from player import Player
from entity import Entity

FPS = 30
DEBUG = False

SYSTEM_SIZE = 1000

class ClientChannel(Channel):
    
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.functions = self._server.functions
        self.player = Player(self.functions)
        self.functions['add_entity'](self.player, etype='collided')
    
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
            size = data['size']
            
            # Generic Box
            if type(size, int) and size >= 10:
                self.new_collide_size(size)
            
            # TODO: Support for more intricate polygons
            if type(size, list) and len(size) >= 3:
                def distance((ax, ay), (bx, by)):
                    return ((ax ** 2) - (bx ** 2)) + ((ay ** 2) - (by ** 2))
                
                # Make sure the size of the polygon is at least the
                # minimum.
                perimeter = 0
                last_i = None
                length = 0
                for i in size:
                    if not last_i:
                        length = 0
                    else:
                        length = distance(i, last_i)
                        
                    perimeter += length
                    last_i = i
                
                if perimeter > 30:
                    self.new_polygon(size)
    
    def Network_controls(self, data):
        if 'controls' in data:
            controls = data['controls']
            self.player.new_controls(controls)


class DFServer(Server):

    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.id_inc = 0
        
        self.clients = []
        self.entities = []
        
        # Entities that can be hit.
        self.collided = []
        
        # Entites that hit.
        self.colliders = []
        
        # Static Objects in space.
        # Functions for the entities.
        self.functions = {
            'new_id': self.get_id,
            'add_entity': self.add_entity,
            'remove_entity': self.remove_entity,
            'system_size': SYSTEM_SIZE,
        }
        
        # A Planet to respawn at:
        planet = Entity(self.functions)
        planet.type = 'planet'
        self.entities.append(planet)
    
    def tick(self, fps):
        entities = self.entities
        collided = self.collided
        colliders = self.colliders
        
        # Test collisions
        for projectile in colliders:
            polygon = projectile.polygon
            for entity in collided:
                result = entity.test_collision(polygon)
                if result:
                    entity.hit_by(projectile)
                    projectile.hit()
                    break
        
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
    
    def add_entity(self, entity, etype=''):
        self.entities.append(entity)
        if etype == 'collider':
            self.colliders.append(entity)
        
        elif etype == 'collided':
            self.collided.append(entity)
    
    def remove_entity(self, entity):
        action = {
            'action': 'delete',
            'object_id': entity.object_id,
        }
        self.send_all(action)
        if entity in self.entities:
            self.entities.remove(entity)
        
        if entity in self.colliders:
            self.colliders.remove(entity)
        
        if entity in self.collided:
            self.collided.remove(entity)
    
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
real_fps = lambda x: 1.0 / x
frame_time = real_fps(dyn_fps)
while running:
    if (len(server.clients) == 0):
        dyn_fps = 10
    
    current_time = time()
    # Tick Update
    server.Pump()
    server.tick(frame_time)
    #Simulate server lag:
    #sleep(0.2) # 200MS! Ridiculous!
    
    time_taken = time() - current_time
    time_left = real_fps(dyn_fps) - time_taken
    
    # If lagging behind, adjust FPS to handle the load.
    if time_left < 0:
        dyn_fps -= 0.5
        frame_time = real_fps(dyn_fps) + abs(time_left)
        print 'Warning, lagging:', frame_time
        continue
    
    else:
        if dyn_fps < FPS:
            dyn_fps += 0.5
            frame_time = real_fps(dyn_fps)

    sleep(time_left)
