# ==[Clothing]==========================================================================================#
# ==[Shirts]==========================================================================================#
BASE_SHIRT = {
    'prototype_key': 'BaseShirt',
    'prototype_tags': ['clothing', 'top'],
    'typeclass': 'core.clothing.Clothing',
    'clothing_type': 'top',
}

HAWAIIAN_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'HawaiianShirt',
    'prototype_tags': ['clothing', 'top'],
    'key': 'hawaiian shirt',
    'desc': 'a loud hawaiian shirt',
    'worn': 'looking like a tourist',
    'value': {'gold': 50}
}
BUTTON_UP_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'ButtonUpShirt',
    'prototype_tags': ['clothing', 'top'],
    'key': 'button-up shirt',
    'desc': 'a plain, white button-up shirt',
    'worn': 'looking clean and proper',
    'value': {'gold': 65}
}
WHITE_TEE = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'XXLTeeShirt',
    'prototype_tags': ['clothing', 'top'],
    'key': 'XXL white tee',
    'desc': 'an incredibly large, white T-shirt',
    'worn': 'hangs down',
    'value': {'gold': 10}
}
LEATHER_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'LeatherShirt',
    'prototype_tags': ['clothing', 'top'],
    'key': 'leather shirt',
    'desc': 'It looks like something one of the Village people would wear.',
    'worn': 'shows off Sharpie chest-hair',
    'value': {'gold': 20}
}
SHINY_KNIT_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'ShinyKnitShirt',
    'prototype_tags': ['clothing', 'top'],
    'key': 'shiny, knit shirt',
    'desc': "It's made out of some kind of shimmery fabric.",
    'worn': "that catches your attention",
    'value': {'gold': 100}
}
BLUE_SHIRT = {
    'prototype_parent': 'BaseShirt',
    'prototype_key': 'PlainBlueShirt',
    'prototype_tags': ['clothing', 'top'],
    'key': 'plain blue shirt',
    'desc': "It's blue. It's a shirt.",
    'worn': "looking nondescript",
    'value': {'gold': 15}
}

# ==[Bottoms]==========================================================================================#
BASE_PANTS = {
    'prototype_key': 'BasePants',
    'prototype_tags': ['clothing', 'bottom'],
    'typeclass': 'core.clothing.Clothing',
    'clothing_type': 'bottom',
}
PANTS_PANTS = {
    'prototype_parent': 'BasePants',
    'prototype_key': 'GenericPants',
    'prototype_tags': ['clothing', 'bottom'],
    'key': 'a pair of pants',
    'desc': 'They\'re pants.What more could you ask for?',
    'value': {'gold': 15}
}
BLACK_SWEATS = {
    'prototype_parent': 'BasePants',
    'prototype_key': 'BlackSweatPants',
    'prototype_tags': ['clothing', 'bottom'],
    'key': 'a pair of black sweats',
    'desc': 'Plain, black sweatpants with an elastic waistband and drawstring.',
    'value': {'gold': 35}
}
FADED_JEANS = {
    'prototype_parent': 'BasePants',
    'prototype_key': 'FadedJeansPants',
    'prototype_tags': ['clothing', 'bottom'],
    'key': 'a pair of faded jeans',
    'desc': 'These jeans have been bean the hell up. THey are very faded and worn.',
    'value': {'gold': 50}
}
CAMO_PANTS = {
    'prototype_parent': 'BasePants',
    'prototype_key': 'CamoPants',
    'prototype_tags': ['clothing', 'bottom'],
    'key': 'a pair of camo pants',
    'desc': 'Standard-issue military wear.',
    'value': {'gold': 200}
}
COTTON_SHORTS = {
    'prototype_parent': 'BasePants',
    'prototype_key': 'CottonShortsPants',
    'prototype_tags': ['clothing', 'bottom'],
    'key': 'a pair of cotton shorts',
    'desc': 'A plain pair of gym shorts.',
    'value': {'gold': 15}
}
BLACK_FATIGUES = {
    'prototype_parent': 'BasePants',
    'prototype_key': 'BlackFatiguesPants',
    'prototype_tags': ['clothing', 'bottom'],
    'key': 'a pair of black fatigues',
    'desc': 'Military-style tactical wear, but less obvious.',
    'value': {'gold': 300}
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
    'prototype_tags': ['clothing', 'hat'],
    'prototype_key': 'VikingHelmetHat',
    'key': 'a viking helmet',
    'desc': 'A horned, metal viking helmet',
    'worn': 'just like Flava Flav',
    'value': {'gold': 150}
}
WOOL_BEANIE = {
    'prototype_parent': 'BaseHat',
    'prototype_tags': ['clothing', 'hat'],
    'prototype_key': 'WoolenBeanieHat',
    'key': 'woolen beanie',
    'desc': 'A knit ski cap',
    'value': {'gold': 25}
}
BASEBALL_CAP = {
    'prototype_parent': 'BaseHat',
    'prototype_tags': ['clothing', 'hat'],
    'prototype_key': 'BaseballCapHat',
    'key': 'baseball cap',
    'desc': 'A plain, brimmed baseball cap',
    'worn': 'pulled down low',
    'value': {'gold': 35}
}
PITH_HELMET = {
    'prototype_parent': 'BaseHat',
    'prototype_tags': ['clothing', 'hat'],
    'prototype_key': 'PithHelmetHat',
    'key': 'a pith helmet',
    'desc': 'You\'ll look just like an African explorer in this!',
    'worn': 'like an African explorer',
    'value': {'gold': 40}
}
FEZ = {
    'prototype_parent': 'BaseHat',
    'prototype_tags': ['clothing', 'hat'],
    'prototype_key': 'FezHat',
    'key': 'fez',
    'desc': 'A red velvet fez, complete with tassle.',
    'worn': 'with a fuzzy tassle',
    'value': {'gold': 30}
}
GRADUATION_CAP = {
    'prototype_parent': 'BaseHat',
    'prototype_tags': ['clothing', 'hat'],
    'prototype_key': 'GraduationCapHat',
    'key': 'a graduation cap',
    'desc': 'You feel smart just looking at this!',
    'worn': 'that makes them look smart',
    'value': {'gold': 35}
}

# ==[Misc]==========================================================================================#
HAZMAT_SUIT = {
    'prototype_key': 'HazmatSuit',
    'prototype_tags': ['clothing', 'fullbody'],
    'typeclass': 'core.clothing.Clothing',
    'key': '|yyellow|n hazmat suit',
    'desc': "A |yyellow|x h|ya|xz|ym|xa|yt|n suit|n, such as to protect from hazardous chemicals and radiation.",
    "worn": "to protect from |yhazardous|g chemicals|n",
    'clothing_type': 'fullbody',
    'value': {'gold': 15000}
}
