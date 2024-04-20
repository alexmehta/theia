class PlayTools():


    def __init__(self, pygame, surface):

        self.pygame = pygame;
        self.surface = surface;

        self.playicon = self.pygame.image.load("./images/play.png");
        self.pauseicon = self.pygame.image.load("./images/pause.png");

        self.restarticon = self.pygame.image.load("./images/restart.png");

        self.forwardicon = self.pygame.image.load("./images/forward.png");

        self.paused = False;
        self.mousedown = False;

    def draw(self, x, y, buttonsize, buttonpadding):

        mousepressed = self.pygame.mouse.get_pressed()[0];

        clicked = mousepressed and not self.mousedown;

        hoverrestart = False;
        hoverpaused = False;
        hoverforward = False;

        hoverrestart = self.render_button(x,y,buttonsize,buttonsize,self.restarticon,(50,50,50),(0,0,125),4);

        if self.paused:
            hoverpaused = self.render_button(x+buttonsize+buttonpadding,y,buttonsize,buttonsize,self.playicon,(50,50,50),(0,0,125),4);
        else:
            hoverpaused = self.render_button(x+buttonsize+buttonpadding,y,buttonsize,buttonsize,self.pauseicon,(50,50,50),(0,0,125),4);

        hoverforward = self.render_button(x+2*buttonsize+2*buttonpadding,y,buttonsize,buttonsize,self.forwardicon,(50,50,50),(0,0,125),4);

        self.mousedown = mousepressed;



        return [hoverrestart and clicked, hoverpaused and clicked, hoverforward and clicked];

    def render_button(self, x, y, w, h, image, color, hovercolor, hoverwidth):

        mousepos = self.pygame.mouse.get_pos()

        image = self.pygame.transform.scale(image, (w,h));

        self.pygame.draw.rect(self.surface, color, self.pygame.Rect(x,y,w,h) );
        self.surface.blit(image, (x,y));

        hovering = x + w >= mousepos[0] and mousepos[0] > x and y + h >= mousepos[1] and mousepos[1] >= y;

        if hovering:
            self.pygame.draw.rect(self.surface, hovercolor, self.pygame.Rect(x,y,w,h), hoverwidth);

        return hovering
