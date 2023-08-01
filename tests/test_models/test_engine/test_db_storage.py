#!/usr/bin/python3
"""
Contains the TestDBStorageDocs and TestDBStorage classes
"""

from datetime import datetime
import inspect
import models
from models.engine import db_storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
import json
import os
import pep8
import unittest
DBStorage = db_storage.DBStorage
classes = {"Amenity": Amenity, "City": City, "Place": Place,
           "Review": Review, "State": State, "User": User}

HBNB_MYSQL_USER = os.getenv('HBNB_MYSQL_USER')
HBNB_MYSQL_PWD = os.getenv('HBNB_MYSQL_PWD')
HBNB_MYSQL_HOST = os.getenv('HBNB_MYSQL_HOST')
HBNB_MYSQL_DB = os.getenv('HBNB_MYSQL_DB')
HBNB_ENV = os.getenv('HBNB_ENV')


class TestDBStorageDocs(unittest.TestCase):
    """Tests to check the documentation and style of DBStorage class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.dbs_f = inspect.getmembers(DBStorage, inspect.isfunction)

    def test_pep8_conformance_db_storage(self):
        """Test that models/engine/db_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/engine/db_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_db_storage(self):
        """Test tests/test_models/test_db_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_models/test_engine/\
test_db_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_db_storage_module_docstring(self):
        """Test for the db_storage.py module docstring"""
        self.assertIsNot(db_storage.__doc__, None,
                         "db_storage.py needs a docstring")
        self.assertTrue(len(db_storage.__doc__) >= 1,
                        "db_storage.py needs a docstring")

    def test_db_storage_class_docstring(self):
        """Test for the DBStorage class docstring"""
        self.assertIsNot(DBStorage.__doc__, None,
                         "DBStorage class needs a docstring")
        self.assertTrue(len(DBStorage.__doc__) >= 1,
                        "DBStorage class needs a docstring")

    def test_dbs_func_docstrings(self):
        """Test for the presence of docstrings in DBStorage methods"""
        for func in self.dbs_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestDBStorageMethods(unittest.TestCase):
    """Test the DBStorage class"""
    @classmethod
    def setUpClass(cls):
        """ Set up for get and count methods """
        cls.storage = DBStorage()
        cls.storage.connect(host=HBNB_MYSQL_HOST,
                            user=HBNB_MYSQL_USER,
                            password=HBNB_MYSQL_PWD,
                            database=HBNB_MYSQL_DB)
        Base.metadata.create_all(cls.storage._DBStorage__engine)

        cls.state = State(name="California")
        cls.state.save()

        cls.city = City(state_id=cls.state.id, name="San Francisco")
        cls.city.save()

        cls.user = User(email="john@snow.com", password="johnpwd")
        cls.user.save()

        cls.place_1 = Place(user_id=cls.user.id,
                            city_id=cls.city.id, name="House 1")
        cls.place_1.save()
        cls.place_2 = Place(user_id=cls.user.id,
                            city_id=cls.city.id, name="House 2")
        cls.place_2.save()

        cls.amenity_1 = Amenity(name="Wifi")
        cls.amenity_1.save()
        cls.amenity_2 = Amenity(name="Cable")
        cls.amenity_2.save()
        cls.amenity_3 = Amenity(name="Oven")
        cls.amenity_3.save()

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_get_returns_obj(self):
        """Test that get() returns object with valid id"""
        state1 = self.storage.get(State, self.state.id)
        user1 = self.storage.get(User, self.user.id)
        place1 = self.storage.get(Place, self.place_1.id)

        self.assertEqual(user1.id, self.user.id)
        self.assertEqual(state1.id, self.state.id)
        self.assertEqual(place1.id, self.place_1.id)

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_get_no_cls(self):
        """Test that get() returns None if id is not valid"""
        state1 = self.storage.get(State, "12345678")
        self.assertTrue(state1 is None)

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_count_with_cls(self):
        """test that count() returns the number of objects
        based on given class"""
        num_amenity = self.storage.count(Amenity)
        self.assertTrue(num_amenity == 3)

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_count_no_class(self):
        """Test that count returns number of all objects in storage"""
        num_objs = self.storage.count()
        self.assertTrue(num_objs == 8)

    @classmethod
    def tearDownClass(cls):
        """ Cleans up at the end of the unit tests """
        cls.storage.close()
