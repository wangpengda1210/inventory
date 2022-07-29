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
    And I should see "1" "NEW" "1" and "LOW" in the "1st" row of the results
    And I should see "1" "OPEN_BOX" "2" and "MODERATE" in the "2nd" row of the results
    And I should see "2" "NEW" "3" and "MODERATE" in the "3rd" row of the results
    And I should see "3" "USED" "4" and "PLENTY" in the "4th" row of the results
