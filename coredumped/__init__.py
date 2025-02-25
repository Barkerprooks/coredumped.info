from markdown import markdownFromFile
from random import choice

import os.path
import json


async def get_random_banner() -> str:
    """
    loads a JSON file, which is just a list of strings, and randomly selects a string
    """

    with open("static/banners.json") as file:
        return choice(json.load(file))
    

async def generate_markdown(path: str) -> str:
    """
    creates a markdown file with syntax highlighting supported
    """
    
    if not os.path.isfile(path):
        return "<center>error generating markdown :(</centrer>"
    
    return markdownFromFile(
        path, 
        extensions=["codehilite"],
        extension_configs={ "codehilite": { "linenums": True } }
    )