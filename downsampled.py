from get_soundindex import get_soundindex

class GenerateDownsampled():



    def __init__(self, xskip, yskip, resx, resy, soundsettings):
        self.xskip = xskip
        self.yskip = yskip
        self.resx = resx
        self.resy = resy
        self.soundsettings = soundsettings

    def generate(self, depth_frame, checkrange, checkskip):

        self.downsampledmap = []
        self.downsampled = []
        self.chunkings = {}

        for y in range(0, self.resy, checkskip):
            rowdone = True
            for x in range(0, self.resx, checkskip):

                xr = int(x / checkrange)
                yr = int(y / checkrange)

                if(xr in self.chunkings and yr in self.chunkings[xr]):
                    x = (xr + 1) * checkrange - 1
                    continue

                rowdone = False

                distance = depth_frame.get_distance(x, y)

                if(get_soundindex(distance, self.soundsettings) == None): continue

                if(xr in self.chunkings):
                    self.chunkings[xr][yr] = distance
                else:
                    self.chunkings[xr] = {}
                    self.chunkings[xr][yr] = distance

            if(rowdone):
                yr = int(y / checkrange)
                y = (yr + 1) * checkrange - 1


        for x in range(0, int(self.resx / self.xskip)):
            for y in range(0, int(self.resy / self.yskip)):
                depth = depth_frame.get_distance(x * self.xskip, y * self.yskip)

                inbound = get_soundindex(depth, self.soundsettings) != None

                if not inbound:
                    xr = int(x * self.xskip / checkrange)
                    yr = int(y * self.yskip / checkrange)

                    if(xr in self.chunkings and yr in self.chunkings[xr]):
                        inbound = True
                        depth = self.chunkings[xr][yr]

                if inbound:
                    self.downsampledmap.append( x )
                    self.downsampledmap.append( y )
                    self.downsampledmap.append( depth )
                    self.downsampled.append( depth )
                    foundinbound = True

                else:
                    self.downsampled.append(0)

        return (self.downsampled, self.downsampledmap)
