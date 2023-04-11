from typing import Optional

from libgravatar import Gravatar


async def get_gravatar(email: str) -> Optional[str]:
    """
    The get_gravatar function takes an email address and returns the URL of a Gravatar image for that email.
    If no Gravatar is found, it returns None.

    :param email: str: Specify the email address of the user
    :return: A url to the gravatar image
    :doc-author: Trelent
    """
    try:
        return Gravatar(email).get_image()
    except Exception as e:
        print(e)
