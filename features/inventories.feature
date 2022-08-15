Feature: The inventory service back-end
    As a Inventory Manager
    I need a RESTful catalog service
    So that I can keep track of all inventories

Background:
    Given the following inventories
        | product_id | condition | quantity | restock_level | 
        | 1          | NEW       | 1        | LOW           |
        | 1          | OPEN_BOX  | 2        | MODERATE      | 
        | 2          | NEW       | 3        | MODERATE      | 
        | 3          | USED      | 4        | PLENTY        |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all inventories 
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "4" rows in the results
    And I should see "1" "NEW" "1" and "LOW" in the "1st" row of the results
    And I should see "1" "OPEN_BOX" "2" and "MODERATE" in the "2nd" row of the results
    And I should see "2" "NEW" "3" and "MODERATE" in the "3rd" row of the results
    And I should see "3" "USED" "4" and "PLENTY" in the "4th" row of the results

Scenario: Create a New inventory
    When I visit the "Home Page"
    And I set the "Product Id" to "4"
    And I select "NEW" in the "Condition" dropdown
    And I set the "Quantity" to "5"
    And I select "MODERATE" in the "Restock Level" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "5" rows in the results
    And I should see "4" "NEW" "5" and "MODERATE" in the "5st" row of the results

Scenario: Query/Filter the inventory
    When I visit the "Home Page"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "2" rows in the results
    And I should see "1" "NEW" "1" and "LOW" in the "1st" row of the results
    And I should see "2" "NEW" "3" and "MODERATE" in the "2rd" row of the results
    When I press the "Clear" button
    And I select "MODERATE" in the "Restock Level" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "2" rows in the results
    And I should see "1" "OPEN_BOX" "2" and "MODERATE" in the "1st" row of the results
    And I should see "2" "NEW" "3" and "MODERATE" in the "2st" row of the results

Scenario: Read a inventory
    When I visit the "Home Page"
    And I paste the "Inventory ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "3" in the "Product Id" field
    And I should see "USED" in the "Condition" dropdown
    And I should see "PLENTY" in the "Restock Level" dropdown
    And I should see "4" in the "Quantity" field
    When I press the "Clear" button
    And I set the "Inventory ID" to "10000"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Inventory with id '10000' could not be found."
    When I press the "Clear" button
    And I press the "Retrieve" button
    Then I should see " " in the "Product Id" field
    And I should see " " in the "Quantity" field

Scenario: Update an Inventory
    When I visit the "Home Page"
    And I set the "Product Id" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" in the "Product Id" field
    And I should see "NEW" in the "Condition" dropdown
    And I should see "LOW" in the "Restock Level" dropdown
    When I select "MODERATE" in the "Restock Level" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Inventory ID" field
    And I press the "Clear" button
    And I paste the "Inventory ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "MODERATE" in the "Restock Level" dropdown
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" "NEW" "1" and "MODERATE" in the "4st" row of the results
    When I press the "Clear" button
    And I set the "Product Id" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" in the "Product Id" field
    And I should see "NEW" in the "Condition" dropdown
    When I select "USED" in the "Condition" dropdown
    And I press the "Update" button
    Then I should see the message "Invalid Product: product_id or condition should not be updated"
    When I press the "Clear" button
    And I paste the "Inventory ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "1" in the "Product Id" field
    And I should see "NEW" in the "Condition" dropdown


Scenario: Delete all inventories
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "4" rows in the results
    And I should see "1" "NEW" "1" and "LOW" in the "1st" row of the results
    And I should see "1" "OPEN_BOX" "2" and "MODERATE" in the "2nd" row of the results
    And I should see "2" "NEW" "3" and "MODERATE" in the "3rd" row of the results
    And I should see "3" "USED" "4" and "PLENTY" in the "4th" row of the results

    When I press the "Clear" button
    And I set the "Product_id" to "1"
    And I select "OPEN BOX" in the "Condition" dropdown
    When I press the "Delete All" button
    Then I should see the message "Inventories have been deleted!"
    When I press the "Search" button
    Then I should see the message "Success"
    And I should see "3" rows in the results
    And I should see "1" "NEW" "1" and "LOW" in the "1st" row of the results
    And I should see "2" "NEW" "3" and "MODERATE" in the "2nd" row of the results
    And I should see "3" "USED" "4" and "PLENTY" in the "3rd" row of the results

    When I press the "Clear" button
    And I select "NEW" in the "Condition" dropdown
    When I press the "Delete All" button
    Then I should see the message "Inventories have been deleted!"
    When I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" rows in the results
    And I should see "3" "USED" "4" and "PLENTY" in the "1st" row of the results

    When I press the "Clear" button
    When I press the "Delete All" button
    Then I should see the message "Inventories have been deleted!"
    When I press the "Search" button
    Then I should see the message "Success"
    And I should not see anything in the results

Scenario: Delete an inventory
    When I visit the "Home Page" 
    And I set the "Product_id" to "1"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" in the "Product Id" field
    And I should see "NEW" in the "Condition" dropdown
    And I should see "LOW" in the "Restock Level" dropdown
    When I copy the "Inventory_id" field
    When I press the "Delete" button
    Then I should see the message "Inventory has been deleted!"

    When I paste the "Inventory_id" field
    And I press the "Retrieve" button
    Then I should see the message containing "404 Not Found"