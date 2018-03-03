from .fortnite import Fortnite


def setup(bot):
    bot.add_cog(Fortnite(bot))
