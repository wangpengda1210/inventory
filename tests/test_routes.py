"""
TestInventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from tests.factory import InventoryFactory, ProductFactory, Condition
from service import app
from service.models import db, Inventory, init_db, Product
from service.utils import status  # HTTP Status Codes

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/inventories"


######################################################################
#  T E S T   C A S E S
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
        pass

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
            # print(inventory.serialize())
            inventories_json.append(inventory.serialize())

        return inventories_json

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

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
        self.assertEqual(data, [],"wrong response")
        # when there is 5 inventories, return 5 inventories
        self._create_inventories(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

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
        print(resp.get_json())
        # send the second request
        resp = self.client.post(BASE_URL, json=requests_json[1])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        print(resp.get_json())

        # set a conflict condition
        conflict_json = self._generate_inventories_with_products(1,2)[0]
        conflict_products_first = conflict_json["products"][0]
        conflict_products_first["condition"] = Condition.USED
        conflict_products_second = conflict_json["products"][1]
        conflict_products_second["condition"] = Condition.OPEN_BOX
        conflict_json["name"] = requests_json[0]["name"]
        print(conflict_json)
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
