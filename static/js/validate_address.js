document.addEventListener('DOMContentLoaded', (event) => {
  // Get the input field
  var input = document.getElementsByName('customer_address')[0];

  // Define the regex pattern
  var pattern = /^(\d+\.\s)?(Ul\.\s)?[A-Za-zčćžšđČĆŽŠĐ0-9\.\s]+ \d+(\w\/\d+)?\w*?,\s+\d{5} [A-Za-zčćžšđČĆŽŠĐ\s]+$/;

  // Function to validate the address
  function validateAddress() {
    // Check if the input is not empty and not just whitespace
    if (input.value.trim()) {
      var isValid = pattern.test(input.value);

      // Use Bootstrap classes to provide visual feedback
      if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
      } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
      }
    } else {
      // If the input is empty, remove both classes
      input.classList.remove('is-invalid');
      input.classList.remove('is-valid');
    }
  }

  // Initialize a timer variable for debouncing
  let debounceTimer;

  // Add an 'input' event listener to the input field
  input.addEventListener('input', function () {
    // Clear any existing timer to reset the debounce period
    clearTimeout(debounceTimer);

    // Set a new debounce timer
    debounceTimer = setTimeout(validateAddress, 500); // Delay in milliseconds (500ms in this case)
  });
});
