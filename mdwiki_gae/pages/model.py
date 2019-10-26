from dataclasses import dataclass


@dataclass
class Page:
    name: str
    contents: str

    title: str = "Untitled"
