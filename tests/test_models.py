"""
Test cases for Inventory Model

"""
from itertools import product
import os
import logging
import unittest
from service import app
from service.models import Inventory, Product, DataValidationError, db, Condition, Stock_Level
from tests.factory import InventoryFactory, ProductFactory

# DATABASE_URI = os.getenv(
#     "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
# )
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  <Inventory>   M O D E L   T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.session.query(Product).delete() 
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################


    def test_create_an_inventory(self):
        """It should Create an inventory and assert that it exists"""
        fake_inventory = InventoryFactory()
        inventory = Inventory(
            name=fake_inventory.name, 
        )
        self.assertIsNotNone(inventory)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.name, fake_inventory.name)
    

    def test_add_a_inventory(self):
        """It should Create an inventory and add it to the database"""
        inventorys = Inventory.all()
        self.assertEqual(inventorys, [])
        inventory = InventoryFactory()
        inventory.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(inventory.id)
        inventorys = inventory.all()
        self.assertEqual(len(inventorys), 1)

    def test_read_inventory(self):
        """It should Read[find by id] an inventory"""
        inventory = InventoryFactory()
        inventory.create()
        
        # Read it back
        found_inventory = Inventory.find(inventory.id)
        self.assertEqual(found_inventory.id, inventory.id)
        self.assertEqual(found_inventory.name, inventory.name)
        self.assertEqual(found_inventory.products, [])
    
    def test_update_inventory(self):
        """It should Update an inventory"""
        inventory = InventoryFactory(name="iphone")
        inventory.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(inventory.id)
        self.assertEqual(inventory.name, "iphone")

        # Fetch it back
        inventory = inventory.find(inventory.id)
        inventory.name = "iphone_discount"
        inventory.update()

        # Fetch it back again
        inventory = Inventory.find(inventory.id)
        self.assertEqual(inventory.name, "iphone_discount")

    def test_delete_an_inventory(self):
        """It should Delete an inventory from the database"""
        inventorys = Inventory.all()
        self.assertEqual(inventorys, [])
        inventory = InventoryFactory()
        inventory.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(inventory.id)
        inventorys = inventory.all()
        self.assertEqual(len(inventorys), 1)
        inventory = inventorys[0]
        inventory.delete()
        inventorys = inventory.all()
        self.assertEqual(len(inventorys), 0)

    def test_list_all_inventorys(self):
        """It should List all inventorys in the database"""
        inventorys = Inventory.all()
        self.assertEqual(inventorys, [])
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
        # Assert that there are now 5 inventorys in the database
        inventorys = inventory.all()
        self.assertEqual(len(inventorys), 5)

    def test_find_by_name(self):
        """It should Find an inventory by name"""
        inventory = InventoryFactory()
        inventory.create()

        # Fetch it back by name
        same_inventory = Inventory.find_by_name(inventory.name)[0]
        self.assertEqual(same_inventory.id, inventory.id)
        self.assertEqual(same_inventory.name, inventory.name)



    def test_serialize_an_inventory(self):
        """It should Serialize an inventory"""
        inventory = InventoryFactory()
        product = ProductFactory()
        inventory.products.append(product)
        serial_inventory = inventory.serialize()
        self.assertEqual(serial_inventory["id"], inventory.id)
        self.assertEqual(serial_inventory["name"], inventory.name)
        self.assertEqual(len(serial_inventory["products"]), 1)
        products = serial_inventory["products"]
        self.assertEqual(products[0]["id"], product.id)
        self.assertEqual(products[0]["inventory_id"], product.inventory_id)
        self.assertEqual(products[0]["condition"], product.condition)
        self.assertEqual(products[0]["restock_level"], product.restock_level)
        self.assertEqual(products[0]["quantity"], product.quantity)


    def test_deserialize_an_inventory(self):
        """It should Deserialize an inventory"""
        inventory = InventoryFactory()
        inventory.products.append(ProductFactory())
        inventory.create()
        serial_inventory = inventory.serialize()
        products = serial_inventory["products"]
        # for type consideration(deserialize is for json data which is only string, but the 
        # creation via ProductFactory, data in some fields is Enum.) 
        products[0]["condition"] = products[0]["condition"].name
        products[0]["restock_level"] = products[0]["restock_level"].name
        # if not, the next step deserialize() would err.
        new_inventory = Inventory()
        new_inventory.deserialize(serial_inventory)
        self.assertEqual(new_inventory.name, inventory.name)


    #assertRaises(ERROR, a, args): check that when a is called with args that it raises ERROR
    def test_deserialize_with_key_error(self):
        """It should not Deserialize an inventory with a KeyError"""
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an inventory with a TypeError"""
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, [])

    def test_deserialize_product_key_error(self):
        """It should not Deserialize an product with a KeyError"""
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, {})

    # def test_deserialize_product_attribute_error(self):
    #     """It should not Deserialize an product with a AttributeError"""
    #     inventory = InventoryFactory()
    #     product = ProductFactory()
    #     inventory.products.append(product)
    #     product.condition = 3

    #     self.assertRaises(DataValidationError, product.deserialize, product)

    def test_deserialize_product_type_error(self):
        """It should not Deserialize an product with a TypeError"""
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, [])

    def test_find_by_condition(self):
        """It should return all products under a certain condition"""
        #generate data for tests
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
            product = ProductFactory()
            inventory.products.append(product)
        #eg. check OPEN_BOX
        #check that OPEN_BOX products only exist in open_box_cll but no in the remaining cll 
        open_box_cll = Product.find_by_condition(Condition.OPEN_BOX).all()
        for open_box in open_box_cll:
            self.assertEqual(open_box.condition.name, "OPEN_BOX")
        for prod in [prod for prod in Product.all() if prod not in open_box_cll]:
               self.assertNotEqual(prod.condition.name, "OPEN_BOX")

    def test_find_by_restock_level(self):
        """It should return all products under a certain condition"""
        #generate data for tests
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
            product = ProductFactory()
            inventory.products.append(product)
        #eg. check LOW
        #check that LOW stock level products only exist in low_cll but not in the remaining cll
        low_stock_cll = Product.find_by_restock_level(Stock_Level.LOW).all()
        for low_stock in low_stock_cll:
            self.assertEqual(low_stock.restock_level.name, "LOW")
        for prod in [prod for prod in Product.all() if prod not in low_stock_cll]:
               self.assertNotEqual(prod.restock_level.name, "LOW")

    def test_find_by_condition_and_restock_level(self):
        #generate data for tests
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
            product = ProductFactory()
            inventory.products.append(product)
        #check LOW and OPEN_BOX
        #check that filtered products only exist in open_box_and_low_cll but not in the remaining cll
        open_box_and_low_cll = Product.find_by_condition_and_restock_level(Condition.OPEN_BOX, Stock_Level.LOW).all()
        for open_box_and_low in open_box_and_low_cll:
            self.assertEqual(open_box_and_low.condition.name, "OPEN_BOX")
            self.assertEqual(open_box_and_low.restock_level.name, "LOW")

        for prod in [prod for prod in Product.all() if prod not in open_box_and_low_cll]:
            assert_indicator = 0
            if (prod.restock_level.name =="LOW"): assert_indicator += 1
            if (prod.condition.name == "OPEN_BOX"): assert_indicator += 1
            self.assertNotEqual(assert_indicator, 2)



        

##############################

    # def test_add_inventory_product(self):
    #     """It should Create an inventory with an product and add it to the database"""
    #     inventorys = inventory.all()
    #     self.assertEqual(inventorys, [])
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
    #     inventorys = inventory.all()
    #     self.assertEqual(len(inventorys), 1)

    #     new_inventory = Inventory.find(inventory.id)
    #     self.assertEqual(inventory.products[0].name, product.name)

    #     product2 = ProductFactory()
    #     inventory.products.append(product2)
    #     inventory.update()

    #     new_inventory = Inventory.find(inventory.id)
    #     self.assertEqual(len(inventory.products), 2)
    #     self.assertEqual(inventory.products[1].name, product2.name)
