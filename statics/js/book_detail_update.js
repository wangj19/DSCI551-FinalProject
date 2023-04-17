document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const updateBtn = document.querySelector('#update-btn');
    const confirmBtn = document.querySelector('#confirm-update-btn');
    const cancelBtn = document.querySelector('#cancel-update-btn');
    const deleteButton = document.querySelector('#delete-btn');
    const author = document.querySelector("#author-input");
    const price = document.querySelector("#price-input");
    const description = document.querySelector("#description-input");
    const confirmationWindow = document.getElementById('confirmation-window');
    const isbn = document.querySelector("#isbn-input");
    const title = document.querySelector("#title-input");
    const author_old = author.value;
    const title_old = title.value;
    const price_old = price.value;
    const decription_old = description.value;
    // Toggle edit mode
    updateBtn.addEventListener('click', () => {
        title.removeAttribute("disabled");
        author.removeAttribute("disabled");
        price.removeAttribute("disabled");
        description.removeAttribute("disabled");
        confirmBtn.style.display = 'block';
        cancelBtn.style.display = 'block';
        updateBtn.style.display = 'none';
        deleteButton.style.display = 'none';
        confirmationWindow.style.display = "none";
    });

    // Cancel update
    cancelBtn.addEventListener('click', () => {
        title.value = title_old
        title.setAttribute("disabled", true);
        author.value = author_old
        author.setAttribute("disabled", true);
        price.value = price_old
        price.setAttribute("disabled", true);
        description.value = decription_old
        description.setAttribute("disabled", true);
        confirmBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
        updateBtn.style.display = 'block';
        deleteButton.style.display = 'block';
    });

    // Update book
    confirmBtn.addEventListener('click', async () => {
        
        let isChanged = false;
        const isbn_new = isbn.value;
        const title_new = title.value;
        const price_new_str = price.value;
        const author_new = author.value;
        const description_new = description.value;
        const price_new = parseFloat(price_new_str);
        if (title_new!==title_old|| price_new_str != price_old||
            author_new!==author_old|| decription_old!==description_new){
            isChanged = true;
        }
        if (isNaN(price_new)) {
            alert('Price must be a valid number!');
            return false;
        }
        // Construct the new book object
        var updateBook = {
            'isbn': isbn_new,
            'title': title_new,
            'author': author_new,
            'price': price_new,
            'description': description_new
        };
        if (isChanged) {
            try {
                fetch('/update_book', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updateBook)
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
                            console.log('Updated Book:\n', updateBook);
                            title.setAttribute("disabled", true);
                            author.setAttribute("disabled", true);
                            price.setAttribute("disabled", true);
                            description.setAttribute("disabled", true);
                            confirmBtn.style.display = 'none';
                            cancelBtn.style.display = 'none';
                            updateBtn.style.display = 'block';
                            deleteButton.style.display = 'block';
                            confirmationWindow.style.display = "none";
                            alert("Successfully Update Book with ISBN - " + isbn_new);
                            location.reload();
     
                    });
                }
              })
            } catch (error) {
                console.error(error);
            }
        }else {
            alert("There is nothing changed!")
        }
    });
  });
  