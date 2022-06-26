"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

def init_db(app):
    """Initialize the SQLAlchemy app"""
    Inventory.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class Condition(Enum):
    """Enumeration of condition of a valid Inventory """

    NEW = 1
    OPEN_BOX = 2
    USED = 3
    UNKNOWN = 4

class Stock_Level(Enum):
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
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a record to the database
        """
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a record from the data store"""
        logger.info("Deleting %s", self.name)
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
        db.Enum(Stock_Level), nullable=False, server_default=(Stock_Level.EMPTY.name)
    )
    quantity = db.Column(db.Integer, nullable=False, default=0)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id', ondelete="CASCADE"), nullable=False)
    
    

    def __repr__(self):
        return "<Product %d id=[%s] inventory[%s]>" % (
            self.condition,
            self.id,
            self.inventory_id,
        )

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
            self.condition = getattr(Condition, data["condition"])  # create enum from string
            self.restock_level = getattr(Stock_Level, data["restock_level"])  # create enum from string
            self.quantity = data["quantity"]

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
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
        return "<Inventory %r id=[%s]>" % (
            self.name, 
            self.id,
            )

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
            # handle innter list of products
            product_list = data.get("products")
            for json_product in product_list:
                product = Product()
                product.deserialize(json_product)
                self.products.append(product)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Inventory: body of request contained bad or no data" + str(error)
            )
        return self


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
