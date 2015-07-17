from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.floatlayout import FloatLayout

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty

from PodSixNet.Connection import connection
from PodSixNet.Connection import ConnectionListener

from time import time

FPS = 30
DEBUG = False

class DogfightGame(Widget, ConnectionListener):
    def __init__(self, *kargs, **kwargs):
        Widget.__init__(self, *kargs, **kwargs)
        
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_keyboard_down)
        self._keyboard.bind(on_key_up = self._on_keyboard_up)
        
        self.controls = {
            'thrust': 0,
            'turning': 0,
            'attack': 0,
        }
        self.old_controls = dict(self.controls)
        
        self.space = FloatLayout()
        self.objects = {}
        self.player_id = None
        
        data = {
            'object_id': 0,
            'type': 'player',
            'pos_x': 100,
            'pos_y': 100,
            'angle': 50,
            'vel_x': 10,
            'vel_y': 10,
            'vel_angle': 120,
        }
        if DEBUG:
            self.add_object(data)
            
        self.add_widget(self.space)
    
    # Network Logic
    def send_action(self, action):
        self.Send(action)
        
    def Network_update(self, data):
        for u in data['updates']:
            self.update_object(u)
    
    def Network_player(self, data):
        if 'info' in data:
            if 'id' in data['info']:
                self.player_id = data['info']['id']
    
    def Network_delete(self, data):
        self.remove_object(data['object_id'])
    
    def Network(self, data):
        if DEBUG:
            print 'Game Window:', data
    
    # Game Logic
    def update(self, fps):
        # Send any new controls to the server.
        self.send_action({'action': 'player'})
        self.update_controls()
        self.Pump()
        
        objects = self.objects
        for i in objects:
            obj = objects[i]
            obj.update(fps)
    
    def update_object(self, data):
        if not data:
            return
            
        object_id = data['object_id']
        if object_id not in self.objects:
            self.add_object(data)
            return
        
        self.objects[object_id].update_data(data)
        if self.player_id and self.player_id != object_id:
            player = self.objects[self.player_id].true_pos
            self.objects[object_id].new_player(player)
    
    def add_object(self, data):
        "Add new object to the screen."
        object_id = data['object_id']
        
        if data['type'] == 'player':
            image = 'images/player.png'
            
        elif data['type'] == 'bullet':
            image = 'images/player.png'
            
        else:
            image = 'images/player.png'
            
        new_object = GenericObject(source=image)
        new_object.update_data(data)
        
        self.objects[object_id] = new_object
        self.space.add_widget(new_object)
    
    def remove_object(self, object_id):
        if object_id in self.objects:
            obj = self.objects[object_id]
            self.space.remove_widget(obj)
        
            del self.objects[object_id]
            del obj

    # Game Controls
    def update_controls(self):
        
        if self.controls != self.old_controls:
            self.old_controls = dict(self.controls)
            action = {
                'action': 'controls',
                'controls': self.old_controls,
            }
            self.send_action(action)
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        if key == 'w':
            self.controls['thrust'] = 1
        
        if key == 'a':
            self.controls['turning'] = 1
        
        elif key == 'd':
            self.controls['turning'] = 2
        
        if key == 'spacebar':
            self.controls['attack'] = 1

    def _on_keyboard_up(self, keyboard, keycode):
        key = keycode[1]
        if DEBUG:
            print key
        
        if key == 'w':
            self.controls['thrust'] = 0
        
        if key == 'a' or key == 'd':
            self.controls['turning'] = 0
        
        if key == 'spacebar':
            self.controls['attack'] = 0
        

class GenericObject(Image):
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel_angle = NumericProperty(0)
    true_pos = (0, 0)
    player = None
    angle = NumericProperty(0)
    source = StringProperty('images/player.png')
    
    def update(self, fps):
        pos = self.true_pos
        angle = self.angle
        
        # Create updated values
        new_x = pos[0] + (self.vel_x * fps)
        new_y = pos[1] + (self.vel_y * fps)
        new_angle = angle + (self.vel_angle * fps)
        
        # Update the variables
        self.true_pos = (new_x, new_y)
        if self.player:
            new_x = (self.true_pos[0] - self.player[0]) + (Window.width / 2.0)
            new_y = (self.true_pos[1] - self.player[1]) + (Window.height / 2.0)
            self.center = (new_x, new_y)
        else:
            self.center = (Window.width / 2.0, Window.height / 2.0)
            
        self.angle = new_angle
    
    def update_data(self, data):
        self.true_pos = (data['pos_x'], data['pos_y'])
        if self.player:
            new_x = (self.true_pos[0] - self.player[0]) + (Window.width / 2.0)
            new_y = (self.true_pos[1] - self.player[1]) + (Window.height / 2.0)
            self.center = (new_x, new_y)
        else:
            self.center = (Window.width / 2.0, Window.height / 2.0)
            
        self.angle = data['angle']
        
        self.vel_x = data['vel_x']
        self.vel_y = data['vel_y']
        self.vel_angle = data['vel_angle']
    
    def new_player(self, entity):
        self.player = entity


class DogfightApp(App, ConnectionListener):
    
    def __init__(self, *kargs, **kwargs):
        App.__init__(self, *kargs, **kwargs)
        self.connected = True
        self.Connect(('127.0.0.1', 34002))
        
        self.count = 0
        self.time = 0
    
    def update(self, data):
        
        # How many times update() is truly called per second.
        if self.time != round(time()):
            if DEBUG:
                print self.count
            
            self.count = 0
            self.time = round(time())
        
        self.count += 1
        
        fps = data
        
        if self.connected:
            connection.Pump()
            self.Pump()
        
        self.game.update(fps)
    
    def Network_connected(self, data):
        print 'Connected to the server!'
        self.connected = True
    
    def Network_disconnected(self, data):
        print 'Disconnected from the server!'
        self.connected = False
    
    def Network_error(self, data):
        print data
    
    def Network(self, data):
        if DEBUG:
            print 'Game App:', data
    
    def build(self):
        Clock.schedule_interval(self.update, 1.0 / FPS)
        self.game = DogfightGame()
        
        return self.game


if __name__ == '__main__':
    game = DogfightApp()
    game.run()
