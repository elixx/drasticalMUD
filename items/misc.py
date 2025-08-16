# ==[Gear]==========================================================================================#
SPEED_BOOTS = {
    'prototype_key': 'SpeedBoots',
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
    'prototype_parent': 'SpeedBoots',
    'prototype_key': 'PremiumSpeedBoots',
    'prototype_tags': ['clothing', 'boots', 'buff'],
    'key': 'premium speed boots',
    'desc': 'these boots allow you to move slightly faster',
    'speed_boost': 0.25,
    'value': {'gold': 15000}
}
RUNNING_SHOES = {
    'prototype_parent': 'SpeedBoots',
    'prototype_key': 'RunningShoesSpeedBoots',
    'prototype_tags': ['clothing', 'boots', 'buff'],
    'key': 'running shoes',
    'desc': 'a fancy pair of running shoes',
    'speed_boost': 0.35,
    'value': {'gold': 100000}
}
