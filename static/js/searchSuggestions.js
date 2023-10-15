let timeout = null;

document.getElementById('productQuery').addEventListener('keyup', function () {
    clearTimeout(timeout);

    // očisti prijedloge
    document.getElementById('suggestions').innerHTML = '';
    document.getElementById('suggestions').hidden = false;
    alertBox.innerHTML = "";

    // postavi timeout dok user ne završi sa upisivanjem
    timeout = setTimeout(function () {
        let query = document.getElementById('productQuery').value;
        if (query.length > 1) {
            $.ajax({
                url: "/api/product_suggestions",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({product_query: query}),
                success: function (data) {
                    let suggestionsDropdown = document.getElementById('suggestions');
                    data[0].products.forEach(product => {
                        let suggestionDiv = document.createElement('div');
                        suggestionDiv.tabIndex = 0; // Make the div focusable
                        suggestionDiv.innerHTML = product.product_name + ' (ID: ' + product.product_id + ', EAN: ' + product.barcode + ')';
                        suggestionDiv.onclick = function () {
                            selectProduct(product.product_name);
                            searchProduct();
                        };

                        suggestionsDropdown.appendChild(suggestionDiv);
                    });
                }
            });
        }
    }, 300);
});

function selectProduct(productName) {
    document.getElementById('productQuery').value = productName.replace('\t', '');
    document.getElementById('suggestions').hidden = true;
}