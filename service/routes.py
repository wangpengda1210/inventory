"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from .utils import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Inventory, Product, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Inventory REST API Service",
            version="1.0",
            paths=url_for("list_inventories", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL INVENTORIES 
######################################################################
@app.route("/inventories", methods=["GET"])
def list_inventories():
    """Returns all of the Inventories"""
    app.logger.info("Request for Inventory list")
    inventories = []
    name = request.args.get("name")
    if name:
        inventories = Inventory.find_by_name(name)
    else:
        inventories = Inventory.all()

    results = [inventory.serialize() for inventory in inventories]
    return make_response(jsonify(results), status.HTTP_200_OK)


# ######################################################################
# # RETRIEVE AN INVENTORY   (#story 4) 
# ######################################################################
# @app.route("/inventories/<int:inventory_id>", methods=["GET"])
# def get_inventories(inventory_id):
#     """
#     Retrieve a single Inventory

#     This endpoint will return an Inventory based on it's id
#     """
#     app.logger.info("Request for Inventory with id: %s", inventory_id)
#     inventory = Inventory.find(inventory_id)
#     if not inventory:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Inventory with id '{inventory_id}' could not be found.",
#         )

#     return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)


# #####################################################################
# # CREATE A NEW INVENTORY (#story 8)
# #####################################################################
# @app.route("/inventories", methods=["POST"])
# def create_inventories():
#     """
#     Creates an Inventory
#     This endpoint will create an inventory based the data in the body that is posted
#     """
#     app.logger.info("Request to create an Inventory")
#     check_content_type("application/json")
#     inventory = Inventory()
#     inventory.deserialize(request.get_json())
#     inventory.create()
#     message = inventory.serialize()
#     location_url = url_for("create_inventories", inventory_id=inventory.id, _external=True)
#     return make_response(
#         jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
#     )

# ######################################################################
# # UPDATE AN EXISTING INVENTORY  (#story 10)
# ######################################################################
# @app.route("/accounts/<int:account_id>", methods=["PUT"])
# def update_accounts(account_id):
#     """
#     Update an Account

#     This endpoint will update an Account based the body that is posted
#     """
#     app.logger.info("Request to update account with id: %s", account_id)
#     check_content_type("application/json")
#     account = Account.find(account_id)
#     if not account:
#         abort(
#             status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found."
#         )

#     account.deserialize(request.get_json())
#     account.id = account_id
#     account.update()
#     return make_response(jsonify(account.serialize()), status.HTTP_200_OK)


# ######################################################################
# # DELETE AN INVENTORY   (#story 9)
# ######################################################################
# @app.route("/accounts/<int:account_id>", methods=["DELETE"])
# def delete_accounts(account_id):
#     """
#     Delete an Account

#     This endpoint will delete an Account based the id specified in the path
#     """
#     app.logger.info("Request to delete account with id: %s", account_id)
#     account = Account.find(account_id)
#     if account:
#         account.delete()
#     return make_response("", status.HTTP_204_NO_CONTENT)



# ---------------------------------------------------------------------
#                P R O D U C T   M E T H O D S
# ---------------------------------------------------------------------



# #####################################################################
# # FILTER BY CONDITIONS (#story 12)
# #####################################################################





######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )
