from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty

from starfield import Starfield

from PodSixNet.Connection import connection
from PodSixNet.Connection import ConnectionListener

from time import time

FPS = 30
DEBUG = False
HOST = 'scclassroom.com'
PORT = 34002

class DogfightGame(FloatLayout, ConnectionListener):
    def __init__(self, *kargs, **kwargs):
        FloatLayout.__init__(self, *kargs, **kwargs)
        
        # Bind the keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_keyboard_down)
        self._keyboard.bind(on_key_up = self._on_keyboard_up)
        
        # Set up the controls
        self.controls = {
            'thrust': 0,
            'turning': 0,
            'attack': 0,
        }
        self.old_controls = dict(self.controls)
        
        self.hud = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.hud)
        
        health_label = Label(
            text='Health',
            pos_hint={
                'top': 1.4,
                'center_x': 0.5,
            }
        )
        self.hud.add_widget(health_label)
        
        self.health = ProgressBar(
            pos_hint={
                'top': 1,
                'center_x': 0.5,
            },
            size_hint=(0.5, 0.1)
        )
        self.hud.add_widget(self.health)
        
        # Screen objects
        self.space = FloatLayout()
        self.add_widget(self.space)
        
        # Objects to display
        self.objects = {}
        self.player_id = None
        
        
        # Debug Object
        if DEBUG:
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
            self.add_object(data)
    
    # Network Logic
    def send_action(self, action):
        "Send data to the server"
        self.Send(action)
        
    def Network_update(self, data):
        "Server says these objects need updates"
        for u in data['updates']:
            self.update_object(u)
    
    def Network_player(self, data):
        "Response from server giving player data"
        if 'info' in data:
            if 'id' in data['info']:
                self.player_id = data['info']['id']
                
                self.health.max = data['info']['max_health']
                self.health.value = data['info']['health']
    
    def Network_delete(self, data):
        "Server says an object was removed"
        self.remove_object(data['object_id'])
    
    def Network(self, data):
        "All network data comes through here."
        if DEBUG:
            print 'Game Window:', data
    
    # Game Logic
    def update(self, delta_time):
        "Update all the objects on the screen"
        # Send any new controls to the server.
        self.send_action({'action': 'player'})
        self.update_controls()
        if game.connected:
            self.Pump()
        
        # Update each object
        objects = self.objects
        for i in objects:
            obj = objects[i]
            obj.update(delta_time)
        
        if self.player_id:
            x, y = self.objects[self.player_id].true_pos
            self.starfield.scroll(x, y, 0)
    
    def update_object(self, data):
        "Update an object based on the data given"
        if not data:
            return
        
        # If the object doesn't exist, create it.
        object_id = data['object_id']
        if object_id not in self.objects:
            self.add_object(data)
            return
        
        # Update it with new data.
        self.objects[object_id].update_data(data)
        
        # If it is not the player, then tell the object who the player is.
        if self.player_id and self.player_id != object_id:
            player = self.objects[self.player_id]
            self.objects[object_id].new_player(player)
    
    def add_object(self, data):
        "Add new object to the screen."
        object_id = data['object_id']
        
        # Image for each type of entity
        if data['type'] == 'player':
            image = 'images/player.png'
            
        elif data['type'] == 'bullet':
            image = 'images/weapon.png'
        
        elif data['type'] == 'planet':
            image = 'images/planet.png'
            
        else: # TODO: Create generic object image.
            image = 'images/player.png'
        
        # Create the new object and update it with the data.
        new_object = GenericObject(source=image)
        self.objects[object_id] = new_object
        self.update_object(data)
        
        # Add it to the display.
        self.space.add_widget(new_object)
    
    def remove_object(self, object_id):
        "Remove an object from the screen"
        if object_id in self.objects:
            obj = self.objects[object_id]
            self.space.remove_widget(obj)
            
            # Delete all references. Clean up.
            del self.objects[object_id]
            del obj

    # Game Controls
    def update_controls(self):
        "Check if there are updates to the controls. If so, send it to the server"
        if self.controls != self.old_controls:
            self.old_controls = dict(self.controls)
            action = {
                'action': 'controls',
                'controls': self.old_controls,
            }
            self.send_action(action)
        
    def _keyboard_closed(self):
        "If the keyboard is closed for some reason (tablets) unbind it"
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        "When a key is pressed, update the controls"
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
        "When a key is lifted, update the controls"
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
    "Any object displayed on the screen."
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel_angle = NumericProperty(0)
    true_pos = (0, 0)
    player = None
    angle = NumericProperty(0)
    source = StringProperty('images/player.png')
    
    def update(self, delta_time):
        "Update the screen based on velocities sent by the server."
        pos = self.true_pos
        angle = self.angle
        
        # Create updated values
        new_x = pos[0] + (self.vel_x * delta_time)
        new_y = pos[1] + (self.vel_y * delta_time)
        new_angle = angle + (self.vel_angle * delta_time)
        
        # Update the variables
        self.true_pos = (new_x, new_y)
        self.angle = new_angle
        
        # Update screen position
        self.move()
    
    def update_data(self, data):
        "Update to the most recent values sent from the server."
        self.true_pos = (data['pos_x'], data['pos_y'])
        self.angle = data['angle']
        self.vel_x = data['vel_x']
        self.vel_y = data['vel_y']
        self.vel_angle = data['vel_angle']
        
        # Update screen position
        self.move()
    
    def move(self):
        "Move the object to the proper location on the screen"
        if self.player:
            # If the player object is set, set the position relative to the
            # player object
            new_x = (self.true_pos[0] - self.player.true_pos[0]) + (Window.width / 2.0)
            new_y = (self.true_pos[1] - self.player.true_pos[1]) + (Window.height / 2.0)
            self.center = (new_x, new_y)
        else:
            # If the player object is not set, assume it is the player object
            # and set the position to the center of the screen
            self.center = (Window.width / 2.0, Window.height / 2.0)
    
    def new_player(self, entity):
        "Set the player object"
        self.player = entity


class DogfightApp(App, ConnectionListener):
    
    def __init__(self, *kargs, **kwargs):
        App.__init__(self, *kargs, **kwargs)
        self.connected = True
        self.Connect((HOST, PORT))
        
        self.count = 0
        self.time = 0
        
    
    def update(self, delta_time):
        "Check for new updates from server and tell the game to update."
        # How many times update() is truly called per second.
        if self.time != round(time()):
            if DEBUG:
                print self.count
            
            self.count = 0
            self.time = round(time())
        
        self.count += 1
        # End counter. This section can be removed.
        
        if self.connected:
            connection.Pump()
            self.Pump()
        
        self.game.update(delta_time)
    
    def Network_connected(self, data):
        print 'Connected to the server!'
        self.connected = True
    
    def Network_disconnected(self, data):
        print 'Disconnected from the server!'
        self.connected = False
    
    def Network_error(self, data):
        print data
    
    def Network(self, data):
        "All network data received will come through this function"
        if DEBUG:
            print 'Game App:', data
    
    def build(self):
        "Return self.game as the main widget."
        Clock.schedule_interval(self.update, 1.0 / FPS)
        self.game = DogfightGame()
        return self.game


if __name__ == '__main__':
    game = DogfightApp()
    game.run()
