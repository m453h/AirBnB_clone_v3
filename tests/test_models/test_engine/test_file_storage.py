#!/usr/bin/python3
"""
Contains the TestFileStorageDocs classes
"""

from datetime import datetime
import inspect
import models
from models.engine import file_storage
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
FileStorage = file_storage.FileStorage
classes = {"Amenity": Amenity, "BaseModel": BaseModel, "City": City,
           "Place": Place, "Review": Review, "State": State, "User": User}


class TestFileStorageDocs(unittest.TestCase):
    """Tests to check the documentation and style of FileStorage class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.fs_f = inspect.getmembers(FileStorage, inspect.isfunction)

    def test_pep8_conformance_file_storage(self):
        """Test that models/engine/file_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/engine/file_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_file_storage(self):
        """Test tests/test_models/test_file_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_models/test_engine/\
test_file_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_file_storage_module_docstring(self):
        """Test for the file_storage.py module docstring"""
        self.assertIsNot(file_storage.__doc__, None,
                         "file_storage.py needs a docstring")
        self.assertTrue(len(file_storage.__doc__) >= 1,
                        "file_storage.py needs a docstring")

    def test_file_storage_class_docstring(self):
        """Test for the FileStorage class docstring"""
        self.assertIsNot(FileStorage.__doc__, None,
                         "FileStorage class needs a docstring")
        self.assertTrue(len(FileStorage.__doc__) >= 1,
                        "FileStorage class needs a docstring")

    def test_fs_func_docstrings(self):
        """Test for the presence of docstrings in FileStorage methods"""
        for func in self.fs_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestFileStorage(unittest.TestCase):
    """Test the FileStorage class"""
    @unittest.skipIf(models.storage_t == 'db', "not testing file storage")
    def test_all_returns_dict(self):
        """Test that all returns the FileStorage.__objects attr"""
        storage = FileStorage()
        new_dict = storage.all()
        self.assertEqual(type(new_dict), dict)
        self.assertIs(new_dict, storage._FileStorage__objects)

    @unittest.skipIf(models.storage_t == 'db', "not testing file storage")
    def test_new(self):
        """test that new adds an object to the FileStorage.__objects attr"""
        storage = FileStorage()
        save = FileStorage._FileStorage__objects
        FileStorage._FileStorage__objects = {}
        test_dict = {}
        for key, value in classes.items():
            with self.subTest(key=key, value=value):
                instance = value()
                instance_key = instance.__class__.__name__ + "." + instance.id
                storage.new(instance)
                test_dict[instance_key] = instance
                self.assertEqual(test_dict, storage._FileStorage__objects)
        FileStorage._FileStorage__objects = save

    @unittest.skipIf(models.storage_t == 'db', "not testing file storage")
    def test_save(self):
        """Test that save properly saves objects to file.json"""
        storage = FileStorage()
        new_dict = {}
        for key, value in classes.items():
            instance = value()
            instance_key = instance.__class__.__name__ + "." + instance.id
            new_dict[instance_key] = instance
        save = FileStorage._FileStorage__objects
        FileStorage._FileStorage__objects = new_dict
        storage.save()
        FileStorage._FileStorage__objects = save
        for key, value in new_dict.items():
            new_dict[key] = value.to_dict()
        string = json.dumps(new_dict)
        with open("file.json", "r") as f:
            js = f.read()
        self.assertEqual(json.loads(string), json.loads(js))


class TestFileStorageGetandCount(unittest.TestCase):
    """Test the FileStorage class get and count methods """
    @classmethod
    def setUpClass(cls):
        """ Set up for get and count methods """
        cls.storage = FileStorage()

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

    @unittest.skipIf(models.storage_t == 'db', "not testing db storage")
    def test_get_returns_obj(self):
        """Test that get() returns object with valid id"""
        state1 = self.storage.get(State, self.state.id)
        user1 = self.storage.get(User, self.user.id)
        place1 = self.storage.get(Place, self.place_1.id)

        self.assertEqual(user1.id, self.user.id)
        self.assertEqual(state1.id, self.state.id)
        self.assertEqual(place1.id, self.place_1.id)

    @unittest.skipIf(models.storage_t == 'db', "not testing db storage")
    def test_get_no_cls(self):
        """Test that get() returns None if id is not valid"""
        state1 = self.storage.get(State, "12345678")
        self.assertTrue(state1 is None)

    @unittest.skipIf(models.storage_t == 'db', "not testing db storage")
    def test_count_with_cls(self):
        """test that count() returns the number of objects
        based on given class"""
        num_amenity = self.storage.count(Amenity)
        self.assertTrue(type(num_amenity) == int)

    @unittest.skipIf(models.storage_t == 'db', "not testing db storage")
    def test_count_no_class(self):
        """Test that count returns number of all objects in storage"""
        num_objs = self.storage.count()
        self.assertTrue(type(num_objs) == int)

    @classmethod
    def tearDownClass(cls):
        """ Cleans up at the end of the unit tests """
        with open("file.json", "w") as file:
            file.write("{}")
        cls.storage.close()

    @unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                     "not testing file storage")
    def test_count(self):
        storage = FileStorage()
        initial_length = len(storage.all())
        self.assertEqual(storage.count(), initial_length)
        state_len = len(storage.all("State"))
        self.assertEqual(storage.count("State"), state_len)
        new_state_1 = State(name="California")
        new_state_1.save()
        new_state_2 = State(name="Iowa")
        new_state_2.save()
        self.assertEqual(storage.count(), initial_length + 2)
        self.assertEqual(storage.count("State"), state_len + 2)
