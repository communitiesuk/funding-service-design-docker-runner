from flask import Flask

from jinja2 import PackageLoader, ChoiceLoader
from flask_assets import Bundle
from jinja2 import PrefixLoader
from app.blueprints.self_serve.routes import self_serve_bp
from flask_assets import Environment
import static_assets

def create_app() -> Flask:

    flask_app = Flask("__name__", static_url_path="/assets")

    flask_app.register_blueprint(self_serve_bp)

    # flask_app.static_url_path = "/static"
    flask_app.static_folder = "app/static/dist"


    # Bundle and compile assets
    assets = Environment()
    assets.init_app(flask_app)

    static_assets.init_assets(
        flask_app,
        auto_build=True,
        static_folder="app/static/dist",
    )

    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )


    return flask_app

app = create_app()