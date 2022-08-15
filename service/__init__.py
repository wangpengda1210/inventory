"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
import logging  # noqa: F401 E402
from flask import Flask
from flask_restx import Api
from .utils import log_handlers
from service import config

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

app.url_map.strict_slashes = False

api = Api(app,
          version="1.0.0",
          title="Inventory REST API Service",
          description="This is a sample inventory API server",
          default="inventories",
          default_label="Inventory item operations",
          doc="/apidocs",
          prefix="/api"
          )


# Dependencies require we import the routes AFTER the Flask app is created
from service import (  # noqa: F401 E402
    routes,
    models,
)  # pylint: disable=wrong-import-position, wrong-import-order
from .utils import error_handlers  # pylint: disable=wrong-import-position  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # make our SQLAlchemy tables
except Exception as error:
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
