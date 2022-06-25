# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
import factory
from datetime import date
import random
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from service.models import Inventory, Product, Condition, Stock_Level


class ProductFactory(factory.Factory):
    """Create fake Product"""
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n)
    inventory_id = None
    condition = FuzzyChoice(choices=[Condition.NEW, Condition.OPEN_BOX, Condition.USED])
    restock_level = FuzzyChoice(choices=[Stock_Level.EMPTY, Stock_Level.LOW, Stock_Level.MODERATE, Stock_Level.PLENTY])
    quantity = FuzzyInteger(10, 5000)



class InventoryFactory(factory.Factory):
    """Creates fake inventory """

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    products = factory.RelatedFactoryList(ProductFactory, 
    factory_related_name='inventory_id', size=lambda: random.randint(1, 5))