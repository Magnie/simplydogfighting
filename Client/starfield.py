import random

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.widget import Widget


class Starfield(Widget):
    max_stars = NumericProperty(256)
    density = NumericProperty(0.5)

    # the layers of the starfield, ordered furthest away to closest
    rectangles = ListProperty()

    def __init__(self, **kwargs):
        super(Starfield, self).__init__(**kwargs)
        self.on_size()

    def on_size(self, *largs):
        self.canvas.clear()
        self.rectangles = []

        for idx in xrange(2):
            star_size = 2

            # create a texture, defaults to rgb / ubyte
            self.texture = Texture.create(size=self.size, colorfmt='rgba')
            self.texture.wrap = 'repeat'

            # create a white star's pixel array (255)
            texture_size = star_size * 4
            buf = [255 for x in xrange(texture_size)]

            # then, convert the array to a ubyte string
            buf = ''.join(map(chr, buf))

            for x in xrange(int(self.density * 256)):
                # then blit the buffer randomly across the texture
                self.texture.blit_buffer(buf,
                    pos=(random.randint(0, self.size[0] - 1),
                        random.randint(0, self.size[1] - 1)),
                    size=(star_size, star_size),
                    colorfmt='rgba',
                    bufferfmt='ubyte'
                )

            with self.canvas:
                self.rectangles.append(Rectangle(texture=self.texture, pos=self.pos, size=self.size))

    def scroll(self, x, y, dt):
        t = Clock.get_boottime()
        
        x /= 100
        y /= 100

        modifier = 0.3
        for rectangle in self.rectangles:
            rectangle.tex_coords = (
                (x * modifier), (y * modifier),
                (x * modifier + 1), (y * modifier),
                (x * modifier + 1), (y * modifier + 1),
                (x * modifier), (y * modifier + 1)
            )
            modifier /= 2


class TestApp(App):
    def build(self):
        return Builder.load_string('''
BoxLayout:
    Starfield:
        ''')

if __name__ == '__main__':
    TestApp().run()
