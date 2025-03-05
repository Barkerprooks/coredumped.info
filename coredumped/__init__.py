from random import choice

async def get_banner() -> str:
    return choice([
        "Hello world!",
        "Howdy there partner!",
        "Come here often?",
        "There's not much to see. Thanks for taking a look anyway!",
        "Well... look who we've got right here!",
        "100% LMM Free!",
        "Gone hackin'",
        "Gone fishin'",
        "Trans rights are human rights!",
        "I didn't even have to use my AK...",
        "You (client) request, I (server) respond. We are not the same.",
        "Hack the planet!",
        "Since 1997",
        "Hell yeah dude.",
        "I just need a cool jacket...",
        "In my cube era...",
        "Cubing it up!",
        "Free Palestine!",
        "Where did you come from?",
    ])