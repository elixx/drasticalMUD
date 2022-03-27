from typeclasses.objects import Object

RESOURCE_TYPES={'wood':     0.3,
                'stone':    0.3,
                'cloth':    0.15,
                'metal':    0.15,
                'gem':      0.05,
                'essence':  0.05}

GEM_TYPES =     ['quartz','amethyst','topaz','emerald','aquamarine','ruby','amethyst','jade','diamond']
ESSENCE_TYPES = ['mind','power','reality','soul','space','time']

class Resource(Object):
    def at_object_creation(self):
        pass
        super().at_object_creation()

