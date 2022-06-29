# NYU DevOps Inventory Project

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a ducumentation for the inventory services our team is going to build.

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── utils                  - utility package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── factory.py      - Factory for creating fake objects for testing
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## Database model and its APIs

### Database model

![Database model](/images/database_model.jpg)

```text
                          Persistent Base, SQLAlchemy
                                  /           \
  Product(db.model, Persistent Base)           Inventory(db.Model, Persistent Base) 
```

### APIs

This is the [documentation](/images/models.html) for the database models. It's located in the images folder. Please open it in a browser.

## Available REST API

### Create an Inventory

  Create an inventory with different product conditions, quantity and restock level.

* **Method:**

  `POST`

* **URL**

  `/inventories`  

* **Data Params**

  ```json
  {
    "name": "iphone5",
    "products": [
        {
          "condition": 1,
          "quantity": 12,
          "restock_level": 2
        },
        {
          "condition": 2,
          "quantity": 15,
          "restock_level": 1
        }
      ]
  }
  ```
  
* **Success Response:**

  * **Code:** 201 CREATED <br />
    **Content:**

    ```json
    {
      "id": 4879,
      "name": "iphone5",
      "products": 
        [
          {
            "condition": 1,
            "id": 469,
            "inventory_id": 4879,
            "quantity": 12,
            "restock_level": 2
          },
          {
            "condition": 2,
            "id": 470,
            "inventory_id": 4879,
            "quantity": 15,
            "restock_level": 1
          }
        ]
    }
    ```

* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />
    **Content:**

    ```json
    {
        "error": "Bad Request",
        "message": "400 Bad Request: The browser (or proxy) sent a request that this server could not understand.",
        "status": 400
    }
    ```

  OR

  * **Code:** 409 CONFLICT <br />
    **Content:**

    ```json
    {
        "error": "Bad Request",
        "message": "400 Bad Request: The browser (or proxy) sent a request that this server could not understand.",
        "status": 400
    }
    ```

### Read Inventories

  List all inventories with product information or read an inventory using given inventory ID or read a product using given inventory ID and product ID.

* **Method:**

  `GET`

* **URL**

  `/inventories`  

* **URL Params**

   **Optional:**

   `/<int:inventory_id>`

   `/<int:inventory_id>/products/<int:product_id>`
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:**

    `GET /inventories`

    List all Inventories with product information

    ```json
    [
      {
        "id": 4879,
        "name": "iphone5",
        "products": 
          [
            {
              "condition": 1,
              "id": 469,
              "inventory_id": 4879,
              "quantity": 12,
              "restock_level": 2
            },
            {
              "condition": 2,
              "id": 470,
              "inventory_id": 4879,
              "quantity": 15,
              "restock_level": 1
            }
          ]
      },
      {
        "id": 4881,
        "name": "iphone6",
        "products": [
            {
              "condition": 3,
              "id": 471,
              "inventory_id": 4881,
              "quantity": 12,
              "restock_level": 2
            },
            {
              "condition": 2,
              "id": 472,
              "inventory_id": 4881,
              "quantity": 15,
              "restock_level": 1
            }
          ]
      }
    ]
    ```

    OR

    `GET /inventories/4879`

    Read an inventory using given inventory ID

    ```json
    {
      "id": 4879,
      "name": "iphone5",
      "products": 
        [
          {
            "condition": 1,
            "id": 469,
            "inventory_id": 4879,
            "quantity": 12,
            "restock_level": 2
          },
          {
            "condition": 2,
            "id": 470,
            "inventory_id": 4879,
            "quantity": 15,
            "restock_level": 1
          }
        ]
    }
    ```

    OR

    `GET /inventories/4879/products/469`

    Read a product using given inventory ID and product ID

    ```json
    {
        "condition": 1,
        "id": 469,
        "inventory_id": 4879,
        "quantity": 12,
        "restock_level": 2
    }
    ```

* **Error Response:**

  * **Code:** 404 NOT FOUND <br />
    **Content:**

    ```json
    {
        "error": "Not Found",
        "message": "404 Not Found: Inventory with id '1' could not be found.",
        "status": 404
    }
    ```

### Update an Inventory

  Update an inventory or a product.

* **Method:**

  `PUT`

* **URL**

  `/inventories`  

* **URL Params**

   **Require:**
   `/<int:inventory_id>`

  **Optional:**
   `/<int:inventory_id>/products/<int:product_id>`

* **Data Params**

  Update Inventory

  ```json
  {
    "name": "iphone7",
  }
  ```

  OR

  Update Product

  ```json
  {
      "condition": 3,
      "id": 469,
      "inventory_id": 4879,
      "quantity": 12,
      "restock_level": 2
  }
  ```

* **Success Response:**

  * **Code:** 200 <br />
    **Content:**

    ```json
    {
      "id": 4879,
      "name": "iphone7",
      "products": 
        [
          {
            "condition": 1,
            "id": 469,
            "inventory_id": 4879,
            "quantity": 12,
            "restock_level": 2
          },
          {
            "condition": 2,
            "id": 470,
            "inventory_id": 4879,
            "quantity": 15,
            "restock_level": 1
          }
        ]
    }
    ```

* **Error Response:**

  * **Code:** 415 UNSUPPORTED MEDIA TYPE <br />
    **Content:**

    ```json
    {
        "error": "Unsupported media type",
        "message": "415 Unsupported Media Type: Inventory name was not provided.",
        "status": 415
    }
    ```

    OR

  * **Code:** 404 NOT FOUND <br />
    **Content:**

    ```json
    {
        "error": "Not Found",
        "message": "404 Not Found: Inventory with id '1' could not be found.",
        "status": 404
    }
    ```

### Remove an Inventory

  Remove an inventory

* **Method:**

  `DELETE`

* **URL**

  `/inventories`  

* **URL Params**

   **Require:**
   `/<int:inventory_id>`
  
* **Success Response:**

  * **Code:** 204 NO CONTENT <br />
    **Content:**

* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />

## Run the Test

```python
nosetests -v --with-spec --spec-color
```

Reference of design: https://github.com/nyu-devops/sample-accounts

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
