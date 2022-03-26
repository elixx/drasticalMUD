#from evennia.web.website import views as website_views
from django.views.generic import TemplateView, ListView, DetailView
from world.utils import area_count
from string import capwords

#class areaView(website_views.EvenniaIndexView):
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
    #template_name = "template_overrides/website/areas.html"
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
        areas.append( { 'area': capwords(area[0]), 'rooms': area[1] } )

    pagevars = {
        "areas": areas,
        "number_of_areas": len(ac),
    }
    return pagevars
