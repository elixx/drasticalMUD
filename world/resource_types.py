from random import choice


# RESOURCE_TYPES=['wood','stone', 'trash']

# WOOD = ['mahogany', 'oak', 'maple', 'birch', 'cedar', 'spruce', 'dogwood', 'fir', 'pine']
# WOOD_SIZE = {'twig':1, 'branch':2, 'bundle':5}
# GEMS = ['quartz', 'amethyst', 'topaz', 'emerald', 'aquamarine', 'ruby', 'amethyst', 'jade', 'diamond']
# ESSENCES = ['mind', 'power', 'reality', 'soul', 'space', 'time']

TRASH =    ['soda can', 'beer bottle', 'rusty spoon', 'rusty fork', 'rusty knife', 'cellophane wrapper',
               'empty bag of chips', 'soggy paper bag', 'dirty napkin', 'broken CD', 'dirty tampon', 'dirty condom',
               'dirty sock', 'old trash bag', 'piece of trash', 'rotten egg', 'soiled diaper', 'dirty syringe',
               'broken record', 'smelly sock', 'broken tape', 'broken gizmo', 'greasy sprocket', 'piece of junk']

trash = lambda: choice(TRASH)
# essence = lambda: '%s essence' % choice(ESSENCES)
# gem = lambda: '%s gem' % choice(GEMS)
# wood = lambda: '%s %s' % (choice(WOOD), choice(WOOD_SIZE))

"""

.db.resources = { "trash": 100,
                  "stone": 100,
                  "wood": 100 }



"""
