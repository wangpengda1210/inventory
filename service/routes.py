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

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    # return (
    #     jsonify(
    #         name="Inventory REST API Service",
    #         version="1.0",
    #         paths=url_for("list_inventories", _external=True),
    #     ),
    #     status.HTTP_200_OK,
    # )
    return app.send_static_file("index.html")

######################################################################
# LIST ALL INVENTORIES
######################################################################
@app.route("/inventories", methods=["GET"])
def list_inventories():
    """Returns all of the Inventories"""
    app.logger.info("Request for Inventory list")
    inventories = []

    req_dict = request.args
    app.logger.info(len(req_dict))

    if len(req_dict) == 0:
        inventories = Inventory.all()
    else:
        inventories = Inventory.find_by_attributes(req_dict)

    results = [inventory.serialize() for inventory in inventories]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE AN INVENTORY   (#story 4)
######################################################################
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
    This endpoint will create an inventory
    based on the data in the body that is posted
    """
    app.logger.info("Request to create an Inventory")
    check_content_type("application/json")

    inventory = Inventory()
    inventory.deserialize(request.get_json())
    inventory.create()

    app.logger.info("Inventory [%s] created.", inventory.inventory_id)

    message = inventory.serialize()
    location_url = url_for(
        "create_inventories", inventory_id=inventory.inventory_id, _external=True
    )

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


# # ######################################################################
# # # UPDATE AN EXISTING INVENTORY  (#story 10)
# # ######################################################################
@app.route("/inventories/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    """
    Update an Inventory

    This endpoint will update an Inventory based the body that is posted
    """
    app.logger.info("Request to update inventory with id: %s", inventory_id)
    check_content_type("application/json")

    inventory = Inventory.find(inventory_id)
    if not inventory:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with id '{inventory_id}' was not found.",
        )
    # inventory.deserialize(request.get_json())
    # inventory.id = inventory_id
    # inventory.update()
    inventory.update(request.get_json())
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE AN INVENTORY   (#story 9)
######################################################################
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


######################################################################
# DELETE ALL INVENTORIES (Action)
######################################################################
@app.route("/inventories/clear", methods=["DELETE"])
def delete_all_inventories():
    """
    Delete all Inventories
    This endpoint will delete all Inventories
    """
    app.logger.info("Request to delete all inventories")
    inventories = Inventory.all()
    for inventory in inventories:
        inventory.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# UPDATE QUANTITY UNDER PRODUCT_ID & CONDITION (Action)
######################################################################
@app.route("/inventories/changeQuantity", methods=["PUT"])
def update_inventory_by_product_id_condition():
    """
    Update an Inventory by product_id & condition

    This endpoint will update an Inventory based on the body that is posted
    """
    check_content_type("application/json")

    request_dict = request.get_json()
    req_product_id = request_dict["product_id"]
    req_condition = request_dict["condition"]

    app.logger.info(
        "Request to update inventory with "
        "product_id: %s & condition: %s",
        req_product_id, req_condition)

    inventories = Inventory.find_by_attributes(
        {"product_id": req_product_id,
         "condition": req_condition}
    ).all()
    if not inventories:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory with product_id '{req_product_id}' & "
            f"condition '{req_condition}' was not found.",
        )
    assert(len(inventories) == 1)
    app.logger.info("%s", type(inventories))
    inventory = inventories[0]
    # inventory.deserialize(request_dict)
    # inventory.update()
    inventory.update(request_dict)
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


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
