from ansimarkup import AnsiMarkup, parse

user_tags = {
    "keyword": parse("<bold>"),
    "debuff": "\033[38;5;166m",
    "buff": "\033[38;5;85m",
    "attack": "\033[38;5;196m",
    "skill": "\033[38;5;45m",
    "power": "\033[38;5;165m",
    "status": "\033[38;5;35m",
    "curse": "\033[38;5;127m",
    "uncommon": "\033[38;5;27m",
    "rare": "\033[38;5;208m"
}
am = AnsiMarkup(tags=user_tags, strict=True)

ansiprint = am.ansiprint
