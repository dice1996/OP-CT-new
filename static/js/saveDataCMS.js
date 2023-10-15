$('#saveChanges').click(function () {
    let updatedData = {
        cms_user: $('#sessionCMSUser').val(),
        cms_password: $('#sessionCMSPassword').val()
    };

    $.ajax({
        url: '/api/update_user_data',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(updatedData),
        success: function (response) {
            if (response === '200') {
                alert('Podaci uspješno spremljeni!');
                $('#userDataModal').modal('hide');
            } else {
                alert('Pogreška prilikom spremanja podataka.');
            }
        }
    });
});