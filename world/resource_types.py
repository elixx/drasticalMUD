from random import choice


# RESOURCE_TYPES=['wood','stone', 'trash', <fruit>]

# GEMS = ['quartz', 'amethyst', 'topaz', 'emerald', 'aquamarine', 'ruby', 'amethyst', 'jade', 'diamond']
# ESSENCES = ['mind', 'power', 'reality', 'soul', 'space', 'time']

# sizes for identification of bundles
# maybe other things too

BASE_VALUE = { 'trash': 1.5,
               'stone': 3,
               'wood': 4,
               'essence': 10 }

GEM_RARITY = { 0: ['stone','slate','silica','rock'],
             45: ['quartz', 'amethyst', 'aquamarine','topaz','silver','lapiz lazuli','copper'],
             85: ['jade', 'ruby', 'sapphire','gold'],
             90: ['diamond'],
             99: ['prismatic shard', 'magical essence', 'rare earth'] }

def GEM(v):
    gem = None
    for k in GEM_RARITY.keys():
        if v >= k:
              gem = choice(GEM_RARITY[k])
    return gem

def SIZES(v):
    if  v==0:
        return "empty"
    elif v<5:
        return "tiny"
    elif v<10:
        return "small"
    elif v<20:
        return "medium"
    elif v<30:
        return "large"
    elif v<50:
        return "giant"
    elif v<100:
        return "enormous"
    elif v<200:
        return "extravagant"
    elif v<300:
        return "gigantic"
    elif v<500:
        return "ridiculous"
    elif v<800:
        return "cosmic"
    elif v<1000:
        return "inconceivable"
    else:
        return "improperly balanced"


TRASH_OBS = ['soda', 'beer', 'spoon', 'fork', 'knife', 'wrapper', 'bag', 'can', 'napkin','towel', 'CD',
             'cassette', 'diaper', 'syringe', 'record', 'condom', 'sock', 'tape', 'piece of junk', 'piece of trash',
             'paper bag', 'trash bag', 'carton', 'gizmo', 'sprocket', 'debris', 'waste', 'refuse', 'scrap', 'rubbish',
             'garbage']
TRASH_ADJS = ['broken', 'greasy', 'damaged', 'empty', 'irreparable', 'dirty', 'old', 'used', 'smelly', 'stinky', 'worn',
              'inoperable', 'useless', 'rusted', 'dilapidated', 'busted', 'blasted', 'shattered', 'putrid', 'squeaky',
              'musty', 'musky', 'gross', 'ugly', 'horrid', 'obnoxious', 'intolerable', 'offensive']

# TRASH =    ['soda can', 'beer bottle', 'rusty spoon', 'rusty fork', 'rusty knife', 'cellophane wrapper',
#                'empty bag of chips', 'soggy paper bag', 'dirty napkin', 'broken CD', 'dirty tampon', 'dirty condom',
#                'dirty sock', 'old trash bag', 'piece of trash', 'rotten egg', 'soiled diaper', 'dirty syringe',
#                'broken record', 'smelly sock', 'broken tape', 'broken gizmo', 'greasy sprocket', 'piece of junk']

WOOD = ['mahogany', 'oak', 'maple', 'birch', 'cedar', 'spruce', 'dogwood', 'fir', 'pine', "myrtle", "poplar", "sycamore"]

FRUIT_TREES = ['apple','orange','pineapple','cherry','apricot','plum','peach','pear','pomegranate','banana',
               'coconut','lemon','lime','tangerine','fig']

trash = lambda: choice(TRASH_ADJS) + " " + choice(TRASH_OBS)
tree_type = lambda: choice(WOOD)
fruit_tree_type = lambda: choice(FRUIT_TREES)

# essence = lambda: '%s essence' % choice(ESSENCES)
# gem = lambda: '%s gem' % choice(GEMS)



"""

.db.resources = { "trash": 100,
                  "stone": 100,
                  "wood": 100 }



"""
