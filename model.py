from pyglet.gl import *
from pyglet.window import key
import pyrealsense2 as rs
import numpy as np


class Model:

    def get_tex(self, file):
        tex = pyglet.image.load(file).get_texture()
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)

    def __init__(self):

        self.batch = pyglet.graphics.Batch()

        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.device = self.pipeline_profile.get_device()

        found_rgb = False
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        self.config.enable_stream(rs.stream.depth, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)

        # Get stream profile and camera intrinsics
        self.sprofile = self.pipeline.get_active_profile()
        self.depth_profile = rs.video_stream_profile(self.profile.get_stream(rs.stream.depth))
        self.depth_intrinsics = self.depth_profile.get_intrinsics()
        self.w, self.h = self.depth_intrinsics.width, self.depth_intrinsics.height

# Processing blocks
pc = rs.pointcloud()
decimate = rs.decimation_filter()
decimate.set_option(rs.option.filter_magnitude, 2 ** state.decimate)
colorizer = rs.colorizer()
        tex_coords = ('t2f', (0, 0, 1, 0, 1, 1, 0, 1, ))

        x, y, z = 0, 0, -1
        X, Y, Z = x+1, y+1, z+1

        pyglet.gl.glPointSize(10)

        for i in range(1000):
            X, Y, Z = X+1, Y+1, Z+1
            x, y, z = x+1, y+1, z+1

            # 3 is the amount of points in the array,       here
            self.batch.add(3, GL_POINTS, None,
                           ('v3f', [x, y, z, x, y, Z, x, Y, Z]))

        print(self.batch)

    def draw(self):


        # Configure depth and color streams
 

        pipeline_wrapper = rs.pipeline_wrapper(pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        self.batch.draw()
