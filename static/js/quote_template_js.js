function calculateTotal() {
    let quantities = document.querySelectorAll('input[name="quantity[]"]');
    let prices = document.querySelectorAll('input[name="price[]"]');
    let discounts = document.querySelectorAll('input[name="rabat[]"]');
    let total = 0;
    let totalDiscount = 0;

    for (let i = 0; i < quantities.length; i++) {
        quantities[i].value = quantities[i].value.replace(',', '.');
        prices[i].value = prices[i].value.replace(',', '.');
        discounts[i].value = discounts[i].value.replace(',', '.');

        let quantity = parseFloat(quantities[i].value) || 0;
        let price = parseFloat(prices[i].value) || 0;
        let discount = parseFloat(discounts[i].value) || 0;

        let discountedPrice = price - (price * discount / 100);
        let lineTotal = quantity * discountedPrice;

        total += lineTotal;
        totalDiscount += (price - discountedPrice) * quantity;
    }

    let amountExcludingTax = total / 1.25;
    let tax = total - amountExcludingTax;
    let grandTotal = total;

    document.getElementById('totalAmount').innerText = amountExcludingTax.toFixed(2);
    document.getElementById('taxAmount').innerText = tax.toFixed(2);
    document.getElementById('grandTotalAmount').innerText = grandTotal.toFixed(2);
    document.getElementById('discountAmount').innerText = totalDiscount.toFixed(2);  // Update discount amount
}

function addProduct() {
    let table = document.getElementById("productTable").getElementsByTagName('tbody')[0];
    let newRow = table.insertRow();
    let cells = ['Product ID', 'Product Name', 'Quantity', 'Price', 'Rabat', 'Note'];
    for (let i = 0; i < cells.length; i++) {
        let cell = newRow.insertCell(i);
        let input = document.createElement("input");
        if (cells[i] === 'Quantity' || cells[i] === 'Price' || cells[i] === 'Rabat') {
            input.style.width = '100px';
            cell.style.textAlign = 'center';
        }
        if (cells[i] === 'Product ID') {
            input.style.width = '150px';
        }
        if (cells[i] === 'Product Name') {
            input.style.width = '400px';
        }
        if (cells[i] === 'Rabat') {
            input.readOnly = false;  // Make the "Rabat" field read-only
        }
        input.type = "text";
        input.className = "form-control";
        input.name = cells[i].toLowerCase().replace(' ', '_') + '[]';
        input.addEventListener('input', calculateTotal);
        cell.appendChild(input);
    }

    // Add a "Remove" button at the end of the row
    let removeCell = newRow.insertCell(cells.length);
    let removeButton = document.createElement("button");
    removeButton.innerHTML = '<i class="fa fa-trash"></i>';
    removeButton.className = 'btn btn-danger';
    removeButton.onclick = function () {
        newRow.remove();
        calculateTotal();
    };
    removeCell.appendChild(removeButton);

    calculateTotal();
}

function addShippingCost() {
    let table = document.getElementById("productTable").getElementsByTagName('tbody')[0];
    let newRow = table.insertRow();
    let cells = ['Product ID', 'Product Name', 'Quantity', 'Price', 'Rabat', 'Note'];
    let predefinedValues = ['15461', 'TROŠKOVI DOSTAVE DO PRVE PREPREKE', '1', '5.57', '', ''];

    for (let i = 0; i < cells.length; i++) {
        let cell = newRow.insertCell(i);
        let input = document.createElement("input");
        if (cells[i] === 'Quantity' || cells[i] === 'Price' || cells[i] === 'Rabat') {
            input.style.width = '100px';
            cell.style.textAlign = 'center';
        }
        if (cells[i] === 'Product ID') {
            input.style.width = '150px';
        }
        if (cells[i] === 'Product Name') {
            input.style.width = '400px';
        }
        if (cells[i] === 'Rabat') {
            input.readOnly = false;  // Make the "Rabat" field read-only
        }
        input.type = "text";
        input.className = "form-control";
        input.name = cells[i].toLowerCase().replace(' ', '_') + '[]';
        input.value = predefinedValues[i];
        input.addEventListener('input', calculateTotal);
        cell.appendChild(input);
    }
    // Add a "Remove" button at the end of the row
    let removeCell = newRow.insertCell(cells.length);
    let removeButton = document.createElement("button");
    removeButton.innerHTML = '<i class="fa fa-trash"></i>';
    removeButton.className = 'btn btn-danger';
    removeButton.onclick = function () {
        newRow.remove();
        calculateTotal();
    };
    removeCell.appendChild(removeButton);

    calculateTotal();
}

