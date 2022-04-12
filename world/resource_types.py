from random import choice

BASE_VALUE = { 'trash': 1.5,
               'stone': 3,
               'wood': 4 }

def SIZES(v):
    if  v==0:
        return "empty"
    elif v<5:
        return "miniscule"
    elif v<10:
        return "tiny"
    elif v<30:
        return "small"
    elif v<80:
        return "medium"
    elif v<120:
        return "large"
    elif v<200:
        return "enormous"
    elif v<350:
        return "extravagant"
    elif v<500:
        return "gigantic"
    elif v<1000:
        return "ridiculous"
    elif v<2000:
        return "cosmic"
    elif v<5000:
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

WOOD = ['mahogany', 'oak', 'maple', 'birch', 'cedar', 'spruce', 'dogwood', 'fir', 'pine', "myrtle", "poplar", "sycamore"]
TREES = WOOD

FRUIT_TREES = ['apple','orange','pineapple','cherry','apricot','plum','peach','pear','pomegranate','banana',
               'coconut','lemon','lime','tangerine','fig']

trash = lambda: choice(TRASH_ADJS) + " " + choice(TRASH_OBS)
tree_type = lambda: choice(WOOD)
fruit_tree_type = lambda: choice(FRUIT_TREES)

# essence = lambda: '%s essence' % choice(ESSENCES)
# gem = lambda: '%s gem' % choice(GEMS)


