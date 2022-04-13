from random import choice

# ==[Growables]==========================================================================================#
GROWABLE = {
    'prototype_key': 'Spore',
    'prototype_desc': 'fungus spore',
    'prototype_tags': 'growable',
    'typeclass': 'typeclasses.growable.GrowableObject'
}

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

# ==[Mining Tools]==========================================================================================#

MINING_TOOL = {
    'prototype_key': 'miningTool',
    'prototype_desc': 'Mining tool',
    'prototype_tags': 'mining',
    'typeclass': 'typeclasses.mining.MiningTool'
}

BASIC_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'basic pickaxe',
    'key': 'basic pickaxe',
    'desc': 'an entry-level mining axe',
    'strength': 1,
    'speed': 1,
    'lifespan': 10,
    'max_lifespan': 10,
    'mining_level': 1,
    'value': {'gold': 500}
}

PRO_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'professional pickaxe',
    'key': 'professional pickaxe',
    'desc': 'a professional mining axe',
    'strength': 1,
    'speed': 1,
    'lifespan': 20,
    'max_lifespan': 20,
    'mining_level': 2,
    'value': {'gold': 600}
}

MASTER_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'master pickaxe',
    'key': 'master pickaxe',
    'desc': 'a master mining axe',
    'strength': 1,
    'speed': 2,
    'lifespan': 20,
    'max_lifespan': 20,
    'mining_level': 5,
    'value': {'gold': 1500}
}

EXPLOSIVE_AXE = {
    'prototype_parent': 'miningTool',
    'prototype_key': 'explosive axe',
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
    'key': 'jackhammer',
    'desc': 'a pneumatic jackhammer that can rapidly chip away at walls.',
    'strength': 1,
    'speed': 8,
    'lifespan': 20,
    'max_lifespan': 30,
    'mining_level': 5,
    'value': {'gold': 2200}
}

# ==[Gear]==========================================================================================#
SPEED_BOOTS = {
    'prototype_key': 'speedBoots',
    'prototype_tags': ['clothing', 'boots', 'buff'],
    'prototype_desc': 'basic speed boots',
    'key': 'basic speed boots',
    'desc': 'a basic pair of speed boots',
    'prototype_tags': 'gear',
    'typeclass': 'typeclasses.gear.SpeedGear',
    'speed_boost': 0.1,
    'value': {'gold': 8000}
}

PREMIUM_SPEED_BOOTS = {
    'prototype_parent': 'speedBoots',
    'prototype_key': 'premium speed boots',
    'key': 'premium speed boots',
    'desc': 'these boots allow you to move slightly faster',
    'speed_boost': 0.25,
    'value': {'gold': 10000}
}

RUNNING_SHOES = {
    'prototype_parent': 'speedBoots',
    'prototype_key': 'running shoes',
    'key': 'running shoes',
    'desc': 'a fancy pair of running shoes',
    'speed_boost': 0.35,
    'value': {'gold': 100000}
}

# ==[Clothing]==========================================================================================#
# ==[Shirts]==========================================================================================#
BASE_SHIRT = {
    'prototype_key': 'BaseShirt',
    'prototype_tags': ['clothing', 'shirt'],
    'typeclass': 'core.clothing.Clothing',
    'clothing_type': 'top',
}
HAWAIIAN_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'hawaiian shirt',
    'key': 'hawaiian shirt',
    'desc': 'a loud hawaiian shirt',
    'worn': 'looking like a tourist',
    'value': {'gold': 50}
}
BUTTON_UP_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'button-up shirt',
    'key': 'button-up shirt',
    'desc': 'a plain, white button-up shirt',
    'worn': 'looking clean and proper',
    'value': {'gold': 65}
}
WHITE_TEE = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'XXL white tee',
    'key': 'XXL white tee',
    'desc': 'an incredibly large, white T-shirt',
    'worn': 'hangs down',
    'value': {'gold': 10}
}
LEATHER_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'leather shirt',
    'key': 'leather shirt',
    'desc': 'It looks like something one of the Village people would wear.',
    'worn': 'shows off Sharpie chest-hair',
    'value': {'gold': 20}
}
SHINY_KNIT_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'shiny, knit shirt',
    'key': 'shiny, knit shirt',
    'desc': "It's made out of some kind of shimmery fabric.",
    'worn': "that catches your attention",
    'value': {'gold': 100}
}
BLUE_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'plain blue shirt',
    'key': 'plain blue shirt',
    'desc': "It's blue. It's a shirt.",
    'worn': "looking nondescript",
    'value': {'gold': 15}
}
# ==[Hats]==========================================================================================#
BASE_HAT = {
    'prototype_key': 'BaseHat',
    'prototype_tags': ['clothing', 'hat'],
    'typeclass': 'core.clothing.Clothing',
    'clothing_type': 'hat',
}
VIKING_HELM = {
    'prototype_parent': 'BaseHat',
    'prototype_key': 'a viking helmet',
    'key': 'a viking helmet',
    'desc': 'A horned, metal viking helmet',
    'worn': 'just like Flava Flav',
    'value': {'gold': 150}
}
WOOL_BEANIE = {
    'prototype_parent': 'BaseHat',
    'prototype_key': 'a woolen beanie',
    'key': 'a woolen beanie',
    'desc': 'A knit ski cap',
    'value': {'gold': 25}
}
BASEBALL_CAP = {
    'prototype_parent': 'BaseHat',
    'prototype_key': 'a baseball cap',
    'key': 'a baseball cap',
    'desc': 'A plain, brimmed baseball cap',
    'worn': 'pulled down low',
    'value': {'gold': 35}
}
PITH_HELMET = {
    'prototype_parent': 'BaseHat',
    'prototype_key': 'a pith helmet',
    'key': 'a pith helmet',
    'desc': 'You\'ll look just like an African explorer in this!',
    'worn': 'like an African explorer',
    'value': {'gold': 40}
}
FEZ = {
    'prototype_parent': 'BaseHat',
    'prototype_key': 'a fez',
    'key': 'a fez',
    'desc': 'A red velvet fez, complete with tassle.',
    'worn': 'with a fuzzy tassle',
    'value': {'gold': 30}
}
GRADUATION_CAP = {
    'prototype_parent': 'BaseHat',
    'prototype_key': 'a graduation cap',
    'key': 'a graduation cap',
    'desc': 'You feel smart just looking at this!',
    'worn': 'that makes them look smart',
    'value': {'gold': 35}
}
# ==[Misc]==========================================================================================#
#
# BAIT = {
#     'prototype_key': 'bait',
#     'prototype_desc': 'Fishing bait',
#     'prototype_tags': 'bait',
#     'typeclass': 'items.objects.Object',
#     'tags': [('bait', 'fishing', None)]
# }
#
# FOUL_SMELLING_BAIT = {
#     'prototype_parent': 'bait',
#     'prototype_key': 'foul-smelling bait',
#     'key': 'foul-smelling bait',
#     'lure': 1,
#     'value': {'trash': 2}
# }
