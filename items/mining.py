# ==[Mining Tools]==========================================================================================#
MINING_TOOL = {
    'prototype_key': 'MiningTool',
    'prototype_desc': 'Mining tool',
    'prototype_tags': 'mining',
    'typeclass': 'typeclasses.mining.MiningTool'
}
REPAIR_KIT = {
    'prototype_key': 'MiningRepairKit',
    'prototype_desc': 'mining repair kit',
    'prototype_tags': 'mining',
    'typeclass': 'typeclasses.mining.RepairKit',
    'key': 'repair kit',
    'desc': 'a toolkit to repair mining equipment',
    'strength': 10,
    'value': {'gold': 100}
}
BASIC_AXE = {
    'prototype_parent': 'MiningTool',
    'prototype_key': 'BasicMiningPick',
    'prototype_tags': 'mining',
    'key': 'basic pickaxe',
    'aliases': ['axe'],
    'desc': 'an entry-level mining axe',
    'strength': 1,
    'speed': 1,
    'lifespan': 25,
    'max_lifespan': 25,
    'mining_level': 1,
    'value': {'gold': 200}
}
AMATEUR_AXE = {
    'prototype_parent': 'MiningTool',
    'prototype_key': 'AmateurMiningPick',
    'prototype_tags': 'mining',
    'key': 'amateur pickaxe',
    'aliases': ['axe'],
    'desc': 'A slightly improved mining axe.',
    'strength': 1,
    'speed': 2,
    'lifespan': 25,
    'max_lifespan': 30,
    'mining_level': 2,
    'value': {'gold': 500}
}
PRO_AXE = {
    'prototype_parent': 'MiningTool',
    'prototype_key': 'ProMiningPick',
    'prototype_tags': 'mining',
    'key': 'professional pickaxe',
    'aliases': ['axe'],
    'desc': 'a professional mining axe',
    'strength': 2,
    'speed': 1,
    'lifespan': 25,
    'max_lifespan': 50,
    'mining_level': 4,
    'value': {'gold': 1000}
}
MASTER_AXE = {
    'prototype_parent': 'MiningTool',
    'prototype_key': 'MasterMiningPick',
    'prototype_tags': 'mining',
    'key': 'master pickaxe',
    'desc': 'a master mining axe',
    'strength': 2,
    'speed': 2,
    'lifespan': 30,
    'max_lifespan': 100,
    'mining_level': 5,
    'value': {'gold': 2000}
}
EXPLOSIVE_AXE = {
    'prototype_parent': 'MiningTool',
    'prototype_key': 'ExplosiveMiningPick',
    'prototype_tags': 'mining',
    'key': 'explosive axe',
    'desc': 'a power axe equipped with explosives',
    'strength': 4,
    'speed': 2,
    'lifespan': 5,
    'max_lifespan': 15,
    'mining_level': 5,
    'value': {'gold': 5000}
}
JACKHAMMER = {
    'prototype_parent': 'MiningTool',
    'prototype_key': 'JackhammerMiningPick',
    'prototype_tags': 'mining',
    'key': 'jackhammer',
    'desc': 'a pneumatic jackhammer that can rapidly chip away at walls.',
    'strength': 2,
    'speed': 8,
    'lifespan': 50,
    'max_lifespan': 100,
    'mining_level': 5,
    'value': {'gold': 5000}
}

