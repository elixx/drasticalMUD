from evennia.commands.default.muxcommand import MuxCommand as DefaultMuxCommand
from world.utils import genPrompt

class MuxCommand(DefaultMuxCommand):
    def parse(self):
        """Implement an additional parsing of 'to'"""
        super().parse()
        if " to " in self.args:
            self.lhs, self.rhs = self.args.split(" to ", 1)

    def at_post_cmd(self):
        """
        This hook is called after the command has finished executing
        (after self.func()).
        """
        super().at_post_cmd()
        self.caller.msg(prompt=genPrompt(self))