$(document).ready(function () {
    $("form").on("submit", function (event) {
        event.preventDefault();
        var createOfferButton = $("#createOfferButton");

        createOfferButton.prop("disabled", true).text("U obradi...");

        $.ajax({
            url: '/create_quote',
            method: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                // Handle success
                console.log("Quote created with ID: " + response.quote_id);

                // Download PDF
                var pdf_base64 = response.pdf_base64;
                var pdf_blob = new Blob([new Uint8Array(atob(pdf_base64).split("").map(function (char) {
                    return char.charCodeAt(0);
                }))], {type: 'application/pdf'});
                var pdf_url = URL.createObjectURL(pdf_blob);
                var pdf_link = document.createElement('a');
                pdf_link.href = pdf_url;
                pdf_link.download = response.quote_id + '.pdf';
                document.body.appendChild(pdf_link);
                pdf_link.click();
                document.body.removeChild(pdf_link);

                createOfferButton.prop("disabled", false).text("Kreiraj ponudu");
                refreshOffersTable()

            },
            error: function (error) {
                createOfferButton.prop("disabled", false).text("Kreiraj ponudu");

                // Handle error
                console.log("Error:", error);
            }
        });
    });
});

$(document).ready(function () {
    // Delete row button
    $(".offer-table").on("click", "button.delete-button", function () {
        var row = $(this).closest("tr");
        var row_id = row.data("row-id");

        // Show confirmation popup
        var isConfirmed = confirm("Stvarno želiš obrisati ovu ponudu?");

        if (isConfirmed) {
            // Make an AJAX request to delete the row
            $.ajax({
                url: '/quote/' + row_id,
                type: 'DELETE',
                success: function (response) {
                    row.remove();  // This will remove the row from the table
                    refreshOffersTable();
                },
                error: function (error) {
                    console.log("Error:", error);
                    refreshOffersTable();
                }
            });
        }
    });

    $('.offer-table tbody').on('click', '.download-button', function () {
        const row = $(this).closest('tr');
        const quote_id = row.data('row-id');  // Assuming the row has an attribute `data-row-id` containing the quote ID

        // Disable the button and maybe change its text or add a spinner
        const btn = $(this);
        btn.prop('disabled', true);
        btn.html('<i class="fa fa-spinner fa-spin"></i>');

        // Make an AJAX GET request to download the PDF
        $.ajax({
            url: `/download/${quote_id}`,
            method: 'GET',
            xhrFields: {
                responseType: 'blob'  // to handle binary data
            },
            success: function (blob, status, xhr) {
                // Create a link element, and set its attributes
                let link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                // Try to get filename from response headers
                let contentDisposition = xhr.getResponseHeader('Content-Disposition') || '';
                let matches = /filename=([^;]+)/ig.exec(contentDisposition);
                let filename = (matches && matches[1]) ? matches[1] : `ponuda_${quote_id}.pdf`;

                link.download = filename;

                // This will download the PDF when the link is clicked
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                btn.prop('disabled', false);
                btn.html('<i class="fa fa-download"></i>');
            },
            error: function (err) {
                btn.prop('disabled', false);
                btn.html('<i class="fa fa-download"></i>');
                alert("An error occurred: " + err);
            }
        });
    });

    // Load offer button
    $(".offer-table").on("click", "button.load-button", function () {
        var row = $(this).closest("tr");
        var row_id = row.data("row-id");

        $('#row_id').val(row_id);

        // Make an AJAX request to fetch the quote details
        $.ajax({
            url: '/quote/' + row_id,
            type: 'GET',
            success: function (response) {
                // Populate the form fields
                $("input[name='customer_name']").val(response.customer.name);
                $("input[name='customer_oib']").val(response.customer.oib);
                $("input[name='customer_address']").val(response.customer.address);
                $("input[name='customer_phone']").val(response.customer.phone);
                $("input[name='customer_email']").val(response.customer.email);

                // Clear existing product rows
                $("#productTable tbody").empty();

                // Populate products (you'll need to adapt this to your specific requirements)
                response.products.forEach(function (product) {
                    addProduct();
                    let newRow = $("#productTable tbody tr:last");
                    newRow.find("input[name='product_id[]']").val(product.product_id);
                    newRow.find("input[name='product_name[]']").val(product.product_name);
                    newRow.find("input[name='quantity[]']").val(product.quantity);
                    newRow.find("input[name='price[]']").val(product.price);
                    newRow.find("input[name='rabat[]']").val(product.discount);
                    newRow.find("input[name='note[]']").val(product.note);
                });

                // Populate other fields like 'napomena'
                $("textarea[name='napomena']").val(response.napomena);

                // Recalculate total
                calculateTotal();
            },
            error: function (error) {
                // Handle error
                console.log("Error:", error);
                refreshOffersTable();
            }
        });
    });

    $("#clearFormButton").click(function () {
        // Clear customer data
        $('input[name="customer_name"]').val('');
        $('input[name="customer_oib"]').val('');
        $('input[name="customer_address"]').val('');
        $('input[name="customer_phone"]').val('');
        $('input[name="customer_email"]').val('');

        // Clear products data by removing all rows
        $("#productTable tbody tr").remove();

        // Clear any additional fields like 'napomena'
        $('#napomena').val('');

        // Clear totals
        $('#totalAmount').text('0.00');
        $('#taxAmount').text('0.00');
        $('#discountAmount').text('0.00');
        $('#grandTotalAmount').text('0.00');

        // Optionally, remove hidden field for row_id if you are using it
        $('input[name="row_id"]').val('');

    });
});

