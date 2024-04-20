import json;

class SettingsGUI():



    def __init__(self, pygame, surface, settings, config, my_font):

        self.settings = settings;
        self.settings_list = [];

        self.originalconfig = config;
        self.pygame = pygame;
        self.surface = surface;
        self.mousepressed = False;
        self.clicked = False;
        self.closed = True;
        self.my_font = my_font;

        self.settingsicon = self.pygame.image.load("./images/settings.png");
        self.closeicon = self.pygame.image.load("./images/close.png");
        self.undoicon = self.pygame.image.load("./images/undo.png");

        self.load_settings();


    def undo_settings(self):
        if len(self.settings_list) > 0:

            self.settings = self.settings_list[len(self.settings_list)-1];
            self.settings_list.pop();
            self.load_settings()
            self.apply_settings(False);

    def load_settings(self):

        self.gui = {}
        self.config = json.loads(json.dumps(self.originalconfig));

        keys = self.config.keys();

        print(keys);

        for key in keys:

            if key in ["xoffset", "yoffset", "xscale", "yscale", "textxoffset", "settingsbuttonxoffset", "settingsbuttonyoffset", "settingsbuttonsize", "settingswidth"]: continue;

            variable = self.settings[key];

            if(isinstance(variable, bool)):

                self.config[key]["pos"][0] *= self.config["xscale"]
                self.config[key]["pos"][1] *= self.config["yscale"];

                self.config[key]["pos"][0] += self.config["xoffset"]
                self.config[key]["pos"][1] += self.config["yoffset"]

                self.config[key]["sizing"][0] *= self.config["xscale"]
                self.config[key]["sizing"][1] *= self.config["yscale"]

                self.gui[key] = {
                    "type": "bool",
                    "name": key,
                    "value": variable,
                    "pos": self.config[key]["pos"],
                    "sizing": self.config[key]["sizing"],
                    "background": self.config[key]["background"]
                }

            elif(isinstance(variable, (int,float))):

                self.config[key]["pos"][0] *= self.config["xscale"]
                self.config[key]["pos"][1] *= self.config["yscale"];

                self.config[key]["pos"][0] += self.config["xoffset"]
                self.config[key]["pos"][1] += self.config["yoffset"]

                self.config[key]["sizing"][0] *= self.config["xscale"]
                self.config[key]["sizing"][1] *= self.config["yscale"]

                self.config[key]["sizing"][2] *= self.config["xscale"]
                self.config[key]["sizing"][3] *= self.config["yscale"]

                self.gui[key] = {
                    "type": "scale",
                    "name": key,
                    "value": variable,
                    "pos": self.config[key]["pos"],
                    "sizing": self.config[key]["sizing"],
                    "bounds": self.config[key]["bounds"],
                    "dragging": False,
                    "roundint": isinstance(variable, int),
                    "background": self.config[key]["background"]
                }



    def run(self):


        mousepressed = self.pygame.mouse.get_pressed()[0];

        self.clicked = mousepressed and not self.mousepressed;
        self.mousepressed = mousepressed;

        keys = self.gui.keys();

        mousepos = self.pygame.mouse.get_pos();

        if not self.closed:


            for key in keys:
                if "background" in self.gui[key]:
                    self.pygame.draw.rect(self.surface, (self.gui[key]["background"][4],self.gui[key]["background"][5],self.gui[key]["background"][6] ),
                    self.pygame.Rect(self.gui[key]["background"][0], self.gui[key]["background"][1], self.gui[key]["background"][2], self.gui[key]["background"][3]))

            for key in keys:

                me = self.gui[key];

                self.render_text(key, (me["pos"][0] + self.config["textxoffset"], me["pos"][1]), (255,255,255), self.my_font, False)

                if me["type"] == "bool":

                    posy = me["pos"][1] - me["sizing"][1] / 2
                    posx = me["pos"][0];

                    hovering = (posx + me["sizing"][0] >= mousepos[0] and mousepos[0] >= posx) and (posy + me["sizing"][1] >= mousepos[1] and mousepos[1] >= posy)

                    if self.clicked:

                        if hovering:
                            me["value"] = not me["value"];
                            self.apply_settings();

                    color = (255,255,255)

                    if me["value"] == True:
                        color = (0,255,0)

                    self.pygame.draw.rect(self.surface, color, self.pygame.Rect(posx, posy, me["sizing"][0], me["sizing"][1]) );

                    if hovering:
                        self.pygame.draw.rect(self.surface, (0,0,125), self.pygame.Rect(posx, posy, me["sizing"][0], me["sizing"][1]), 4 );



                if me["type"] == "scale":

                    portion = (me["value"] - me["bounds"][0] ) / ( me["bounds"][1] - me["bounds"][0] );
                    xpos = portion * me["sizing"][0];

                    self.pygame.draw.rect(self.surface, (255,255,255), self.pygame.Rect(me["pos"][0], me["pos"][1], me["sizing"][0], me["sizing"][1]));

                    indicatorx = xpos + me["pos"][0] - me["sizing"][2]/2;
                    indicatory = me["pos"][1] + me["sizing"][1]/2 - me["sizing"][3]/2;

                    self.pygame.draw.rect(self.surface, (255,255,255), self.pygame.Rect(indicatorx, indicatory, me["sizing"][2], me["sizing"][3]))

                    hovering = (indicatorx + me["sizing"][2] >= mousepos[0] and mousepos[0] >= indicatorx) and (indicatory + me["sizing"][3] >= mousepos[1] and mousepos[1] >= indicatory)

                    if self.clicked:

                        if hovering:
                            me["dragging"] = True;

                    if me["dragging"]:
                        hovering = True;
                        if not mousepressed:
                            me["dragging"] = False;
                            self.apply_settings();
                        else:
                            mouseportion = (mousepos[0] - me["pos"][0]) / (me["sizing"][0]);

                            if mouseportion < 0: mouseportion = 0;
                            if mouseportion > 1: mouseportion = 1;

                            me["value"] = float('%.1f'%(mouseportion * (me["bounds"][1] - me["bounds"][0]) + me["bounds"][0]));
                            if(me["roundint"] == True): me["value"] = int(me["value"])

                    if hovering:
                        self.pygame.draw.rect(self.surface, (0,0,125), self.pygame.Rect(indicatorx, indicatory, me["sizing"][2], me["sizing"][3]), 4)

                    self.render_text(str(me["value"]), (indicatorx + me["sizing"][2]/2, indicatory + me["sizing"][3] + 9), (255,255,255), self.my_font)

        if self.closed:

            posx = self.config["settingsbuttonxoffset"]
            posy = self.config["yoffset"] + self.config["settingsbuttonyoffset"]

            self.pygame.draw.rect(self.surface, (50,50,50), self.pygame.Rect(posx, posy, self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]) );

            settings_surface = self.pygame.transform.scale(self.settingsicon, (self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]));
            self.surface.blit(settings_surface, (posx,posy))


            hovering = (posx + self.config["settingsbuttonsize"] >= mousepos[0] and mousepos[0] >= posx) and (posy + self.config["settingsbuttonsize"] >= mousepos[1] and mousepos[1] >= posy)


            if hovering:
                self.pygame.draw.rect(self.surface, (0,0,125), self.pygame.Rect(posx, posy, self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]), 4 );

                if self.clicked:
                    self.closed = False;
        else:

            self.pygame.draw.rect(self.surface, (40,40,40), self.pygame.Rect(0, -100, self.config["settingswidth"], 2000), 8)

            posx = self.config["settingswidth"] - self.config["settingsbuttonsize"] - self.config["settingsbuttonxoffset"];
            posy = self.config["yoffset"] + self.config["settingsbuttonyoffset"]

            self.pygame.draw.rect(self.surface, (255,0,0), self.pygame.Rect(posx, posy, self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]) );

            close_surface = self.pygame.transform.scale(self.closeicon, (self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]));
            self.surface.blit(close_surface, (posx,posy))


            hovering = (posx + self.config["settingsbuttonsize"] >= mousepos[0] and mousepos[0] >= posx) and (posy + self.config["settingsbuttonsize"] >= mousepos[1] and mousepos[1] >= posy)

            if hovering:
                self.pygame.draw.rect(self.surface, (0,0,125), self.pygame.Rect(posx, posy, self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]), 4 );

                if self.clicked:
                    self.closed = True;

            pos2x = self.config["settingswidth"] - self.config["settingsbuttonsize"] - self.config["settingsbuttonxoffset"];
            pos2y = self.config["yoffset"] + self.config["settingsbuttonyoffset"] + self.config["settingsbuttonsize"] + 6

            self.pygame.draw.rect(self.surface, (60,60,60), self.pygame.Rect(pos2x, pos2y, self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]) );

            close_surface = self.pygame.transform.scale(self.undoicon, (self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]));
            self.surface.blit(close_surface, (pos2x,pos2y))


            hovering2 = (pos2x + self.config["settingsbuttonsize"] >= mousepos[0] and mousepos[0] >= pos2x) and (pos2y + self.config["settingsbuttonsize"] >= mousepos[1] and mousepos[1] >= pos2y)

            if hovering2:
                self.pygame.draw.rect(self.surface, (0,0,125), self.pygame.Rect(pos2x, pos2y, self.config["settingsbuttonsize"], self.config["settingsbuttonsize"]), 4 );

                if self.clicked:
                    self.undo_settings();


    def apply_settings(self, append=True):


        keys = self.gui.keys();

        if append: self.settings_list.append(json.loads(json.dumps(self.settings)))

        for key in keys:
            self.settings[key] = self.gui[key]["value"];

        settingsstring = json.dumps(self.settings, indent=2);

        with open("./settings/soundsettings.json", "w") as file:

            print("writing it all");
            file.write(settingsstring);






    def render_text(self, string, pos, col, my_font, centered=True):


        text_surface = my_font.render(string, False, col)

        w = text_surface.get_width();
        h = text_surface.get_height();

        if centered: self.surface.blit(text_surface, (pos[0] - int(w/2), pos[1] - h/2))
        else: self.surface.blit(text_surface, (pos[0], pos[1] - h/2))
