
from player import Player
from window import Window
from pyglet.gl import *
from pyglet.window import key


if __name__ == '__main__':
    window = Window(width=854,height=480,caption='Depth View',resizable=True)
    glClearColor(0.5,0.7,1,1)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_CULL_FACE)
    pyglet.app.run()
