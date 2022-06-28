"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from enum import Enum, IntEnum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

def init_db(app):
    """Initialize the SQLAlchemy app"""
    Inventory.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class Condition(IntEnum):
    """Enumeration of condition of a valid Inventory """
    NEW = 1
    OPEN_BOX = 2
    USED = 3
    UNKNOWN = 4

class StockLevel(IntEnum):
    """Enumeration of Stock_Level of a valid Inventory """
    EMPTY = 0
    LOW = 1
    MODERATE = 2
    PLENTY = 3

######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################

class PersistentBase:
    """Base class added persistent methods"""

    def create(self):
        """
        Creates a record to the database
        """
        # logger.info("Creating %s", self.name)
        logger.info("Creating")
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a record to the database
        """
        logger.info("Updating %s", self.id)
        db.session.commit()

    def delete(self):
        """Removes a record from the data store"""
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


class Product(db.Model, PersistentBase):
    """
    Class that represents a Product

    Provide a one-to-many relationship between an inventory and its condition,
    restock level and number.
    """
    #Table Schema
    id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(
        db.Enum(Condition), nullable=False, server_default=(Condition.UNKNOWN.name)
    )
    restock_level = db.Column(
        db.Enum(StockLevel), nullable=False, server_default=(StockLevel.EMPTY.name)
    )
    quantity = db.Column(db.Integer, nullable=False, default=0)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id', ondelete="CASCADE"),
                    nullable=False)


    def __repr__(self):
        return f"<Product {self.condition} id=[{self.id}] inventory[{self.inventory_id}]>"

    # def __str__(self):
    #     return "%s: %s, %s" % (
    #         self.quantity,
    #         self.id,
    #         self.inventory_id,
    #     )

    def serialize(self) -> dict:
        """ Serializes a Product into a dictionary """
        return {
            "id": self.id,
            "condition": self.condition,
            "restock_level": self.restock_level,
            "quantity": self.quantity,
            "inventory_id": self.inventory_id,
            }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.condition =  data["condition"]  # create enum from string
            self.restock_level = data["restock_level"]  # create enum from string
            self.quantity = data["quantity"]

        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data" + str(error)
            )
        return self


    ##################################################
        # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_condition(cls, condition: Enum) -> list:
        """Returns all of the Products in a condition

        :param condition: the condition of the Products you want to match
        :type condition: Enum

        :return: a collection of Products in that condition
        :rtype: list

        """
        logger.info("Processing condition query for %s ...", condition)
        return cls.query.filter(cls.condition == condition)

    @classmethod
    def find_by_inventory_id(cls, inventory_id) -> list:
        """Returns all of the Products in a condition

        :param condition: the condition of the Products you want to match
        :type condition: Enum

        :return: a collection of Products in that condition
        :rtype: list

        """
        logger.info("Processing product query for %s ...", inventory_id)
        return cls.query.filter(cls.inventory_id==inventory_id)

    @classmethod
    def find_by_restock_level(cls, restock_level: Enum) -> list:
        """Returns all of the Products in a restock_level

        :param restock_level: the restock_level of the Products you want to match
        :type restock_level: Enum

        :return: a collection of Products in that restock_level
        :rtype: list

        """
        logger.info("Processing restock_level query for %s ...", restock_level)
        return cls.query.filter(cls.restock_level == restock_level)

    @classmethod
    def find_by_condition_and_restock_level(cls, condition,restock_level: Enum) -> list:
        """Returns all of the Products in a restock_level under a certain condition

        :param restock_level: the restock_level of the Products you want to match
        :param condition: the condition of the Products you want to match
        :type restock_level: Enum
        :type condition: Enum

        :return: a collection of Products in that restock_level
        :rtype: list

        """
        logger.info("Processing restock_level query for %s ...", restock_level)
        return cls.query.filter(cls.restock_level == restock_level, cls.condition == condition)


######################################################################
#  I N V E N T O R Y   M O D E L
######################################################################
class Inventory(db.Model, PersistentBase):
    """
    Class that represents a Inventory

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    products = db.relationship('Product', backref='inventory', passive_deletes=True, lazy=True)

    def __repr__(self):
        return f"<Inventory {self.name} id=[{self.id}]>"

    def serialize(self) -> dict:
        """ Serializes a Inventory into a dictionary """
        inventory = {
            "id": self.id,
            "name": self.name,
            "products": [],
            }
        for product in self.products:
            inventory["products"].append(product.serialize())
        return inventory

    def deserialize(self, data):
        """
        Deserializes a Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            # # handle inner list of products
            # product_data = data.get("products")

        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Inventory: body of request contained bad or no data" + str(error)
            )
        return self

    def create_product(self, data):
        """
        Create an Inventory item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        product = Product()
        product.deserialize(data)
        self.products.append(product)
        product.create()


    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_name(cls, name):
        """Returns all Inventories with the given name

        Args:
            name (string): the name of the Inventories you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    # @classmethod
    # def if_exists_by_name(cls, name):
    #     """Returns whether an inventory with the given name already created

    #     Args:
    #         name (string): the name of the Inventories you want to match
    #     """
    #     logger.info("Processing existence query for %s ...", name)
    #     return db.session.query(cls.query.filter(cls.name == name)).scalar()
