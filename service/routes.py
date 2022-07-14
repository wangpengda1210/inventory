"""
My Service

Describe what your service does here
"""


# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL

# ######################################################################
# # IMPORT DEPENDENCIES
# ######################################################################

from flask import jsonify, request, url_for, make_response, abort
from service.models import Inventory
from .utils import status  # HTTP Status Codes
# Import Flask application
from . import app

# ######################################################################
# # GET INDEX
# ######################################################################
# @app.route("/")
# def index():
#     """Root URL response"""
#     app.logger.info("Request for Root URL")
#     return (
#         jsonify(
#             name="Inventory REST API Service",
#             version="1.0",
#             paths=url_for("list_inventories", _external=True),
#         ),
#         status.HTTP_200_OK,
#     )


######################################################################
# LIST ALL INVENTORIES
######################################################################
@app.route("/inventories", methods=["GET"])
def list_inventories():
    """Returns all of the Inventories"""
    app.logger.info("Request for Inventory list")
    inventories = []

    # Comment out for future development
    # name = request.args.get("name")
    # if name:
    #     inventories = Inventory.find_by_name(name)
    # else:
    #     inventories = Inventory.all()

    # For now, just list all Inventories
    inventories = Inventory.all()

    results = [inventory.serialize() for inventory in inventories]
    return make_response(jsonify(results), status.HTTP_200_OK)


# # ######################################################################
# # # RETRIEVE AN INVENTORY   (#story 4)
# # ######################################################################
@app.route("/inventories/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """
    Retrieve a single Inventory

    This endpoint will return an Inventory based on it's id
    """
    app.logger.info("Request for Inventory with id: %s", inventory_id)
    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' could not be found.",
        )

    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


#####################################################################
# CREATE A NEW INVENTORY (#story 8)
#####################################################################
@app.route("/inventories", methods=["POST"])
def create_inventories():  # noqa: C901
    """
    Creates an Inventory
    This endpoint will create an inventory based the data in the body that is posted
    """
    app.logger.info("Request to create an Inventory")
    check_content_type("application/json")

    inventory = Inventory()
    inventory.deserialize(request.get_json())
    inventory.create()

    app.logger.info("Inventory [%s] created.", inventory.id)

    message = inventory.serialize()
    location_url = url_for(
        "create_inventories", inventory_id=inventory.id, _external=True
    )
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


# # ######################################################################
# # # UPDATE AN EXISTING INVENTORY  (#story 10)
# # ######################################################################
# @app.route("/inventories/<int:inventory_id>", methods=["PUT"])
# def update_inventory(inventory_id):
#     """
#     Update an Inventory

#     This endpoint will update an Inventory based the body that is posted
#     """
#     app.logger.info("Request to update inventory with id: %s", inventory_id)
#     check_content_type("application/json")

#     name = request.get_json().get("name")
#     # If there is no name in json, request can't be process
#     if not name:
#         abort(
#             status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Inventory name was not provided."
#         )

#     inventory = Inventory.find(inventory_id)
#     if not inventory:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Inventory with id '{inventory_id}' was not found.",
#         )
#     inventory.deserialize(request.get_json())
#     inventory.id = inventory_id
#     inventory.update()
#     return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


# # ######################################################################
# # # DELETE AN INVENTORY   (#story 9)
# # ######################################################################
@app.route("/inventories/<int:inventory_id>", methods=["DELETE"])
def delete_inventory(inventory_id):
    """
    Delete an Inventory
    This endpoint will delete an Inventory based id specified in the path
    """
    app.logger.info("Request to delete inventory with id: %s", inventory_id)
    inventory = Inventory.find(inventory_id)
    if inventory:
        inventory.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


# # #####################################################################
# # # RETRIEVE A PRODUCT FROM AN INVENTORY (#story 4)
# # #####################################################################
# @app.route("/inventories/<int:inventory_id>/products/<int:product_id>", methods=["GET"])
# def get_products(inventory_id, product_id):
#     """
#     Retrieve Products of an Inventory

#     This endpoint returns a group of Products with a same condition
#     """
#     app.logger.info(
#         "Request to retrieve Products %s for Inventory id: %s",
#         (product_id, inventory_id),
#     )
#     product = Product.find(product_id)
#     if not product:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Products with id '{product_id}' could not be found.",
#         )

#     return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


# # #####################################################################
# # # UPDATE A PRODUCT FROM AN INVENTORY (#story 10)
# # #####################################################################
# @app.route("/inventories/<int:inventory_id>/products/<int:product_id>", methods=["PUT"])
# def update_products(inventory_id, product_id):
#     """
#     Update Products of an Inventory

#     This endpoint update a group of Products with a same condition
#     """
#     app.logger.info(
#         "Request to update Products %s for Inventory id: %s", (product_id, inventory_id)
#     )
#     check_content_type("application/json")
#     update_product = Product.find(product_id)
#     if not update_product:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Product with id '{product_id}' could not be found.",
#         )
#     request_product = request.get_json()
#     update_product.deserialize(request_product)
#     update_product.id = product_id
#     update_product.update()
#     app.logger.info("Updated")
#     return make_response(jsonify(update_product.serialize()), status.HTTP_200_OK)


# ######################################################################
# #  U T I L I T Y   F U N C T I O N S
# ######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
