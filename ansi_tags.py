from ansimarkup import AnsiMarkup, parse

user_tags = {
    "keyword": parse("<bold>"),
    "aggresive": "\033[38;5;196m",
    "debuff": "\033[38;5;148m",
    "buff": "\033[38;5;85m",
    "attack": "\033[38;5;196m",
    "skill": "\033[38;5;45m",
    "power": "\033[38;5;51m",
    "status": "\033[38;5;35m",
    "curse": "\033[38;5;127m",
    "status": "\033[38;5;35m",
    "curse": "\033[38;5;127m",
    "basic": "\033[38;5;245m",
    "common": "\033[38;5;245m",
    "uncommon": "\033[38;5;45m",
    "rare": "\033[38;5;214m",
    "special": "\033[38;5;27m",
    "yellow": "\033[38;5;220m",
    "dark-blue": "\033[38;5;20m",
    "dark-green": "\033[38;5;28m",
    "true-blue": "\033[38;5;21m",
    "light-black": "\033[38;5;242m",
    "light-red": "\033[38;5;1m",
    'watcher-purple': "\033[38;5;93m",
    "boss": "\033[38;5;124m",
    "event": "\033[38;2;254;49;236m",
    "starter": "\033[38;5;247m",
}
am = AnsiMarkup(tags=user_tags, strict=True)

ansiprint = am.ansiprint
