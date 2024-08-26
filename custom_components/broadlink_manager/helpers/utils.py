def format_name(name: str) -> str:
    """Transform a name by replacing underscores with spaces and capitalizing words, only if they have no existing capitalization."""

    def should_capitalize(word):
        return not any(char.isupper() for char in word)

    return " ".join(
        word if not should_capitalize(word) else word.capitalize()
        for word in name.split("_")
    )


def normalize_mac(mac: str) -> str:
    """Normalize a MAC address by removing colons and converting to lowercase."""
    return mac.replace(":", "").lower()
