from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from core import conf

template_dir = Environment(loader=FileSystemLoader('ui'))


def render(template_name: str, args=None):
    # Set the default template arguments.
    if args is None:
        args = dict()
    # Render the template.
    template = template_dir.get_template(template_name)
    return HTMLResponse(template.render({**args, 'game_name': conf.GAME_TITLE}))
