import numpy as np

class NoteDrawer():


    def __init__(self, pygame, surface, width, height, sx, sy):

        self.width = width
        self.height = height
        self.sx = sx
        self.sy = sy
        self.pygame = pygame
        self.surface = surface


    def draw_notes(self, downsampledmap, min_depth, max_depth, min_map, max_map, offsetx, offsety):

        self.pygame.draw.rect(self.surface, (0,255,0), self.pygame.Rect(offsetx,offsety,self.width,self.height))
        for i in range(0, int(len(downsampledmap)/3)):

            x = downsampledmap[i*3] * (self.width / self.sx)
            y = downsampledmap[i*3 + 1] * (self.height / self.sy)
            color = (downsampledmap[i*3 + 2] - min_depth) * (max_map - min_map) / (max_depth - min_depth) + min_depth

            if(color < 0): color = 0
            if(color > 255): color = 255

            self.pygame.draw.rect(self.surface, (color,0,0), self.pygame.Rect(offsetx + x,offsety + y,self.width / self.sx, self.height / self.sy))

    def draw_objects(self, objectdownsampledmap, offsetx, offsety):

        self.pygame.draw.rect(self.surface, (0,255,0), self.pygame.Rect(offsetx,offsety,self.width,self.height))
        for i in range(0, int(len(objectdownsampledmap)/3)):

            x = objectdownsampledmap[i*3] * (self.width / self.sx)
            y = objectdownsampledmap[i*3 + 1] * (self.height / self.sy)

            color = 255

            self.pygame.draw.rect(self.surface, (color,0,0), self.pygame.Rect(offsetx + x,offsety + y,self.width / self.sx,self.height / self.sy))

    def draw_image(self, x, y):
        self.surface.blit(self.imagesurface, (x,y))

    def draw_soundpoint(self, soundpoint, offsetx, offsety):

        x = soundpoint[0] * (self.width / self.sx)
        y = soundpoint[1] * (self.height / self.sy)

        self.pygame.draw.rect(self.surface, (255,255,255), self.pygame.Rect(offsetx + x,offsety + y,self.width / self.sx,self.height / self.sy))

    def convert_image(self, color_frame, width, height):
        color_image = np.asanyarray(color_frame.get_data())
        color_image = color_image.transpose(1,0,2)
        newsurface = self.pygame.surfarray.make_surface(color_image)
        newsurface = self.pygame.transform.scale(newsurface, (width, height))
        self.imagesurface = newsurface
