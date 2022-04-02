# from evennia.web.website import views as website_views
from django.views.generic import TemplateView, ListView, DetailView

import evennia
from world.utils import area_count
from string import capwords
from evennia.utils.logger import log_err


class areaView(TemplateView):
    """
    This is a basic example of a Django class-based view, which are functionally
    very similar to Evennia Commands but differ in structure. Commands are used
    to interface with users using a terminal client. Views are used to interface
    with users using a web browser.

    To use a class-based view, you need to have written a template in HTML, and
    then you write a view like this to tell Django what values to display on it.

    While there are simpler ways of writing views using plain functions (and
    Evennia currently contains a few examples of them), just like Commands,
    writing views as classes provides you with more flexibility-- you can extend
    classes and change things to suit your needs rather than having to copy and
    paste entire code blocks over and over. Django also comes with many default
    views for displaying things, all of them implemented as classes.

    This particular example displays the index page.

    """

    # Tell the view what HTML template to use for the page
    # template_name = "template_overrides/website/areas.html"
    template_name = "website/areas.html"

    # This method tells the view what data should be displayed on the template.
    def get_context_data(self, **kwargs):
        """
        This is a common Django method. Think of this as the website
        equivalent of the Evennia Command.func() method.

        If you just want to display a static page with no customization, you
        don't need to define this method-- just create a view, define
        template_name and you're done.

        The only catch here is that if you extend or overwrite this method,
        you'll always want to make sure you call the parent method to get a
        context object. It's just a dict, but it comes prepopulated with all
        sorts of background data intended for display on the page.

        You can do whatever you want to it, but it must be returned at the end
        of this method.

        Keyword Args:
            any (any): Passed through.

        Returns:
            context (dict): Dictionary of data you want to display on the page.

        """
        # Always call the base implementation first to get a context object
        context = super(TemplateView, self).get_context_data(**kwargs)

        # Add game statistics and other pagevars
        context.update(_area_stats())

        return context


def _area_stats():
    ac = area_count()
    ac = sorted(ac.items(), key=lambda x: x[1], reverse=True)

    areas = []

    for area in ac:
        if area[0] in areainfo.keys():
            areas.append({'area': '<a href="/area/' + area[0] + '" class="highlight-link text-action"><span class="text-info">' + capwords(area[0]) + '</span></a>', 'rooms': area[1]})
        else:
            areas.append({'area': capwords(area[0]), 'rooms': area[1]})

    pagevars = {
        "areas": areas,
        "number_of_areas": len(ac),
    }
    return pagevars


class toplistView(TemplateView):
    template_name = "website/toplist.html"

    # This method tells the view what data should be displayed on the template.
    def get_context_data(self, **kwargs):
        # Always call the base implementation first to get a context object
        context = super(TemplateView, self).get_context_data(**kwargs)

        # Add game statistics and other pagevars
        context.update(_toplist_stats())

        return context


def _toplist_stats():
    from typeclasses.rooms import topClaimed
    from world.utils import topGold
    claimed = topClaimed()
    gold = topGold()
    stats = {}
    for (player, count) in claimed:
        if player in stats.keys():
            stats[player]['claimed'] = count
        else:
            stats[player] = {'claimed': count, 'gold': '-'}
    for (player, g) in gold:
        if player in stats:
            stats[player]['gold'] = g
        else:
            stats[player] = {'name': player, 'claimed': '-', 'gold': g}

    output = []
    for player in stats.keys():
        pid = evennia.search_object(player).first().id
        output.append(
            {'name': player, 'owned': stats[player]['claimed'], 'gold': int(stats[player]['gold']), 'id': pid})

    pagevars = {"stats": output}
    return pagevars


class playerView(TemplateView):
    template_name = "website/player.html"

    def get_context_data(self, **kwargs):
        # Always call the base implementation first to get a context object
        context = super(TemplateView, self).get_context_data(**kwargs)
        # Add game statistics and other pagevars
        context.update(_player_stats(**kwargs))
        return context


def _player_stats(**kwargs):
    from evennia.utils.search import search_object as object_search, search_tag_object
    from django.http import Http404
    # from django.shortcuts import render
    from evennia.utils.utils import inherits_from
    from world.utils import claimed_in_area, total_rooms_in_area, visited_in_area
    from django.conf import settings

    object_id = kwargs['object_id']

    if object_id is not None:
        object_id = "#" + str(object_id)
        try:
            character = object_search(object_id)[0]
        except IndexError:
            raise Http404("I couldn't find a character with that ID.")
        if not inherits_from(character, settings.BASE_CHARACTER_TYPECLASS):
            raise Http404("I couldn't find a character with that ID. "
                          "Found something else instead.")
        explored = []
        visited = character.db.stats['visited']
        for area in visited.keys():
            total = total_rooms_in_area(area)
            seen = len(visited_in_area(area, character.id))
            claimed = claimed_in_area(area, character.id)
            owned = claimed.count()
            explored.append({'name': area, 'total': total, 'seen': seen, 'owned': owned})
        explored = sorted(explored, key=lambda x: x['seen'], reverse=True)
    return {'character': character, 'gold': round(character.db.stats['gold'],2), 'explored': explored}


