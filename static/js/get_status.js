$(document).ready(function() {
    // Function to format the date
    function formatDate(dateString) {
        var date = new Date(dateString);
        return date.toLocaleString('hr-HR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }

    // Function to get status update
    function getStatusUpdate() {
        $.ajax({
            url: '/get_status',  // The route we created in Flask
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if(response.success) {
                    // Parse the last update time and create a Date object at midnight
                    var lastUpdateDate = new Date(response.last_update_time);
                    lastUpdateDate.setHours(0, 0, 0, 0);

                    // Create a new Date object for the current time at midnight
                    var currentDate = new Date();
                    currentDate.setHours(0, 0, 0, 0);

                    // Check if the last update was before today
                    if(lastUpdateDate < currentDate) {
                        $('#statusDot').css('color', 'red'); // Last update was before today, show red dot
                    } else {
                        $('#statusDot').css('color', 'green'); // Last update was today, show green dot
                    }

                    $('#lastUpdateTime').html('Ažurirano: <strong>' + formatDate(response.last_update_time)) + '</strong>';
                } else {
                    // If there was an error or no status update found
                    alert(response.message);
                }
            },
            error: function(xhr, status, error) {
                // If there was an AJAX error
                //alert('An error occurred while fetching the status update.');
            }
        });
    }

    // Call the getStatusUpdate function to get the status when the page loads
    getStatusUpdate();

    // Optionally, if you want to poll the server every minute for status updates, you can set an interval
    // setInterval(getStatusUpdate, 60000); // 60000 milliseconds = 1 minute
});