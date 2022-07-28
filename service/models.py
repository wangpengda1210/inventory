"""
Models for Inventory

All of the models are stored in this module
"""
from itertools import product
import logging
from enum import IntEnum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError, StatementError
from . import app

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Inventory.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class DuplicateKeyValueError(Exception):
    """
    Used for inserting records with
    duplicate keys error in create() function"""


class Condition(IntEnum):
    """Enumeration of condition of a valid Inventory"""

    NEW = 1
    OPEN_BOX = 2
    USED = 3
    UNKNOWN = 4


class RestockLevel(IntEnum):
    """Enumeration of RestockLevel of a valid Inventory"""

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
                    "duplicate key value violates unique "
                    "constraint unique_constraint_product_id_condition"
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

    Provide a one-to-one relationship between an inventory and
    its product_id, condition, restock level and number.
    """
    # app = None
    # __tablename__ = "inventory"
    product_id = db.Column(db.Integer, nullable=False)
    condition = db.Column(
        db.Enum(Condition), nullable=False,
        server_default=(Condition.UNKNOWN.name)
    )

    restock_level = db.Column(
        db.Enum(RestockLevel), nullable=False,
        server_default=(RestockLevel.EMPTY.name)
    )

    quantity = db.Column(db.Integer, nullable=False, default=0)
    inventory_id = db.Column(
        db.Integer, autoincrement=True,
        primary_key=True, nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            'product_id', 'condition',
            name='unique_constraint_product_id_condition'
        ),
    )

    def __repr__(self):
        return (f"<Inventory_id = [{self.inventory_id}]"
                f"condition=[{self.condition}]"
                f"product_id[{self.product_id}]"
                f"quantity=[{self.quantity}]"
                f"restock_level=[{self.restock_level}]>")

    def serialize(self) -> dict:
        """Serializes a Inventory into a dictionary"""
        return {
            "inventory_id": self.inventory_id,
            "condition": self.condition.name,
            "product_id": self.product_id,
            "restock_level": self.restock_level.name,
            "quantity": self.quantity
            }

    def deserialize(self, data):
        """
        Deserializes a Inventory from a dictionary

        :param data: A dictionary containing the resource data
        :type data: dict
        """
        try:
            self.product_id = data["product_id"]
            self.condition = data["condition"]  # create enum from string
            self.restock_level = data.get(
                "restock_level", self.restock_level)  # create enum from string
            self.quantity = data.get("quantity", self.quantity)

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

    def update(self, data):
        """Update an Inventory from a dictionary
           while checking for bad cases when
           product_id or condition are being
           updated.

        :param data: A dictionary containing the resource data
        :type data: dict
        """
        condition = data["condition"] if isinstance(data["condition"], int) else Condition[data["condition"]].value
        if self.product_id != data["product_id"] or \
           self.condition != condition:
            raise DataValidationError(
                "Invalid Product: product_id or "
                "condition should not be updated"
            )
        self.deserialize(data)
        return super().update()

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

    @classmethod
    def find_by_attributes(cls, req_dict) -> list:
        """Returns all of the products correspond to given request parameters

        :param req_dict: dictionary of request parameters
        :type req_dict: MultiDict

        :return: a collection of products
        correspond to given request parameters
        :rtype: list
        """
        app.logger.info(
            "Processing query with parameters %s ...", str(req_dict))
        filter_list = []

        # Add query parameters into filter list,
        # ignore invalid params and illegal values
        for attr in ['condition', 'restock_level', 'quantity', 'product_id']:
            value = req_dict.get(attr)
            if value:
                try:
                    if attr == 'condition':
                        value = Condition(int(value))
                    elif attr == 'restock_level':
                        value = RestockLevel(int(value))
                    else:
                        value = int(value)
                    filter_list.append(getattr(cls, attr) == value)
                except ValueError:
                    app.logger.info('Ignore invalid %s: %s', attr, value)

        return cls.query.filter(*filter_list)

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

        :param restock_level: the target restock_level
        :type restock_level: IntEnum

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

        :param restock_level: the target restock_level of the Products
        :param condition: the target condition of the Products
        :type restock_level: IntEnum
        :type condition: IntEnum

        :return: a collection of Products in that restock_level
        :rtype: list

        """
        logger.info("Processing restock_level query for %s ...", restock_level)
        return cls.query.filter(
            cls.restock_level == restock_level, cls.condition == condition
        )