class areaInfoView(TemplateView):
    template_name = "website/areainfo.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context.update(_area_info(**kwargs))
        return context


def _area_info(**kwargs):
    area = kwargs['area_name']
    if area not in areainfo.keys():
        pagevars = {'area': area, 'areainfo': 'no info for %s' % area}
    else:
        info = areainfo[area]
        while "\n\n" in info:
            info = info.replace("\n\n", "\n")
        # info = info.replace("\n", "</PRE>\n<PRE>")
        info = "\n<PRE>" + info + "</PRE>\n"
        pagevars = {'area': area, 'areainfo': info}
    return pagevars


areainfo = {
    'the abyss': "Converted to standard Envy 1.x by Jason Huang (god@sure.net)\n"+
                 "Further conversion to Rom 2.4 by Jaceks and Chicken's Den Staff",
    'animaland': "Many years ago, a cabal of powerful wizards known as the High Magi\n"+
                 "conducted a series of experiments on laboratory test animals, in an\n"+
                 "attempt to grant these simple beasts a level of sentience equivalent to or\n"+
                 "superior to their own. For decades their efforts, and the efforts of their\n"+
                 "descendants, met with dismal failure.\n"+
                 "     Then one day, a brilliant younge mage known as Ceraphem stumbled \n"+
                 "across a mystical tome in the foothills of G'hal that contained the\n"+
                 "total knowledge of the ancient Animage Gor-Kheebler. Elated with his find,\n"+
                 "Cerapham rushed home to the stony fortress of Teut-Rhogar, that he and his\n"+
                 "associates shared with some Dwarven priests, and set to work on their\nexperiments, this time following instructions given in Gor-Kheebler's tome.\n     Soon afterward, strange beasts began to emerge from Teut-Rhogar's\nforbidding heights, animals that could walk and talk and interact with\ntheir creators on a level of sophistication that would have impressed even\nGor-Kheebler himself. The cabal were amazed, and continued to pour out\ntheir creations, animals of all types granted remarkable acuity and skill.\n     But the humans that lived at the foot of the mountains that housed\nthe fortress grew restless, then angry towards the mages and their\ncreations. Calling it heresy, they continued to grow agitated until one\nday they sent an emissary to the Dwarves hosting the cabal that unless\nthe experiments ceased and the animals were destroyed, the nearby human\ntowns would cease to buy ore from the dwarves or provide them with the\nfood that they could not provide for themselves. The Dwarves of course\nrefused, slaying the emissary, but the cabal were concerned for the safety\nof their allies and began to plan how to spirit the animals away.\n     It was Ceraphem who once again brought salvation to his friends. He\nknew of a knigdom many miles away that had once flourished with Elves and\nKender, but which was now uninhabited due to the decline in populations\nof these two races, and he suggested that the Animals and Dwarves be given \nhaven there. All instantly agreed, and they set out.\n     Upon reaching the kingdom, the animals set up an administrative and\npolitical system, and soon were coping quite well without their creators'\nguiding hand. However, Ceraphem worried for their safety, and thus cast\nan enchantment that none may ever leave the bounds of Animaland that was\nan animal. Furhtermore, he called upon a favour owed him by the Knights\nof the Order of the Liver, and they pledged to establish a guard post\nat the entrance to Animaland, staffing it at all times with their best\nknights.\n     And so it has remained over the intervening years till today. The\nOrder of the Liver grew decadent however, and these days only one knight\nremains in the tower near the entrance, and even then only because he\nfelt obliged to live up to the oath made by his more honorable ancestors.\nWhen he dies, there will be no-one to protect Animaland, but the Animals\nhave gained in power, and actually have a competent defense force, as well\nas a powerful wizard, a former apprentice of Ceraphem named Wizard Owl.\nSo feel free to enter Animaland, but respect the inhabitants, especially\nthe inhabitants of Animaltown, who rank amongst the most powerful creatures\nin all the land of Anon.\n",
    'chessboard of midgaard': "Converted to standard Envy 1.x by Jason Huang (god@sure.net)\nFurther conversion to Rom 2.4 by Jaceks and Chicken's Den Staff",
    'dark continent': 'Created by Mort for 5-35 level players. \nConverted to ROM 2.4 format by Gapcio.\nEnhanced and balanced by jaceks.\nChecked and beta tested by Quartz.\n',
    'firetop mountain': 'This area was created by Yaegar in November 1995 with the use of a DOS\nText Editor and MakeZonesFast from Slash. It is based on the Fighting\nFantasy Gamebook "The Warlock of Firetop Mountain", by Steve Jackson and\nIan Livingstone, published by Puffin Books.\n\n     Thanks go to Steve and Ian, Rainman, Lenny, Slash, Julilla,Argh, Fle\nMarc and Sol, and the rest of the gang at AM, for aid, assistance, support\nand friendship. Permission is given for any Implementor to use this area\nin their Mud, with the exception of Barren Realms (barren.liii.com 8000).\n',
    'fun house': "Welcome to the magical world of the circus! In recent years, we have been\nworking on some major renevations to try and make it more enjoyable for you!\nThe Fun House is one of many new features you can expect in the near future.\n\nFun House area has been created by Gorzak for 12-17 level players,\nconverted to ROM 2.4 format by jaceks, july'96.\n",
    'ghost town': "This is purely a simple hack-n-slash area with the interesting added feature\nthat you can't recall... You have to fight your way through the many powerful\nhigh level undead that populate this place. To a good mudder its heaven. To\nsomeone who flees when fighting the children in Mud School, its probably gonna\nbe considered impossible. Either way, have fun.\n\n- Yaegar Dec 1995\n\n",
    'mirkwood': 'Written by Yaegar using MZF and a DOS text Editor in December 1995. Based\nloosely on the forest mentioned in the works of Tolkien of the same name.\n\nThanks to J.R.R. Tolkien and the gang at AM.\n',
    'newbie2.are': "Converted to standard Envy 1.x by Jason Huang (god@sure.net)\nFurther conversion to Rom 2.4 by Jaceks and Chicken's Den Staff",
    'pawmist': 'Area written by Twilight (twlthunter@faynet.com) for telnet://blades.wolfpaw.net:1234.  Area is for levels 15-50.  Special thanks to Estellios for providing ideas and insight into the area.\n',
    'the shielding': 'The  Shielding is the holy ground and religious cathedral of the order\n\nof the Shielding. There are several things of interest here. First the entire\n\narea is  no recall, no teleport, no sumon- it is holy ground and evil forces\n\ntrying to enter are barred from entry that way. Next the shopkeep mobs lack\n\nnames so that they can not be summoned, charmed, or teleported to.  Of paticular\n\ninterest are the stained glass windows. Lok comissioned an artist-magician to\n\ndepict several areas of paticular evil and create one way gateways to them from\n\nthe Shielding. This is so the  Knights of the Shielding can rallly and go forth to \n\nbattle these sundry forces. The main item of interest for this area is the holy\n\nhelm, which is type key and unlocks the doors of the Cathedral. When worn it\n\nhelps members detect evil and protects them from it. Also of interest are the\n\nholy orbs, which reveal those unseen forces which seek to harm the Shielding.\n\n',
    'water': "This area is a cheap no brainer which I whipped up in less than 15 minutes.\nIf you want newbies to level really fast, then use this, but don't complain\nto me when everyone is heroed. :p",
    'midgaard': "Midgaard is a capitol city in the middle of the continent, towards the southern coast.\n"+
                " Located on the Midgaard river, this popular city is home to adventurers of all sorts.",
    'underdark': "Just as its name implies, this area is found in underground areas not directly\n"+
                 " accessible by normal means. A race of gnomes who are busy brewing up their own\n"+
                 "potions and forging their own magical equipment is found here.\n",
    'new thalos': '  Long ago, after the city of Thalos was completely destroyed and its survivors all fled\n'+
                  "into the surrounding hills, they banded together in camps to decide what to do.\n"+
                  "  Ultimately the decision was made to rebuild the city in a location some distance\n"+
                  ' away from the smoldering ruins of Thalos, where it was safer.  Naming the new city\n'+
                  '"New" Thalos, after many years it is once again prosperous, with many businesses\n'+
                  'and a large population.\n',
    'high tower': '   The High Tower of Sorcery is where all the young mages who want to study\n'+
                  'under the most learned wizards go to learn.  It\'s been said that the tower is\n'+
                  'under the control of forces more evil than you can imagine.  The grounds are\n'+
                  'covered in an almost suffocating mist and travelers have tried to find their\n'+
                  'way to it, but never returned.\n',
    'haon dor': '   Haon-Dor is a forest of many secrets.  Its innocent, furry creatures belie\n'+
                'the fact that somewhere, someone is watching you...  perhaps even hunting you.\n'+
                '  Your only hope is that, if he does find you, you die quickly and with dignity.\n',
    'elemental canyon': '   Exploring the Elemental Canyon, one will come across a melting pot of\n'+
                        'all the elements of life.  There are five main areas to be searched - fire,\n'+
                        'water, air, earth, and electricity, all containing different creatures and\n'+
                        'elementals, and each one looked over by an elemental ruler.  These rulers\n'+
                        'sometimes horde valuable treasures, but are formidable opponents, and can\n'+
                        'not be easily defeated by an unprepared fighter.\n',
    'sesame street': '   Sesame Street is home to all of your favorite childhood characters - Big Bird,\n'+
                     'Oscar the Grouch, the cute and cuddly little Elmo, and of course, your favorite\n'+
                     'frog (and mine), Kermie!  Just down the road is the Muppet Theater with guest\n'+
                     'stars such as Mark Hamill and Phyllis Diller, and of course, 123 Sesame Street\n'+
                     'and the Count\'s Castle.\nA statue has been erected in memory of John Denver, talented\n'+
                     'performer and long-time guest star of Sesame Streets Muppet Theatre, in the\n'+
                     'dressing room with his name on it.\n',


}
