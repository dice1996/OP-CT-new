// funkcija dobiva kod proizvoda iz tablice
function getProductCode() {
    let productCodeElement = document.getElementById('productCode');
    return productCodeElement ? productCodeElement.innerText.trim() : null;
}

// funkcija dobiva trenutnu količinu određenog retka u tablici
function getCurrentQuantity(row) {
    let quantityCell = row.cells[1]; // Druga ćelija predstavlja količinu
    return parseInt(quantityCell.innerText, 10) || 0;
}

// Ova funkcija šalje AJAX zahtjev na server kako bi se ažurirala količina u dataframe-u
function updateQuantityOnServer(productCode, locationId, currentQuantity, newQuantity) {
    return $.ajax({
        url: '/api/update_quantity',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            productCode: productCode,
            location: locationId,
            currentQuantity: currentQuantity,
            newQuantity: newQuantity
        }),
    });
}

// Glavna funkcija koja hendla gumbe i ažuriranje količine
function handleQuantityUpdate(button, change) {
    let row = button.closest('tr');
    let quantityCell = row.cells[1]; // Druga ćelija predstavlja količinu
    let locationId = quantityCell.id; // Izvlačimo ID lokacije ze ćelije količine

    let currentQuantity = getCurrentQuantity(row);
    let newQuantity = currentQuantity + change;

    // Onemogućavamo sve gumbe u retku
    let buttons = row.querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = true);

    let productCode = getProductCode();

    if (!productCode) {
        console.error('Product code element not found');
        // Omogućavamo gumbe
        buttons.forEach(btn => btn.disabled = false);
        return;
    }

    // Šaljemo AJAX zahtjev na server kako bi se ažurirala količina
    updateQuantityOnServer(productCode, locationId, currentQuantity, newQuantity)
        .done(function (response) {
            // Ažuriramo količinu u tablici
            quantityCell.innerText = response.new_quantity;
            highlightMaxQuantityRow();
        })
        .fail(function (xhr, status, error) {
            console.error("Error - Status:", status, "Message:", xhr.responseText);
        })
        .always(function () {
            // Omogućavamo gumbe
            buttons.forEach(btn => btn.disabled = false);
        });
}