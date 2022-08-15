$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#inventory_inventory_id").val(res.inventory_id);
        $("#inventory_product_id").val(res.product_id);
        $("#inventory_condition").val(res.condition);
        $("#inventory_quantity").val(res.quantity);
        $("#inventory_restock_level").val(res.restock_level);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#inventory_inventory_id").val("");
        $("#inventory_product_id").val("");
        $("#inventory_condition").val("");
        $("#inventory_quantity").val("");
        $("#inventory_restock_level").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Inventory
    // ****************************************

    $("#create-btn").click(function () {

        let product_id = $("#inventory_product_id").val();
        let condition = $("#inventory_condition").val();
        let quantity = $("#inventory_quantity").val();
        let restock_level = $("#inventory_restock_level").val();

        let data = {
            "product_id": product_id,
            "condition": condition,
            "quantity": quantity,
            "restock_level": restock_level,
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/inventories",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Inventory
    // ****************************************

    $("#update-btn").click(function () {

        let inventory_id = $("#inventory_inventory_id").val();
        let product_id = $("#inventory_product_id").val();
        let condition = $("#inventory_condition").val();
        let quantity = $("#inventory_quantity").val();
        let restock_level = $("#inventory_restock_level").val();

        let data = {
            "product_id": product_id,
            "condition": condition,
            "quantity": quantity,
            "restock_level": restock_level,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/inventories/${inventory_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Inventory
    // ****************************************

    $("#retrieve-btn").click(function () {

        let inventory_id = $("#inventory_inventory_id").val();

        $("#flash_message").empty();

        let ajax;

        if (inventory_id == "") {
            ajax = $.ajax({
                type: "GET",
                url: `/api/inventories/${inventory_id}`,
                data: ''
            })
        } else {
            ajax = $.ajax({
                type: "GET",
                url: `/inventories/${inventory_id}`,
                contentType: "application/json",
                data: ''
            })
        }

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Inventory
    // ****************************************

    $("#delete-btn").click(function () {

        let inventory_id = $("#inventory_inventory_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/inventories/${inventory_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Inventory has been deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Delete all Inventories (Action)
    // ****************************************

    $("#deleteall-btn").click(function () {

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/inventories/clear`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            clear_form_data()
            $("#search_results").empty();
            flash_message("All Inventories have been deleted!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#inventory_inventory_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for an Inventory
    // ****************************************

    $("#search-btn").click(function () {

        let product_id = $("#inventory_product_id").val();
        let condition = $("#inventory_condition").val();
        let quantity = $("#inventory_quantity").val();
        let restock_level = $("#inventory_restock_level").val();

        let queryString = ""

        if (product_id) {
            queryString += 'product_id=' + product_id
        }
        if (condition) {
            if (queryString.length > 0) {
                queryString += '&condition=' + condition
            } else {
                queryString += 'condition=' + condition
            }
        }
        if (quantity) {
            if (queryString.length > 0) {
                queryString += '&quantity=' + quantity
            } else {
                queryString += 'quantity=' + quantity
            }
        }

        if (restock_level) {
            if (queryString.length > 0) {
                queryString += '&restock_level=' + restock_level
            } else {
                queryString += 'restock_level=' + restock_level
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/inventories?${queryString}`,
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Inventory_ID</th>'
            table += '<th class="col-md-2">Product_ID</th>'
            table += '<th class="col-md-2">Condition</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Restock_Level</th>'
            table += '</tr></thead><tbody>'
            let firstInventory = "";
            for(let i = 0; i < res.length; i++) {
                let inventory = res[i];
                table +=  
                    `<tr id="row_${i}"><td>
                    ${inventory.inventory_id}</td><td>
                    ${inventory.product_id}</td><td>
                    ${inventory.condition}</td><td>
                    ${inventory.quantity}</td><td>
                    ${inventory.restock_level}</td></tr>`;

                if (i == 0) {
                    firstInventory = inventory;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
