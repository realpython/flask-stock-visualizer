# from werckercli.decorators import login_required
from werckercli.decorators import login_required


@login_required
def login(valid_token=None):

    if not valid_token:
        raise ValueError("A valid token is required!")
