from ansimarkup import AnsiMarkup, parse

user_tags = {
    "keyword": parse("<bold>"),
    "aggresive": "\x1B[38;5;196m",
    "debuff": "\x1B[38;5;148m",
    "buff": "\x1B[38;5;85m",
    "attack": "\x1B[38;5;196m",
    "skill": "\x1B[38;5;45m",
    "power": "\x1B[38;5;51m",
    "status": "\x1B[38;5;35m",
    "curse": "\x1B[38;5;127m",
    "basic": "\x1B[38;5;245m",
    "common": "\x1B[38;5;245m",
    "uncommon": "\x1B[38;5;45m",
    "rare": "\x1B[38;5;214m",
    "special": "\x1B[38;5;27m",
    "yellow": "\x1B[38;5;220m",
    "dark-blue": "\x1B[38;5;20m",
    "dark-green": "\x1B[38;5;28m",
    "true-blue": "\x1B[38;5;21m",
    "light-black": "\x1B[38;5;242m",
    "light-red": "\x1B[38;5;1m",
    'watcher-purple': "\x1B[38;5;93m",
    "boss": "\x1B[38;5;124m",
    "event": "\x1B[38;2;254;49;236m",
    "starter": "\x1B[38;5;247m",
    "orange": parse("<fg #d78700>")
}
am = AnsiMarkup(tags=user_tags, strict=True)

ansiprint = am.ansiprint
strip = am.strip
parse = am.parse
