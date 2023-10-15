function highlightMaxQuantityRow() {
    let tableRows = document.querySelectorAll("tbody tr");
    let maxQuantity = -Infinity;
    let maxQuantityRows = [];

    // Prvo, počisti sve aktivne highlighte
    tableRows.forEach(row => {
        row.classList.remove("highlighted");
    });

    // Drugo, pronađi max količinu
    tableRows.forEach(row => {
        let quantityCell = row.lastElementChild;
        let quantityValue = parseInt(quantityCell.innerText, 10) || 0; // Default to 0 if NaN

        if (quantityValue > maxQuantity) {
            maxQuantity = quantityValue;
        }
    });

    // Ukoliko je max 0, ne obilježi  ništa
    if (maxQuantity === 0) {
        return;
    }

    // treći prolaz, zapiši redove koji imaju max količinu
    tableRows.forEach(row => {
        let quantityCell = row.lastElementChild;
        let quantityValue = parseInt(quantityCell.innerText, 10) || 0; // Default to 0 if NaN

        if (quantityValue === maxQuantity) {
            maxQuantityRows.push(row);
        }
    });

    // Obilježi polja s max količinom
    maxQuantityRows.forEach(row => {
        row.classList.add("highlighted");
    });
}