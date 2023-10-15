document.addEventListener('keydown', function (event) {
    let suggestionsDropdown = document.getElementById('suggestions');
    let suggestions = suggestionsDropdown.children;
    let focusedSuggestion = document.activeElement;

    // Check if Ctrl + S is pressed
    if (event.ctrlKey && event.key.toLowerCase() === 's') {
        event.preventDefault();
        let searchBox = document.getElementById('productQuery');
        searchBox.value = ''; // Clear search box
        searchBox.focus();    // Set focus to search box
    }

    // Check if ArrowDown is pressed
    if (event.key === 'ArrowDown' && suggestionsDropdown && !suggestionsDropdown.hidden) {
        event.preventDefault();
        if (focusedSuggestion && focusedSuggestion.parentNode === suggestionsDropdown) {
            // Move focus to next suggestion if there's one
            if (focusedSuggestion.nextSibling) {
                focusedSuggestion.nextSibling.focus();
            }
        } else {
            // Focus the first suggestion
            if (suggestions.length > 0) {
                suggestions[0].focus();
            }
        }
    }

    // Check if ArrowUp is pressed
    if (event.key === 'ArrowUp' && suggestionsDropdown && !suggestionsDropdown.hidden) {
        event.preventDefault();
        if (focusedSuggestion && focusedSuggestion.parentNode === suggestionsDropdown && focusedSuggestion.previousSibling) {
            // Move focus to previous suggestion
            focusedSuggestion.previousSibling.focus();
        }
    }

    // Check if Enter is pressed
    if (event.key === 'Enter') {
        event.preventDefault();
        // If a suggestion is focused, select the product and run the search
        if (focusedSuggestion && focusedSuggestion.parentNode === suggestionsDropdown) {
            focusedSuggestion.click();
        } else {
            // Trigger the search button's click event
            let searchButton = document.querySelector('.input-group-append button');
            if (searchButton) {
                searchButton.click();
            }
        }
    }
});
