from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty

FPS = 30

class DogfightGame(Widget):
    def __init__(self, *kargs, **kwargs):
        Widget.__init__(self, *kargs, **kwargs)
        
        self.space = FloatLayout()
        self.objects = {}
        
        data = {
            'player_id': 0,
            'type': 'player',
            'pos_x': 100,
            'pos_y': 100,
            'angle': 50,
            'vel_x': 10,
            'vel_y': 0,
            'vel_angle': 120,
        }
        self.add_object(data)
        
        self.add_widget(self.space)
    
    def update(self, fps):
        objects = self.objects
        for i in objects:
            obj = objects[i]
            obj.update(fps)
    
    def add_object(self, data):
        "Add new object to the screen."
        player_id = data['player_id']
        
        if data['type'] == 'player':
            image = 'images/player.png'
            
        elif data['type'] == 'bullet':
            image = 'images/player.png'
            
        else:
            image = 'images/player.png'
            
        new_object = GenericObject(source=image)
        new_object.update_data(data)
        
        self.objects[player_id] = new_object
        self.space.add_widget(new_object)
    
    def remove_object(self, object_id):
        if object_id in self.objects:
            obj = self.objects[object_id]
            self.remove_widget(obj)
        
            del self.objects[object_id]
            del obj


class GenericObject(Image):
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel_angle = NumericProperty(0)
    angle = NumericProperty(0)
    source = StringProperty('images/player.png')
    
    def update(self, fps):
        pos = self.pos
        angle = self.angle
        
        # Create updated values
        new_x = pos[0] + (self.vel_x / fps)
        new_y = pos[1] + (self.vel_y / fps)
        new_angle = angle + (self.vel_angle / fps)
        
        # Update the variables
        self.pos = (new_x, new_y)
        self.angle = new_angle
    
    def update_data(self, data):
        self.pos = data['pos_x'], data['pos_y']
        self.angle = data['angle']
        
        self.vel_x = data['vel_x']
        self.vel_y = data['vel_y']
        self.vel_angle = data['vel_angle']


class DogfightApp(App):
    
    def update(self, data):
        fps = FPS
        self.game.update(fps)
    
    def build(self):
        Clock.schedule_interval(self.update, 1.0 / FPS)
        self.game = DogfightGame()
        
        return self.game


if __name__ == '__main__':
    game = DogfightApp()
    game.run()
