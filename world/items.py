from random import choice

#==[Growables]==========================================================================================#
GROWABLE = {
    'prototype_key': 'Growable',
    'prototype_desc': 'growable object',
    'prototype_tags': 'growable',
    'typeclass': 'typeclasses.growable.GrowableObject'
}

TREE = {
    'prototype_key': 'Tree',
    'prototype_desc': 'A harvestable tree',
    'prototype_tags': 'growable',
    'typeclass': 'typeclasses.growable.Tree'
}


FRUIT_TREE = {
    'prototype_key': 'FruitTree',
    'prototype_desc': 'A fruit tree',
    'prototype_tags': 'growable',
    'typeclass': 'typeclasses.growable.FruitTree',
    'harvest_spawn': True
}



PLANT = {
    'prototype_key': 'Plant',
    'prototype_desc': 'growable object',
    'prototype_tags': 'growable',
    'typeclass': 'typeclasses.growable.FruitTree'
}




CROP_BEARING_PLANT = {
    'prototype_parent': 'Plant',
    'prototype_key': 'CropBearingPlant',
    'prototype_tags': 'growable',
    'key': 'crop-bearing plant',
    'harvest_spawn': True
}





#==[Mining Tools]==========================================================================================#

MINING_TOOL = {
    'prototype_key': 'miningTool',
    'prototype_desc': 'Mining tool',
    'prototype_tags': 'mining',
    'typeclass': 'typeclasses.mining.MiningTool'
}

BASIC_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'basic pickaxe',
    'prototype_tags': 'mining',
    'key': 'basic pickaxe',
    'desc': 'an entry-level mining axe',
    'strength': 1,
    'speed': 1,
    'lifespan': 10,
    'max_lifespan': 10,
    'mining_level': 1,
    'value': {'gold': 500 }
}

PRO_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'professional pickaxe',
    'prototype_tags': 'mining',
    'key': 'professional pickaxe',
    'desc': 'a professional mining axe',
    'strength': 1,
    'speed': 1,
    'lifespan': 20,
    'max_lifespan': 20,
    'mining_level': 2,
    'value': {'gold': 600 }
}

MASTER_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'master pickaxe',
    'prototype_tags': 'mining',
    'key': 'master pickaxe',
    'desc': 'a master mining axe',
    'strength': 1,
    'speed': 2,
    'lifespan': 20,
    'max_lifespan': 20,
    'mining_level': 5,
    'value': {'gold': 1500 }
}

EXPLOSIVE_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'explosive axe',
    'prototype_tags': 'mining',
    'key': 'explosive axe',
    'desc': 'a power axe equipped with explosives',
    'strength': 3,
    'speed': 2,
    'lifespan': 5,
    'max_lifespan': 15,
    'mining_level': 5,
    'value': {'gold': 2000}
}

JACKHAMMER = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'jackhammer',
    'prototype_tags': 'mining',
    'key': 'jackhammer',
    'desc': 'a pneumatic jackhammer that can rapidly chip away at walls.',
    'strength': 1,
    'speed': 5,
    'lifespan': 20,
    'max_lifespan': 30,
    'mining_level': 5,
    'value': {'gold': 2200}
}

#==[Gear]==========================================================================================#
SPEED_BOOTS = {
    'prototype_key': 'speedBoots',
    'prototype_desc': 'basic speed boots',
    'prototype_tags': 'gear',
    'typeclass': 'typeclasses.gear.SpeedBoots',
    'speed_boost': 0.1,
    'value': {'gold': 8000 }
}

PREMIUM_SPEED_BOOTS = {
    'prototype_parent': 'speedBoots',
    'prototype_key': 'premium speed boots',
    'key': 'premium speed boots',
    'desc': 'these boots allow you to move slightly faster',
     'speed_boost': 0.25,
    'value': {'gold': 10000 }
}

RUNNING_SHOES = {
    'prototype_parent': 'speedBoots',
    'prototype_key': 'running shoes',
    'key': 'running shoes',
    'desc': 'a fancy pair of running shoes',
     'speed_boost': 0.35,
    'value': {'gold': 100000 }
}

#==[Misc]==========================================================================================#

BAIT = {
    'prototype_key': 'bait',
    'prototype_desc': 'Fishing bait',
    'prototype_tags': 'bait',
    'typeclass': 'items.objects.Object',
    'tags': [('bait', 'fishing', None)]
}

FOUL_SMELLING_BAIT = {
    'prototype_parent': 'bait',
    'prototype_key': 'foul-smelling bait',
    'key': 'foul-smelling bait',
    'lure': 1,
    'value': {'trash': 2}
}

