class NoteDrawer():


    def __init__(self, pygame, surface, x, y, width, height, sx, sy):

        self.width = width;
        self.height = height;
        self.sx = sx;
        self.sy = sy;
        self.offsetx = x;
        self.offsety = y;
        self.pygame = pygame;
        self.surface = surface;



    def draw_notes(self, downsampledmap, min_depth, max_depth, min_map, max_map):

        self.pygame.draw.rect(self.surface, (0,255,0), self.pygame.Rect(self.offsetx,self.offsety,self.width,self.height));
        for i in range(0, int(len(downsampledmap)/3)):

            x = downsampledmap[i*3] * (self.width / self.sx)
            y = downsampledmap[i*3 + 1] * (self.height / self.sy)
            color = (downsampledmap[i*3 + 2] - min_depth) * (max_map - min_map) / (max_depth - min_depth) + min_depth

            if(color < 0): color = 0;
            if(color > 255): color = 255;

            self.pygame.draw.rect(self.surface, (color,0,0), self.pygame.Rect(self.offsetx + x,self.offsety + y,self.width / self.sx, self.height / self.sy));

    def draw_objects(self, objectdownsampledmap):
        
        self.pygame.draw.rect(self.surface, (0,255,0), self.pygame.Rect(self.offsetx,self.offsety,self.width,self.height));
        for i in range(0, int(len(objectdownsampledmap)/3)):

            x = objectdownsampledmap[i*3] * (self.width / self.sx)
            y = objectdownsampledmap[i*3 + 1] * (self.height / self.sy)

            color = 255;

            self.pygame.draw.rect(self.surface, (color,0,0), self.pygame.Rect(self.offsetx + x,self.offsety + y,self.width / self.sx,self.height / self.sy));

    def draw_soundpoint(self, soundpoint):

        x = soundpoint[0] * (self.width / self.sx)
        y = soundpoint[1] * (self.height / self.sy)

        self.pygame.draw.rect(self.surface, (255,255,255), self.pygame.Rect(self.offsetx + x,self.offsety + y,self.width / self.sx,self.height / self.sy));
