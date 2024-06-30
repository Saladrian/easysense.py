import logging
from typing import Dict, Any


log = logging.getLogger(__name__)


class Easysense:
    sensors: Dict[str, Any] = {}

    def give_data(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method!")


def ask_install(prompt: str, error_msg: str = "Please enter valid data."):
    user_input = input(prompt)
    try:
        if user_input.strip().lower() in "yn":
            return user_input.lower() == "y"
        else:
            raise ValueError

    except ValueError:
        print(error_msg)
        return ask_install(prompt, error_msg)
