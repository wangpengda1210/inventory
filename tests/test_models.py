"""
Test cases for Inventory Model

"""
import os
import logging
# from typing import Type
import unittest
from service import app
from service.models import (
    Inventory,
    DataValidationError,
    DuplicateKeyValueError,
    db,
    Condition,
    StockLevel,

)
# from service.models import Product
from tests.factory import InventoryFactory

# DATABASE_URI = os.getenv(
#     "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
# )
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  M O D E L   T E S T   C A S E S
######################################################################


class TestInventory(unittest.TestCase):
    """Test Cases for Inventory Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.drop_all()

    def setUp(self):
        """This runs before each test"""
        # db.session.query(Product).delete()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_inventory(self):
        """It should Create an inventory and assert that it exists"""
        fake_inventory = InventoryFactory()
        inventory = Inventory(
            product_id=fake_inventory.product_id,
            condition = fake_inventory.condition,
            restock_level = fake_inventory.restock_level,
            quantity = fake_inventory.quantity
        )
        self.assertIsNone(inventory.inventory_id)
        self.assertIsNotNone(inventory)
        self.assertEqual(inventory.condition, fake_inventory.condition)
        self.assertEqual(inventory.quantity, fake_inventory.quantity)
        self.assertEqual(inventory.restock_level, fake_inventory.restock_level)
        # inventory.create()

    def test_add_a_inventory(self):
        """It should Create an inventory and add it to the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        inventory = InventoryFactory()
        inventory.create()
        # Assert that it generated an inventory_id and shows up in the database
        self.assertIsNotNone(inventory.inventory_id)
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)

    def test_read_inventory(self):
        """
        It should Read[find by id] an inventory
        Step1 create instance of inventory
        Step2 list all inventory
        Step3 query with inventory_id
        
        """
        inventory = InventoryFactory()
        inventory.create()
        # Read it back
        inventory_list = Inventory.all()
        only_inventory = inventory_list[0]
        inventory_id = only_inventory.inventory_id
        self.assertIsNotNone(inventory_id)
        found_inventory = Inventory.find(inventory_id)
        self.assertEqual(found_inventory.inventory_id, inventory_id)
        self.assertEqual(found_inventory.product_id,inventory.product_id)
        self.assertEqual(found_inventory.condition,inventory.condition)
        self.assertEqual(found_inventory.restock_level,inventory.restock_level)
        self.assertEqual(found_inventory.quantity,inventory.quantity)

    def test_update_inventory(self):
        """It should Update an inventory"""
        inventory = InventoryFactory(product_id=12345)
        inventory.create()
        # Assert that it generated an inventory_id and shows up in the database
        self.assertIsNotNone(inventory.inventory_id)
        self.assertEqual(inventory.product_id, 12345)
        # Fetch it back
        inventory = Inventory.find(inventory.inventory_id)
        inventory.product_id = "54321"
        inventory.update()

        # Fetch it back again
        inventory = Inventory.find(inventory.inventory_id)
        self.assertEqual(inventory.product_id, 54321)

    def test_delete_an_inventory(self):
        """It should Delete an inventory from the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        inventory = InventoryFactory()
        inventory.create()
        # Assert that it generated an inventory_id and shows up in the database
        self.assertIsNotNone(inventory.inventory_id)
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)
        inventory = inventories[0]
        inventory.delete()
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 0)

    def test_list_all_inventories(self):
        """It should List all inventories in the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
        # Assert that there are now 5 inventories in the database
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 5)

    # def test_find_by_name(self):
    #     """It should Find an inventory by name"""
    #     inventory = InventoryFactory()
    #     inventory.create()

    #     # Fetch it back by name
    #     same_inventory = Inventory.find_by_name(inventory.name)[0]
    #     self.assertEqual(same_inventory.id, inventory.id)
    #     self.assertEqual(same_inventory.name, inventory.name)

    def test_serialize_an_inventory(self):
        """It should Serialize an inventory"""
        inventory = InventoryFactory()
        # product = ProductFactory()
        # inventory.products.append(product)
        serial_inventory = inventory.serialize()
        self.assertEqual(serial_inventory["inventory_id"], inventory.inventory_id)
        self.assertEqual(serial_inventory["product_id"], inventory.product_id)
        self.assertEqual(serial_inventory["condition"], inventory.condition)
        self.assertEqual(serial_inventory["restock_level"], inventory.restock_level)
        self.assertEqual(serial_inventory["quantity"], inventory.quantity)

    def test_deserialize_an_inventory(self):
        """It should Deserialize an inventory"""
        inventory = InventoryFactory()
        # inventory.products.append(ProductFactory())
        
        inventory.create()

        serial_inventory = inventory.serialize()
        print(serial_inventory)
        # products = serial_inventory["products"]
        # for type consideration(deserialize is for json data which is only string, but the
        # creation via InventoryFactory, data in some fields is Enum.)
        serial_inventory ["condition"] = serial_inventory ["condition"].name
        serial_inventory ["restock_level"] = serial_inventory ["restock_level"].name
        # if not, the next step deserialize() would err.
        new_inventory = Inventory()
        new_inventory.deserialize(serial_inventory)
        self.assertEqual(new_inventory.product_id, inventory.product_id)
        self.assertEqual(new_inventory.condition, inventory.condition)
        self.assertEqual(new_inventory.restock_level, inventory.restock_level)
        self.assertEqual(new_inventory.quantity, inventory.quantity)

    # assertRaises(ERROR, a, args): check that when a is called with args that it raises ERROR
    def test_deserialize_with_key_error(self):
        """It should not Deserialize an inventory with a KeyError"""
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an inventory with a TypeError"""
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, [])

    def test_find_by_condition(self):
        """It should return all products under a certain condition"""
        # generate data for tests
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
            # product = ProductFactory()
            # inventory.products.append(product)
        # eg. check OPEN_BOX
        # check that OPEN_BOX products only exist in open_box_cll but no in the remaining cll
        open_box_cll = Inventory.find_by_condition(Condition.OPEN_BOX).all()
        for open_box in open_box_cll:
            self.assertEqual(open_box.condition.name, "OPEN_BOX")
        for inv in [inv for inv in Inventory.all() if inv not in open_box_cll]:
            self.assertNotEqual(inv.condition.name, "OPEN_BOX")

    def test_find_by_restock_level(self):
        """It should return all products under a certain condition"""
        # generate data for tests
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
            # product = ProductFactory()
            # inventory.products.append(product)
        # eg. check LOW
        # check that LOW stock level products only exist in low_cll but not in the remaining cll
        low_stock_cll = Inventory.find_by_restock_level(StockLevel.LOW).all()
        for low_stock in low_stock_cll:
            self.assertEqual(low_stock.restock_level.name, "LOW")
        for inv in [inv for inv in Inventory.all() if inv not in low_stock_cll]:
            self.assertNotEqual(inv.restock_level.name, "LOW")

    def test_find_by_condition_and_restock_level(self):
        """It should return all products under condition & restock_level"""
        # generate data for tests
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
            # product = ProductFactory()
            # inventory.products.append(product)
        # check LOW and OPEN_BOX
        # check that filtered products only exist in open_box_and_low_cll
        # but not in the remaining cll
        open_box_and_low_cll = Inventory.find_by_condition_and_restock_level(
            Condition.OPEN_BOX, StockLevel.LOW
        ).all()
        for open_box_and_low in open_box_and_low_cll:
            self.assertEqual(open_box_and_low.condition.name, "OPEN_BOX")
            self.assertEqual(open_box_and_low.restock_level.name, "LOW")

        for inv in [
            inv for inv in Inventory.all() if inv not in open_box_and_low_cll
        ]:
            assert_indicator = 0
            if inv.restock_level.name == "LOW":
                assert_indicator += 1
            if inv.condition.name == "OPEN_BOX":
                assert_indicator += 1
            self.assertNotEqual(assert_indicator, 2)

    def test_duplicate_compound_keys(self):
        fake_inventory = InventoryFactory()
        inventory_1 = Inventory(
            product_id=fake_inventory.product_id,
            condition = fake_inventory.condition,
            restock_level = fake_inventory.restock_level,
            quantity = fake_inventory.quantity
        )
        inventory_1.create()
        inventory_2 = Inventory(
            product_id=fake_inventory.product_id,
            condition = fake_inventory.condition,
            restock_level = fake_inventory.restock_level,
            quantity = fake_inventory.quantity
        )
        self.assertRaises(DuplicateKeyValueError,inventory_2.create)





##############################

# def test_add_inventory_product(self):
#     """It should Create an inventory with an product and add it to the database"""
#     inventories = inventory.all()
#     self.assertEqual(inventories, [])
#     inventory = InventoryFactory()
#     inventory.create()
#     logging.debug("Created: %s", inventory.serialize())
#     product = ProductFactory()
#     inventory.products.append(product)
#     inventory.update()
#     logging.debug("Updated: %s", inventory.serialize())
#     # Assert that it was assigned an id and shows up in the database
#     # [both inventory and product table]
#     self.assertIsNotNone(inventory.id)
#     inventories = inventory.all()
#     self.assertEqual(len(inventories), 1)

#     new_inventory = Inventory.find(inventory.id)
#     self.assertEqual(inventory.products[0].name, product.name)

#     product2 = ProductFactory()
#     inventory.products.append(product2)
#     inventory.update()

#     new_inventory = Inventory.find(inventory.id)
#     self.assertEqual(len(inventory.products), 2)
#     self.assertEqual(inventory.products[1].name, product2.name)
