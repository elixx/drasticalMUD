# from typeclasses.rooms import ImportedRoom
# [obj.at_object_creation() for obj in ImportedRoom.objects.all()]

def fixtags():
    areas = { "pawmist": "twilight city of pawmist",
              "erealms": "elven realms",
              "shadval150": "kandahar shadow valley",
              "sdearth": "south dearthwood",
              "edearth": "east dearthwood",
             "avalonch": "avalon",
             "talonvle": "gilda and the dragon",
             "takshrin": "shrine of tahkien",
            "dawn": "city of dawn",
             "tisland": "treasure island",
            "amazon":"the amazon jungle",
            "partbody": "body parts castle",
            "north": "northern road",
            'river': 'durgas river',
            'island': 'island of illusion',
            'east': 'eastern road',
            'demise': 'death room',
            'path': 'the hidden path',
            'gstrong': 'goblin stronghold',
            'plains': 'plains of the north',
            'pyramid': 'the great pyramid',
              'weaverei': 'the dreamweaver\'s path',
            'marsh': 'generic old marsh',
            'tree': 'yggdrasil',
    'zoology': 'mudschool fieldtrip',
    'dock': 'calinth docks',
    'water': 'blizzard water nymphs',
    'chessbrd': 'chessboard'}



    for area in areas.keys():
        for a in ['area','room']:
            rename_tag(area, a, areas[area], a)