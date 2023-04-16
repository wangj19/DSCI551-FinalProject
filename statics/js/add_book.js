// Wait for the DOM to load
document.addEventListener('DOMContentLoaded', function() {

  // Get the add book button element
  var addBookBtn = document.getElementById('add-book-btn');

  // Get the add book dialog element
  var addBookDialog = document.getElementById('add-book-dialog');

  // Get the add book form element
  var addBookForm = document.getElementById('add-book-form');

  // Add a click event listener to the add book button
  addBookBtn.addEventListener('click', function() {
    // Display the add book dialog
    addBookDialog.style.display = 'block';
  });

  // Add a click event listener to the cancel button
  var cancelBtn = document.getElementById('cancel-button');
  cancelBtn.addEventListener('click', function() {
    // Hide the add book dialog
    addBookDialog.style.display = 'none';
  });

  // Add a submit event listener to the add book form
  addBookForm.addEventListener('submit', function(event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get the input values from the form
    var isbnInput = document.getElementById('isbn-input');
    var titleInput = document.getElementById('title-input');
    var authorInput = document.getElementById('author-input');
    var priceInput = document.getElementById('price-input');
    var descriptionInput = document.getElementById('description-input');
      // Check if all required fields are filled up
    if (isbnInput.value === '' || titleInput.value === '' || authorInput.value === '' || priceInput.value === '' || descriptionInput.value === '') {
      alert('Please fill in all fields!');
      return false;
    }

    // Check if price is a valid float
    const price = parseFloat(priceInput.value);
    const title = titleInput.value
    if (isNaN(price)) {
      alert('Price must be a valid number!');
      return false;
    }
    // Check if ISBN is a 10-digit number

    if (isbnInput.value.length !== 10 || isNaN(parseInt(isbnInput.value))) {
      alert("ISBN must be a 10-digit number");
      event.preventDefault();
      return;
    }
    // Construct the new book object
    var newBook = {
      'isbn': isbnInput.value,
      'title': titleInput.value,
      'author': authorInput.value,
      'price': price,
      'description': descriptionInput.value
    };
    fetch('/add_book', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newBook)
    }).then(function(response) {
      if (response.status !== 200) {
        // handle error response
        response.json().then(function(data) {
          console.log("Error message: " + data.error);
          alert("Error message: " + data.error);
        });
      } else {
        // handle success response
        response.json().then(function(data) {
          // Book added successfully, do something here
          location.reload(); // Reload the book page
          // print sth in console
          alert("Successfully Insert New Book - " + title)
          console.log('New book added:', newBook);
        });
      }
    }).catch(function(err) {
      console.log("Fetch error: " + err);
    });
  });
    
});
