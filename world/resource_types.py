from random import choice


# RESOURCE_TYPES=['wood','stone', 'trash']

# GEMS = ['quartz', 'amethyst', 'topaz', 'emerald', 'aquamarine', 'ruby', 'amethyst', 'jade', 'diamond']
# ESSENCES = ['mind', 'power', 'reality', 'soul', 'space', 'time']

TRASH =    ['soda can', 'beer bottle', 'rusty spoon', 'rusty fork', 'rusty knife', 'cellophane wrapper',
               'empty bag of chips', 'soggy paper bag', 'dirty napkin', 'broken CD', 'dirty tampon', 'dirty condom',
               'dirty sock', 'old trash bag', 'piece of trash', 'rotten egg', 'soiled diaper', 'dirty syringe',
               'broken record', 'smelly sock', 'broken tape', 'broken gizmo', 'greasy sprocket', 'piece of junk']

WOOD = ['mahogany', 'oak', 'maple', 'birch', 'cedar', 'spruce', 'dogwood', 'fir', 'pine', "myrtle", "poplar", "sycamore"]
WOOD_SIZE = {'twig':1, 'branch':2, 'bundle':5}

trash = lambda: choice(TRASH_ADJS) + " " + choice(TRASH_OBS)
wood = lambda: '%s %s' % (choice(WOOD), choice(WOOD_SIZE))
# essence = lambda: '%s essence' % choice(ESSENCES)
# gem = lambda: '%s gem' % choice(GEMS)



"""

.db.resources = { "trash": 100,
                  "stone": 100,
                  "wood": 100 }



"""

TRASH_OBS = ['soda', 'beer', 'spoon', 'fork', 'knife', 'wrapper', 'bag', 'can', 'napkin',' towel', 'CD',
             'cassette', 'diaper', 'syringe', 'record', 'condom', 'sock', 'tape', 'piece of junk', 'piece of trash',
             'paper bag', 'trash bag', 'carton', 'gizmo', 'sprocket']
TRASH_ADJS = ['broken', 'greasy', 'damaged', 'empty', 'irreparable', 'dirty', 'old', 'used', 'smelly', 'stinky', 'worn',
              'inoperable', 'useless', 'blasted', 'shattered', 'putrid']