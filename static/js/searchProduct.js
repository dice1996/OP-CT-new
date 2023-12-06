function searchProduct() {
    let productQuery = document.getElementById('productQuery').value;
    $.ajax({
        url: "/api/product_quantities",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({product_query: productQuery}),
        success: function (data) {
            if (data[0].product_name) {
                let productName = data[0].product_name;
                const compareTo = "TIPKOVNICA WHITE SHARK GK-2103 MIKASA HR ROZA";

                if (productName.length > compareTo.length) {
                    const shortenBy = productName.length - compareTo.length + 3;
                    productName = productName.substring(0, productName.length - shortenBy) + "...";
                }

                document.getElementById('productNameDisplay').innerText = productName;
                document.getElementById('productCode').innerText = data[0].sifra;
                document.getElementById('productEAN').innerText = data[0].ean
                selectProduct(data[0].product_name);
            } else {
                const alertBox = document.getElementById('alertBox');
                alertBox.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show centered-content" role="alert">
                Proizvod nije pronađen ili nije na zalihi.
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>`;
            }
            // Ažuriraj količine za sve lokacije dinamički
            for (let location in data[0].quantities) {
                let quantityCell = document.getElementById(location);
                if (quantityCell) {
                    quantityCell.innerText = data[0].quantities[location];
                }
            }
            attachEventListeners();
            highlightMaxQuantityRow();

        },
        error: function () {
            const alertBox = document.getElementById('alertBox');
            alertBox.innerHTML = '<div class="alert alert-danger" role="alert">Proizvod nije pronađen.</div>';
        }
    });
}

function attachEventListeners() {
    // Remove existing event listeners to avoid duplicates
    $('.update-button-plus, .update-button-minus').off('click');

    // Attach new event listeners
    $('.update-button-plus').on('click', function() {
        handleQuantityUpdate(this, 1);
    });

    $('.update-button-minus').on('click', function() {
        handleQuantityUpdate(this, -1);
    });
}
