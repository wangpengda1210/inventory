"""
TestInventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factory import InventoryFactory, ProductFactory, Condition
from service import app
from service.models import db, Inventory, init_db, Product
from service.utils import status  # HTTP Status Codes

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/inventories"


######################################################################
#  R O U T E   T E S T   C A S E S
######################################################################
class TestInventoryServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        db.session.query(Product).delete()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_inventories(self, count):
        """Factory method to create inventories in bulk"""
        inventories = []
        for _ in range(count):
            inventory = InventoryFactory()
            resp = self.client.post(BASE_URL, json=inventory.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test inventory",
            )
            new_inventory = resp.get_json()
            inventory.id = new_inventory["id"]
            inventories.append(inventory)
        return inventories

    def _generate_inventories_with_products(self, num_inventories, num_products):
        """Factory method to create inventories with products in bulk"""
        inventories_json = []
        for __ in range(num_inventories):
            inventory = InventoryFactory()
            for _ in range(num_products):
                product = ProductFactory()
                inventory.products.append(product)
            inventories_json.append(inventory.serialize())

        return inventories_json

    # ######################################################################
    # #  T E S T   H A P P Y   P A T H S
    # ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_inventory_list(self):
        """It should Get a list of Inventories"""
        # when no data, return []
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, [], "wrong response")
        # when there is 5 inventories, return 5 inventories
        #create fake data
        requests_json = self._generate_inventories_with_products(5,2)
        successful_create_count = 0
        for i in range(5):
            resp = self.client.post(BASE_URL, json=requests_json[i])
            # self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            if resp.status_code == status.HTTP_201_CREATED:
                successful_create_count +=1
        resp = self.client.get(BASE_URL)
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), successful_create_count)
        products = data[0]["products"]
        self.assertEqual(len(products),2)

    def test_read_inventory(self):
        """It should Read a single Inventory"""
        # get the id of an Inventory
        inventory = self._create_inventories(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{inventory.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], inventory.name)

    def test_create_inventory(self):
        """It should Create an Inventory """
        # generate fake request json
        requests_json = self._generate_inventories_with_products(2,1)

        # create not conflict product in one inventory
        # set two inventories the same name
        requests_json[1]["name"] = requests_json[0]["name"]
        # set the condition different
        products_first = requests_json[0]["products"][0]
        products_first["condition"] = Condition.NEW
        products_second = requests_json[1]["products"][0]
        products_second["condition"] = Condition.OPEN_BOX
        # send the first request
        resp = self.client.post(BASE_URL, json=requests_json[0])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # send the second request
        resp = self.client.post(BASE_URL, json=requests_json[1])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create different inventory
        requests_json[0]["name"] += "_diff"
        resp = self.client.post(BASE_URL, json=requests_json[0])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_update_inventory(self):
        """It should Update an Inventory"""
        # generate fake request json
        requests_json = self._generate_inventories_with_products(1,1)

        # create
        resp = self.client.post(BASE_URL, json=requests_json[0])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update
        new_inventory = resp.get_json()
        new_inventory_id = new_inventory["id"]
        new_inventory["name"] = "James Bond"
        resp = self.client.put(f"{BASE_URL}/{new_inventory_id}", json=new_inventory)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated = resp.get_json()
        self.assertEqual(updated["name"], "James Bond")

    def test_delete_inventory(self):
        """It should Delete an Inventory """
        # generate fake request json
        requests_json = self._generate_inventories_with_products(1,1)

        # create
        resp = self.client.post(BASE_URL, json=requests_json[0])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # delete
        inventory_json = resp.get_json()
        inventory_id = inventory_json["id"]
        resp = self.client.delete(BASE_URL+"/"+ str(inventory_id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        inventories = Inventory.all()
        self.assertEqual(len(inventories), 0)

    def test_read_product(self):
        """It should Read a group of Products (with same condition) from an Inventory"""
        # create a known product
        requests_json = self._generate_inventories_with_products(1,1)
        # print("what's generated:", requests_json)
        resp = self.client.post(BASE_URL, json=requests_json[0])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        # print("what's stored", data)

        inventory_id = data["id"]
        product = data["products"][0]
        product_id = product["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{inventory_id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug(data)
        # print("what's returned", data)

        self.assertEqual(data["inventory_id"], inventory_id)
        self.assertEqual(data["condition"], product["condition"])
        self.assertEqual(data["restock_level"], product["restock_level"])
        self.assertEqual(data["quantity"], product["quantity"])

    def test_update_product(self):
        """It should Update a group of Products (with same condition) from an Inventory"""
        # create a known product
        requests_json = self._generate_inventories_with_products(1,1)
        # print("what's generated:", requests_json)
        resp = self.client.post(BASE_URL, json=requests_json[0])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug("Created %s", data["products"][0])
        # print("what's stored", data)

        inventory_id = data["id"]
        product = data["products"][0]
        product_id = product["id"]

        # update
        product["quantity"] = 3000
        product["condition"] = 3
        logging.debug("Updated %s", product)
        resp = self.client.put(
            f"{BASE_URL}/{inventory_id}/products/{product_id}",
            json=product
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["quantity"], 3000)
        self.assertEqual(updated_product["condition"], 3)

    # ######################################################################
    # #  T E S T   S A D   P A T H S
    # ######################################################################

    def test_create_inventory_no_data(self):
        """It should not Create an Inventory with missing data"""
        resp = self.client.post(BASE_URL, json={})
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_inventory_conflict(self):
        """It should not Create two Inventory Product with same condition"""
        # generate fake json request
        requests_json = self._generate_inventories_with_products(2,1)

        # create not conflict product in one inventory
        # set two inventories the same name
        requests_json[1]["name"] = requests_json[0]["name"]
        # set the condition different
        products_first = requests_json[0]["products"][0]
        products_first["condition"] = Condition.NEW
        products_second = requests_json[1]["products"][0]
        products_second["condition"] = Condition.OPEN_BOX
        # send the first request
        resp = self.client.post(BASE_URL, json=requests_json[0])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # send the second request
        resp = self.client.post(BASE_URL, json=requests_json[1])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # set a conflict condition
        conflict_json = self._generate_inventories_with_products(1,2)[0]
        conflict_products_first = conflict_json["products"][0]
        conflict_products_first["condition"] = Condition.USED
        conflict_products_second = conflict_json["products"][1]
        conflict_products_second["condition"] = Condition.OPEN_BOX
        conflict_json["name"] = requests_json[0]["name"]
        resp = self.client.post(BASE_URL, json=conflict_json)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_create_inventory_no_name(self):
        """It should not Create an Inventory with no inventory name"""
        requests_json = self._generate_inventories_with_products(1,1)[0]
        requests_json.pop("name")
        resp = self.client.post(BASE_URL, json=requests_json)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_inventory_bad_data(self):
        """It should not Create an Inventory Product with bad data"""
        # create inventory with incomplete product data
        requests_json = self._generate_inventories_with_products(1,1)[0]
        requests_json["products"][0].pop("condition")
        resp = self.client.post(BASE_URL, json=requests_json)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_inventory_wrong_content_type(self):
        """It should not use content other than json to Create the Inventory"""
        resp = self.client.post(BASE_URL, data="Wrong Content Type")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_read_inventory_not_found(self):
        """It should not Read the Inventory when it is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_product_not_found(self):
        """It should not Read the Product when it is not found"""
        resp = self.client.get(f"{BASE_URL}/0/products/1")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_inventory_no_name(self):
        """It should not Update the Inventory without inventory name"""
        # create an Inventory
        request_json = self._generate_inventories_with_products(1,1)[0]
        resp = self.client.post(BASE_URL, json=request_json)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # incomplete the update request json by popping the name
        new_inventory = resp.get_json()
        new_inventory_id = new_inventory["id"]
        new_inventory.pop("name")
        resp = self.client.put(f"{BASE_URL}/{new_inventory_id}", json=new_inventory)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_inventory_wrong_content_type(self):
        """It should not use content other than json to Update the Inventory"""
        # create an Inventory
        request_json = self._generate_inventories_with_products(1,1)[0]
        resp = self.client.post(BASE_URL, json=request_json)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_inventory = resp.get_json()
        new_inventory_id = new_inventory["id"]
        resp = self.client.put(f"{BASE_URL}/{new_inventory_id}", data="Wrong Content Type")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_inventory_not_found(self):
        """It should not Update the Inventory when it is not found"""
        request_json = self._generate_inventories_with_products(1,1)[0]
        resp = self.client.put(f"{BASE_URL}/0", json=request_json)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_not_found(self):
        """It should not Update the Product when it is not found"""
        request_json = self._generate_inventories_with_products(1,1)[0]
        resp = self.client.put(f"{BASE_URL}/0/products/0", json=request_json["products"][0])
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_not_exist_inventory(self):
        """It should return 204 when Deleting not exist inventory"""
        # generate fake request json
        inventory_json = self._generate_inventories_with_products(1,1)[0]

        # delete
        inventory_id = inventory_json["id"]
        resp = self.client.delete(BASE_URL+"/"+ str(inventory_id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_methods_not_allowed(self):
        """
        It should not allow
        PUT/DELETE to /inventories
        POST to /inventories/<inventory_id>
        POST/DELETE to /inventories/<inventory_id>/products/<product_id>
        """
        resp = self.client.put(f"{BASE_URL}")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp = self.client.delete(f"{BASE_URL}")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(f"{BASE_URL}/0/products/0")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp = self.client.delete(f"{BASE_URL}/0/products/0")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
