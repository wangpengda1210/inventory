# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

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

  Returns json data about a single user.

* **Method:**

  `POST`

* **URL**

  `/inventories`  

* **Data Params**
  {
    "id": 28,
    "name": "Nicole",
    "products": [
        {
            "id": 108,
            "condition": 3,
            "restock_level": 0,
            "quantity": 3910,
            "inventory_id": 0
        }
    ]
}
  
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ id : 12, name : "Michael Bloom" }`
 
* **Error Response:**

  * **Code:** 404 NOT FOUND <br />
    **Content:** `{ error : "User doesn't exist" }`

  OR

  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** `{ error : "You are unauthorized to make this request." }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/users/1",
      dataType: "json",
      type : "GET",
      success : function(r) {
        console.log(r);
      }
    });
  ```

Reference of design: https://github.com/nyu-devops/sample-accounts


## License
Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
