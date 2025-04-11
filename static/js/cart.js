var updateBtns = document.getElementsByClassName('update-cart')

for (let i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function () {
		let productId = this.dataset.product
		let action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)
		console.log('USER:', user)

		if (user == 'AnonymousUser') {
			addCookieItem(productId, action)
		} else {
			updateUserOrder(productId, action)
		}
	})
}

function updateUserOrder(productId, action) {
	console.log('User is authenticated, sending data...')

	let url = '/update_item/'

	fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		body: JSON.stringify({ 'productId': productId, 'action': action })
	})
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			alert(data.message);  
			location.reload();
		});
}

function addCookieItem(productId, action) {
	console.log('User is not authenticated')

	let productName = document.querySelector(`[data-product="${productId}"]`).closest('.product').querySelector('h6 strong').innerText;

	if (action == 'add') {
		if (cart[productId] == undefined) {
			cart[productId] = { 'quantity': 1 }
		} else {
			cart[productId]['quantity'] += 1
		}
		alert(`Added one "${productName}" to your cart.`)
	}

	if (action == 'remove') {
		cart[productId]['quantity'] -= 1
		if (cart[productId]['quantity'] <= 0) {
			delete cart[productId]
			alert(`Removed "${productName}" from your cart.`)
		} else {
			alert(`Removed one "${productName}" from your cart.`)
		}
	}

	console.log('CART:', cart)
	document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
	location.reload()
}
