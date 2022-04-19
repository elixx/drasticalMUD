# ==[Growables]==========================================================================================#
GROWABLE = {
    'prototype_key': 'Spore',
    'prototype_desc': 'fungus spore',
    'prototype_tags': 'growable',
    'key': 'fungal spore',
    'typeclass': 'typeclasses.growable.GrowableObject'
}
SPORE = GROWABLE
TREE = {
    'prototype_key': 'TreeSeed',
    'prototype_desc': 'A harvestable tree',
    'prototype_tags': 'growable',
    'key': 'tree seed',
    'desc': 'This seed will grow into a tree of some kind.',
    'typeclass': 'typeclasses.growable.Tree'
}
FRUIT_TREE = {
    'prototype_key': 'FruitTreeSeed',
    'prototype_desc': 'A fruit tree seed',
    'prototype_tags': 'growable',
    'key': 'fruit tree seed',
    'desc': 'This seed will grow into a fruit-bearing tree of some kind.',
    'typeclass': 'typeclasses.growable.FruitTree',
    'harvest_spawn': True
}
PLANT = {
    'prototype_key': 'PlantSeed',
    'prototype_desc': 'plant seed',
    'prototype_tags': 'growable',
    'key': 'plant seed',
    'desc': 'This looks like the kind of seed that grows crops.',
    'typeclass': 'typeclasses.growable.Plant'
}