function refreshOffersTable() {
    $.ajax({
            url: '/quote/update', // Replace with your actual API endpoint
            method: 'GET',
            success: function (response) {
                console.log(response);
                // Destroy the existing DataTable instance if it exists
                if ($.fn.DataTable.isDataTable('.offer-table')) {
                    $('.offer-table').DataTable().destroy();
                }
                // Clear the table body
                const tableBody = $('.offer-table tbody');
                tableBody.empty(); // Clear existing rows

                response.forEach(offer => {
                    const row = `<tr data-row-id="${offer.row_id}">
                        <td>${offer.customer_name}</td>
                        <td style="width: 17%;">${offer.id}</td>
                        <td>${offer.total_amount}€</td>
                        <td style="width: 18%;">
                            <button type="button" class="btn btn-primary load-button" title="Učitaj"><i class="fa fa-folder-open"></i></button>
                            <button type="button" class="btn btn-success download-button" title="Preuzmi"><i class="fa fa-download"></i></button>
                            <button type="button" class="btn btn-danger delete-button" title="Obriši"><i class="fa fa-trash"></i></button>
                        </td>
                    </tr>`;
                    tableBody.append(row);
                });

                setTimeout(reinitializeDataTable, 0);

            }, error: function (error) {
                console.log("Error:", error);
            }
        }
    );
}

function reinitializeDataTable() {
    $('.offer-table').DataTable({
        "order": [[1, "desc"]],
        "language": {
            "search": "Pretraga:",
            "lengthMenu": "Prikaz _MENU_ ponuda",
            "info": "Prikazano _START_ do _END_ od ukupno _TOTAL_ ponuda",
            "infoEmpty": "Prikazano 0 do 0 od 0 unosa",
            "infoFiltered": "(Filtrirano iz _MAX_ ukupnih ponuda)",
            "paginate": {
                "first": "Prva",
                "last": "Posljednja",
                "next": "Sljedeća",
                "previous": "Prethodna"
            },
        },
        // Enable vertical scrolling
        scrollY: '195px',  // Set the height

        // Enable scroll collapse
        scrollCollapse: true,

        // Enable fixed header and footer
        fixedHeader: {
            header: true,
            footer: true
        }
    });
    moveDataTablesControls();
}

function moveDataTablesControls() {
    // Remove existing controls from custom divs
    $('#lengthMenuDiv').empty();
    $('#searchDiv').empty();

    // Move length menu (Show entries)
    $('.dataTables_length').appendTo('#lengthMenuDiv');

    // Move search box
    $('.dataTables_filter').appendTo('#searchDiv');
}

window.addEventListener('load', function () {
    document.body.style.opacity = '1';
});

