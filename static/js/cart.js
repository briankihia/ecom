var updateBtns = document.getElementsByClassName('update-cart')
// first we have accessed our buttons
// now we loop through all of our buttons

for (i=0; i< updateBtns.length; i++) {
    // we added an event listener to our button
    updateBtns[i].addEventListener('click', function(){
        // dataset is how we query those custom attributes
        // this means the item that is clicked on
        var productId = this.dataset.product 
        var action = this.dataset.action 
        console.log('productId:', productId, 'action:', action)

        // this is where u verify if a user is logged in or not 
        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            console.log('User is not authenticated')
        } else{
            updateUserOrder(productId, action)
        }

    })
}


function updateUserOrder(productId, action) {
    console.log('User is authenticated ,sending data...')

        // here we now send productId and action to the view we just created
        // this is the url we are going to send our post thing to
        var url = '/update_item/'
        
        // we are using the fetch API to send this data to our view
        // first thing we pass into fetch is the url we want to send the data to
        // we then enter the type of data we want to send which here is POST data
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type':'application/json',
                'X-CSRFToken': csrftoken,
            },
            // here we cant just send the object to the backend ie
            // body:{'productId':productId, 'action':action}
            // thus we need to convert it into string ie JSON.stringify
            body:JSON.stringify({'productId':productId, 'action':action})
        })
        // once we send the data we want to return a promise ie it will be the response we get after sending the data
        // we use response in the brackets to turn the value into json data
        .then((response)=> {
            return response.json();
        })
        // now we console the data that we got back
        .then((data)=>{
            console.log('data:', data)
            location.reload()
        });
}