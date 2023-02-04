from get_soundindex import get_soundindex;

class GenerateDownsampled():



    def __init__(self, checkrange, xskip, yskip, resx, resy, soundsettings):
        self.checkrange = checkrange;
        self.xskip = xskip;
        self.yskip = yskip;
        self.resx = resx;
        self.resy = resy;
        self.soundsettings = soundsettings;

    def generate(self, depth_frame):

        self.downsampledmap = [];
        self.downsampled = [];

        for x in range(int(self.resx / self.xskip)-1, -1, -1):
            for y in range(0, int(self.resy / self.yskip)):
                depth = depth_frame.get_distance(x * self.xskip, y * self.yskip);


                foundinbound = False;

                for j in range(-self.checkrange,self.checkrange):

                    if foundinbound: break;

                    for k in range(-self.checkrange,self.checkrange):

                        if foundinbound: break;

                        if x * self.xskip + j >= self.resx or x * self.xskip + j < 0: break;
                        if y * self.yskip + k >= self.resy or y * self.yskip + k < 0: break;

                        depth = depth_frame.get_distance(x * self.xskip + j, y * self.yskip + k);

                        inbound = get_soundindex(depth, self.soundsettings) != None;

                        if inbound:
                            self.downsampledmap.append( int(self.resx / self.xskip) - 1 - x )
                            self.downsampledmap.append( y )
                            self.downsampledmap.append( depth )
                            self.downsampled.append( depth );
                            foundinbound = True;

                if not foundinbound: self.downsampled.append(0);

        return (self.downsampled, self.downsampledmap);
