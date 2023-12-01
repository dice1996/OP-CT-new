function updateQuantity(button, change) {
    let row = button.closest('tr');
    let quantityCell = row.cells[1]; // Assuming the quantity cell is the second cell
    let locationId = quantityCell.id; // Extracting the location ID from the quantity cell

    // Disable all buttons in the row
    let buttons = row.querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = true);

    let productCodeElement = document.getElementById('productCode');
    let productCode = productCodeElement ? productCodeElement.innerText.trim() : null;

    if (!productCode) {
        console.error('Product code element not found');
        return;
    }

    if (!quantityCell) {
        console.error('Quantity cell not found');
        return;
    }

    let currentQuantity = parseInt(quantityCell.innerText, 10) || 0;
    let newQuantity = currentQuantity + change;

    // Send AJAX request to update quantity on the server
    $.ajax({
        url: '/api/update_quantity',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            productCode: productCode,
            location: locationId,
            currentQuantity: currentQuantity,
            newQuantity: newQuantity
        }),
        success: function (response) {
            // Update the quantity in the table
            quantityCell.innerText = response.new_quantity;
            highlightMaxQuantityRow();
            // Re-enable buttons
            buttons.forEach(btn => btn.disabled = false);
        },
        error: function (xhr, status, error) {
            console.error("Error - Status:", status, "Message:", xhr.responseText);
            highlightMaxQuantityRow();
            // Re-enable buttons
            buttons.forEach(btn => btn.disabled = false);
        }
    });
}