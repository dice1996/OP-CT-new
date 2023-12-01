function highlightMaxQuantityRow() {
    let tableRows = document.querySelectorAll("tbody tr");
    let maxQuantity = -Infinity;
    let maxQuantityRows = [];

    tableRows.forEach(row => {
        row.classList.remove("highlighted");
        let quantityCell = isAdmin ? row.cells[row.cells.length - 2] : row.lastElementChild;

        if (quantityCell) { // Check if quantityCell is not undefined
            let quantityValue = parseInt(quantityCell.innerText, 10) || 0;

            if (quantityValue > maxQuantity) {
                maxQuantity = quantityValue;
            }
        }
    });

    if (maxQuantity === 0) {
        return;
    }

    tableRows.forEach(row => {
        let quantityCell = isAdmin ? row.cells[row.cells.length - 2] : row.lastElementChild;

        if (quantityCell) {
            let quantityValue = parseInt(quantityCell.innerText, 10) || 0;

            if (quantityValue === maxQuantity) {
                maxQuantityRows.push(row);
            }
        }
    });

    maxQuantityRows.forEach(row => {
        row.classList.add("highlighted");
    });
}
