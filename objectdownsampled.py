class GenerateObjectDownsampled():

    def __init__(self, xskip, yskip, resx, resy):
        self.xskip = xskip;
        self.yskip = yskip;
        self.resx = resx;
        self.resy = resy;


    def generate(self, objects):

        self.objectdownsampled = [];
        self.objectdownsampledmap = [];

        for x in range(0, int(self.resx * self.resy / (self.xskip * self.yskip))):
            self.objectdownsampled.append(0);

        for object in objects:

            x = (object[0] + object[2])/2;
            y = (object[1] + object[3])/2;

            x = int(x / self.xskip);
            y = int(y / self.yskip);
            index = y + x * int(self.resy / self.yskip);

            self.objectdownsampled[index] = object[4];
            self.objectdownsampledmap.append(x);
            self.objectdownsampledmap.append(y);
            self.objectdownsampledmap.append(object[4]);

        return (self.objectdownsampled, self.objectdownsampledmap);
