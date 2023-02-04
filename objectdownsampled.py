class GenerateObjectDownsampled():

    def __init__(self, xskip, yskip, resx, resy):
        self.xskip = xskip
        self.yskip = yskip
        self.resx = resx
        self.resy = resy
        self.object_downsampled = []
        self.object_downsampled_map = []

    def generate(self, objects):

        for x in range(0, int(self.resx * self.resy / (self.xskip * self.yskip))):
            self.object_downsampled.append(0)

        for obj in objects:

            x = (obj[0] + obj[2])/2
            y = (obj[1] + obj[3])/2

            x = int(x / self.xskip)
            y = int(y / self.yskip)
            index = y + x * int(self.resy / self.yskip)

            self.object_downsampled[index] = obj[4]
            self.object_downsampled_map.append(x)
            self.object_downsampled_map.append(y)
            self.object_downsampled_map.append(obj[4])

        return (self.object_downsampled, self.object_downsampled_map)
