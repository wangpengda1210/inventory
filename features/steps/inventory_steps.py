"""
Inventory Steps

Steps file for inventories.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given('the following inventories')
def step_impl(context):
    """ Delete all Inventories and load new ones """
    # List all of the Inventories and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/api/inventories"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for inventory in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{inventory['inventory_id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new pets
    for row in context.table:
        payload = {
            "condition": row['condition'],
            "product_id": row['product_id'],
            "quantity": row['quantity'],
            "restock_level": row['restock_level'],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        context.clipboard = context.resp.json()['inventory_id']
        expect(context.resp.status_code).to_equal(201)
