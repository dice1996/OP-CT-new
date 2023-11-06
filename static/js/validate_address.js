document.addEventListener('DOMContentLoaded', (event) => {
  // Get the input field
  var input = document.getElementsByName('customer_address')[0];

  // Define the regex pattern
  var pattern = /^(\d+\.\s)?(Ul\.\s)?[A-Za-zčćžšđČĆŽŠĐ0-9\.\s]+ \d+(\w\/\d+)?\w*?,\s+\d{5} [A-Za-zčćžšđČĆŽŠĐ\s]+$/;

  // Initialize a timer variable
  var timeout = null;

  // Add a keyup event listener to the input field
  input.addEventListener('keyup', function () {
    // Clear the existing timeout
    clearTimeout(timeout);

    // Set a new timeout to validate the address
    timeout = setTimeout(function () {
      var isValid = pattern.test(input.value);

      // Use Bootstrap classes to provide visual feedback
      if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
      } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
      }
    }, 500); // Delay in milliseconds (500ms in this case)
  });
});
