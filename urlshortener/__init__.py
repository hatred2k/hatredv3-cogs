from .urlshortener import Urlshortener


def setup(bot):
    bot.add_cog(Urlshortener(bot))
