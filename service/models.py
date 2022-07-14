"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from enum import IntEnum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError, StatementError

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Inventory.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class DuplicateKeyValueError(Exception):
    """Used for inserting records with duplicate keys error in create() function"""


class Condition(IntEnum):
    """Enumeration of condition of a valid Inventory"""

    NEW = 1
    OPEN_BOX = 2
    USED = 3
    UNKNOWN = 4


class StockLevel(IntEnum):
    """Enumeration of StockLevel of a valid Inventory"""

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
        # id must be none to generate next primary key
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            error = str(e.orig)
            db.session.rollback()
            if "duplicate key value violates unique constraint" in error:
                raise DuplicateKeyValueError(
                    "duplicate key value violates unique constraint unique_constraint_productid_condition"
                )
        except (DataError, StatementError) as data_error:
            db.session.rollback()
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data"
                + str(data_error.args[0])
            ) from data_error

    def update(self):
        """
        Updates a record to the database
        """
        logger.info("Updating %s", self.inventory_id)
        db.session.commit()

    def delete(self):
        """Removes a record from the data store"""
        logger.info("Deleting inventory_id:%s" % self.inventory_id)
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

######################################################################
#  I N V E N T O R Y   M O D E L
######################################################################


class Inventory(db.Model, PersistentBase):
    """
    Class that represents a Inventory

    Provide a one-to-one relationship between an inventory and its product_id,condition,
    restock level and number.
    """
    # app = None
    # __tablename__ = "inventory"
    product_id = db.Column(db.Integer, nullable=False)
    condition = db.Column(
        db.Enum(Condition), nullable=False,
        server_default=(Condition.UNKNOWN.name)
    )

    restock_level = db.Column(
        db.Enum(StockLevel), nullable=False, server_default=(StockLevel.EMPTY.name)
    )

    quantity = db.Column(db.Integer, nullable=False, default=0)
    inventory_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'condition', name='unique_constraint_productid_condition'),
    )

    def __repr__(self):
        return (f"<Inventory_id = [{self.inventory_id}]"
                f"condition=[{Condition(self.condition).name}]"
                f"product_id[{self.product_id}]"
                # f"inventory[{self.inventory_id}]"
                f"Product quantity=[{StockLevel(self.restock_level).name}]>")

    def serialize(self) -> dict:
        """Serializes a Inventory into a dictionary"""
        return {
            "inventory_id": self.inventory_id,
            "condition": self.condition,
            "product_id": self.product_id,
            "restock_level": self.restock_level,
            "quantity": self.quantity
            }

    def deserialize(self, data):
        """
        Deserializes a Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.condition = data["condition"]  # create enum from string
            self.restock_level = data["restock_level"]  # create enum from string
            self.quantity = data["quantity"]

        except KeyError as key_error:
            raise DataValidationError(
                "Invalid Inventory: missing " + key_error.args[0]
            ) from key_error
        except TypeError as type_error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data"
                + str(type_error)
            ) from type_error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_condition(cls, condition: IntEnum) -> list:
        """Returns all of the Products in a condition

        :param condition: the condition of the Products you want to match
        :type condition: Enum

        :return: a collection of Products in that condition
        :rtype: list

        """
        logger.info("Processing condition query for %s ...", condition)
        return cls.query.filter(cls.condition == condition)

    # @classmethod
    # def find_by_inventory_id(cls, inventory_id) -> list:
    #     """Returns all of the Products in a condition

    #     :param condition: the condition of the Products you want to match
    #     :type condition: Enum

    #     :return: a collection of Products in that condition
    #     :rtype: list

    #     """
    #     logger.info("Processing product query for %s ...", inventory_id)
    #     return cls.query.filter(cls.inventory_id == inventory_id)

    @classmethod
    def find_by_restock_level(cls, restock_level: IntEnum) -> list:
        """Returns all of the Products in a restock_level

        :param restock_level: the restock_level of the Products you want to match
        :type restock_level: Enum

        :return: a collection of Products in that restock_level
        :rtype: list

        """
        logger.info("Processing restock_level query for %s ...", restock_level)
        return cls.query.filter(cls.restock_level == restock_level)

    @classmethod
    def find_by_condition_and_restock_level(
        cls, condition, restock_level: IntEnum
    ) -> list:
        """Returns all of the Products in a restock_level under a certain condition

        :param restock_level: the restock_level of the Products you want to match
        :param condition: the condition of the Products you want to match
        :type restock_level: Enum
        :type condition: Enum

        :return: a collection of Products in that restock_level
        :rtype: list

        """
        logger.info("Processing restock_level query for %s ...", restock_level)
        return cls.query.filter(
            cls.restock_level == restock_level, cls.condition == condition
        )
#     ##################################################
#     # CLASS METHODS
#     ##################################################

#     @classmethod
#     def find_by_name(cls, name):
#         """Returns all Inventories with the given name

#         Args:
#             name (string): the name of the Inventories you want to match
#         """
#         logger.info("Processing name query for %s ...", name)
#         return cls.query.filter(cls.name == name)

#     # @classmethod
#     # def if_exists_by_name(cls, name):
#     #     """Returns whether an inventory with the given name already created

#     #     Args:
#     #         name (string): the name of the Inventories you want to match
#     #     """
#     #     logger.info("Processing existence query for %s ...", name)
#     #     return db.session.query(cls.query.filter(cls.name == name)).scalar()
