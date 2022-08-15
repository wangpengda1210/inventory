"""
My Service

Describe what your service does here
"""


# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL

# ######################################################################
# # IMPORT DEPENDENCIES
# ######################################################################

from flask import jsonify, request, make_response, abort
from flask_restx import Resource, fields, reqparse
from service.models import Inventory, RestockLevel, Condition
from .utils import status  # HTTP Status Codes
# Import Flask application
from . import app, api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


# define models so that the docs reflect what can be sent
create_model = api.model("Inventory", {
    "product_id": fields.Integer(required=True,
                                 description="The product id for the inventory item"),
    "condition": fields.String(required=True,
                               enum=Condition._member_names_,
                               description="The condition of the inventory item"),
    "restock_level": fields.String(required=True,
                                   enum=RestockLevel._member_names_,
                                   description="The restock level of the inventory item"),
    "quantity": fields.Integer(required=True,
                               default=0,
                               description="The quantity of items available")
})

inventory_model = api.inherit(
    "InventoryModel",
    create_model,
    {
        "inventory_id": fields.Integer(readOnly=True,
                                       description="The unique id assigned internally by service")
    }
)

inventory_args = reqparse.RequestParser()
# 'condition', 'restock_level', 'quantity', 'product_id'
inventory_args.add_argument('condition', type=str, required=False, help='List inventory by condition')
inventory_args.add_argument('restock_level', type=str, required=False, help='List inventory by restock level')
inventory_args.add_argument('quantity', type=int, required=False, help='List inventory by quantity')
inventory_args.add_argument('product_id', type=int, required=False, help='List inventory by product ID')


######################################################################
#  PATH: /inventories/{inventory_id}
######################################################################
@api.route('/inventories/<inventory_id>')
@api.param('inventory_id', 'The Inventory identifier')
class InventoryResource(Resource):
    """
    InventoryResource class
    Allows the manipulation of a single Inventory
    GET /inventories/{inventory_id} - Returns a Inventory with the inventory_id
    PUT /inventories/{inventory_id} - Update a Inventory with the inventory_id
    DELETE /inventories/{inventory_id} - Deletes a Inventory with the inventory_id
    """

    # ------------------------------------------------------------------
    # DELETE AN INVENTORY
    # ------------------------------------------------------------------
    @api.doc('delete_inventories')
    @api.response(204, 'Inventory deleted')
    def delete(self, inventory_id):
        """
        Delete an Inventory
        This endpoint will delete an Inventory based id specified in the path
        """
        app.logger.info("Request to delete inventory with id: %s", inventory_id)
        inventory = Inventory.find(inventory_id)
        if inventory:
            inventory.delete()
            app.logger.info('Inventory with id [%s] was deleted', inventory_id)
        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /inventories
######################################################################
@api.route('/inventories', strict_slashes=False)
class InventoryCollection(Resource):
    """ Handles all interaction with collections of Inventory items """
    # ------------------------------------------------------------------
    # LIST ALL INVENTORIES
    # ------------------------------------------------------------------
    @api.doc('list_inventories')
    @api.expect(inventory_args, validate=True)
    @api.response(400, "Query parameters not valid")
    @api.marshal_list_with(inventory_model)
    def get(self):
        """Returns all of the Inventories"""
        app.logger.info("Request for Inventory list")
        inventories = []

        try:
            req_dict = inventory_args.parse_args()
            req_dict = {k: v for k, v in req_dict.items() if v is not None}

            if len(req_dict) == 0:
                inventories = Inventory.all()
            else:
                inventories = Inventory.find_by_attributes(req_dict)
        except Exception:
            abort(status.HTTP_400_BAD_REQUEST, "Query parameters not valid")

        results = [inventory.serialize() for inventory in inventories]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW INVENTORY
    # ------------------------------------------------------------------
    @api.doc('create_inventories')
    @api.response(400, 'The posted data was not valid')
    @api.response(409, "Re-creating inventory with an existing product_id & condition")
    @api.expect(create_model)
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Creates an Inventory
        This endpoint will create an inventory
        based on the data in the body that is posted
        """
        app.logger.info("Request to create an Inventory")
        inventory = Inventory()
        app.logger.info("Payload = %s", api.payload)
        inventory.deserialize(api.payload)
        inventory.create()

        app.logger.info("Inventory [%s] created.", inventory.inventory_id)

        location_url = api.url_for(
            InventoryResource, inventory_id=inventory.inventory_id, _external=True
        )

        return inventory.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
#  PATH: /inventories/clear
######################################################################
@api.route('/inventories/clear', strict_slashes=False)
class ClearResource(Resource):
    """ Delete all actions for Inventories """
    @api.doc('Delete_inventories')
    @api.expect(inventory_args, validate=True)
    @api.response(204, 'Inventories deleted')
    def delete(self):
        """
        Delete all Selected Inventories
        This endpoint will delete all selected Inventories
        """
        app.logger.info("Request to delete inventories")
        inventories = []

        try:
            req_dict = inventory_args.parse_args()
            req_dict = {k: v for k, v in req_dict.items() if v is not None}
            if len(req_dict) == 0:
                inventories = Inventory.all()
            else:
                inventories = Inventory.find_by_attributes(req_dict)
        except Exception:
            pass

        for inventory in inventories:
            inventory.delete()
            app.logger.info('Inventory with id [%s] was deleted', inventory.inventory_id)
        return '', status.HTTP_204_NO_CONTENT

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
    assert (len(inventories) == 1)
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
    return make_response(jsonify(status=200, message="OK"), status.HTTP_200_OK)


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
