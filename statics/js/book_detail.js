
document.addEventListener('DOMContentLoaded', function() {

    const updateBtn = document.querySelector('#update-btn');
    const confirmBtn = document.querySelector('#confirm-update-btn');
    const cancelBtn = document.querySelector('#cancel-update-btn');
    const deleteButton = document.querySelector('#delete-btn');
    const author = document.querySelector("#author-input");
    const price = document.querySelector("#price-input");
    const description = document.querySelector("#description-input");
    const isbn = document.querySelector("#isbn-input");
    const title = document.querySelector("#title-input");
    const author_old = author.value;
    const title_old = title.value;
    const price_old = price.value;
    const decription_old = description.value;

    var socket = io.connect("http://localhost:5000");
    // socket process successful update
    socket.on('book_updated', function(name) {
        console.log("Successfully Update Book with title - " + name)
        alert("Successfully Update Book with title - " + name);
        title.setAttribute("disabled", true);
        author.setAttribute("disabled", true);
        price.setAttribute("disabled", true);
        description.setAttribute("disabled", true);
        confirmBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
        updateBtn.style.display = 'block';
        deleteButton.style.display = 'block';
        location.reload();
    });
    // socket process successful delete
    socket.on('book_deleted', function(isbn_) {
        window.location.href = 'http://localhost:5000/';
        console.log("Successfully Delete Book with ISBN - " + isbn_)
        alert("Successfully Delete Book with ISBN - " + isbn_);
    });
    // socket process failed update
    socket.on('update_fail', function(error_message) {
        console.log("Error message of Update: " + error_message)
        alert("Error message of Update: " + error_message);
    });

    // socket process failed delete
    socket.on('delete_fail', function(error_message) {
        console.log("Error message of Delete: " + error_message)
        alert("Error message of Delete: " + error_message);
    });
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
            socket.emit("update", JSON.stringify(updateBook))
            // try {
            //     fetch('/update_book', {
            //         method: 'PUT',
            //         headers: {
            //             'Content-Type': 'application/json'
            //         },
            //         body: JSON.stringify(updateBook)
            //     }).then(function(response) {
            //         if (response.status !== 200) {
            //             // handle error response
            //             response.json().then(function(data) {
            //             console.log("Error message: " + data.error);
            //             alert("Error message: " + data.error);
            //           });
            //         } else {
            //             // handle success response
            //             response.json().then(function(data) {
            //                 // Book added successfully, do something here
            //                 console.log('Updated Book:\n', updateBook);
            //                 title.setAttribute("disabled", true);
            //                 author.setAttribute("disabled", true);
            //                 price.setAttribute("disabled", true);
            //                 description.setAttribute("disabled", true);
            //                 confirmBtn.style.display = 'none';
            //                 cancelBtn.style.display = 'none';
            //                 updateBtn.style.display = 'block';
            //                 deleteButton.style.display = 'block';
            //                 confirmationWindow.style.display = "none";
            //                 alert("Successfully Update Book with ISBN - " + isbn_new);
            //                 location.reload();
     
            //         });
            //     }
            //   })
            // } catch (error) {
            //     console.error(error);
            // }
        }else {
            alert("There is nothing changed!")
        }
    });

    // add event listener to delete button
    deleteButton.addEventListener('click', function() {
        // show confirmation window
        updateBtn.style.display = 'none';

        const isbn_value = isbn.value;
        if (confirm("Are you sure you want to delete this book with ISBN " + isbn_value + "?")) {
            // get the book's ISBN number

            // emit a message to the server to delete the book
            socket.emit('delete', isbn_value);
        }
    });
});


  