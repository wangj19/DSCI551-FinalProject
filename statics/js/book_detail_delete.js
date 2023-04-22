document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const updateBtn = document.querySelector('#update-btn');
    const confirmBtn = document.querySelector('#confirm-update-btn');
    const cancelBtn = document.querySelector('#cancel-update-btn');
    const deleteButton = document.querySelector('#delete-btn');
    const confirmationWindow = document.getElementById('confirmation-window');
    const confirmDeleteButton = document.querySelector('#confirm-delete');
    const cancelDeleteButton = document.querySelector('#cancel-delete');

    // add event listener to delete button
    deleteButton.addEventListener('click', function() {
    // show confirmation window
        confirmationWindow.style.display = "block";
        updateBtn.style.display = 'none';
        confirmBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
    });

    // add event listener to confirm delete button
    confirmDeleteButton.addEventListener('click', function() {
        const isbn = document.getElementById('isbn-input').value;
        // send isbn to server to delete book
        try {
            // create WebSocket connection
            console.log(isbn)
            fetch(`/delete_book/${isbn}`, {
                method: 'DELETE',
                
            }).then(function(response) {
                if (response.status !== 200) {
                    // handle error response
                    response.json().then(function(data) {
                    console.log("Error message: " + data.error);
                    alert("Error message: " + data.error);
                    updateBtn.style.display = 'block';
                    confirmationWindow.style.display = "none";
                });
                } else {
                    // handle success response
                    response.json().then(function(data) {
                        // Book delete successfully, do something here
                        // load index page
                        window.location.href = 'http://localhost:5000/';
                        console.log("Successfully Update Book with ISBN - " + isbn)
                        alert("Successfully Update Book with ISBN - " + isbn);

                    });
                }
            })
            
        } catch (error) {
            console.error(error);
        }
        
        // hide confirmation window

        
        
    });

    // add event listener to cancel delete button
    cancelDeleteButton.addEventListener('click', function() {
    // hide confirmation window
        confirmationWindow.style.display = "none"
        updateBtn.style.display = 'block';
    });
});