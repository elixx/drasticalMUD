
"""

Lockfuncs

Lock functions are functions available when defining lock strings,
which in turn limits access to various game systems.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See the
Evennia documentation for more info on locks.

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled with *args, **kwargs. The lock function
should handle all eventual tracebacks by logging the error and
returning False.

Lock functions in this module extend (and will overload same-named)
lock functions from evennia.locks.lockfuncs.

"""

def keycheck(accessing_obj, accessed_obj, *args, **kwargs):
    if accessed_obj.db.unlocked_by != None:
        for item in accessing_obj.contents:
            if item.db.unlocks != None:
                for unlocks in item.db.unlocks:
                    if unlocks == accessed_obj.db.unlocked_by:
                        accessing_obj.msg("You unlock the %s with %s" % (accessed_obj.name, item.name))
                        accessing_obj.location.msg_contents("%s unlocks %s with %s." % (accessing_obj.name,
                                                                                        accessed_obj.name, item.name),
                                                            exclude=accessing_obj)
                        return True
        accessing_obj.location.msg_contents("%s tried to unlock %s, but they don't have the key." % (accessing_obj.name, accessed_obj.name),
                                            exclue=accessing_obj)
        accessing_obj.msg("You try to enter %s, but don't have the key." % accessed_obj.name)
        return False
    else:
        accessing_obj.location.msg_contents(
            "%s unlocks the %s." % (accessing_obj.name, accessed_obj.name))
        return True

# def myfalse(accessing_obj, accessed_obj, *args, **kwargs):
#    """
#    called in lockstring with myfalse().
#    A simple logger that always returns false. Prints to stdout
#    for simplicity, should use utils.logger for real operation.
#    """
#    print "%s tried to access %s. Access denied." % (accessing_obj, accessed_obj)
#    return False
