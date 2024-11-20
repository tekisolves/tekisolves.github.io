document.addEventListener('DOMContentLoaded', function() {
    // Printify API token (replace 'YOUR_API_KEY' with your actual API key)
    const API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6ImI1ZjBlNDFjN2U1OWU4ZWIyYjA5OGU5YTMzYTQ2N2Y5MDdkZDdlMTBkNGI4YzhjMjMwN2RkODk0ODI2ZThjZWEwMzg4MjhiMmFmOTU1NjBmIiwiaWF0IjoxNzMxNjA0Nzc4Ljg4NDExNiwibmJmIjoxNzMxNjA0Nzc4Ljg4NDExOSwiZXhwIjoxNzYzMTQwNzc4Ljg3Njk5OSwic3ViIjoiMjA0MTM4NjAiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIiwidXNlci5pbmZvIl19.ArOcG4YkIjJVYBsTWgeaAS0vAuT03BYNEEBV7v2bNuwO1ksXTl14lEEEWapnnwjHuE7PCM7t3MjTjhORCno';
    const SHOP_ID = '18813703';

    fetch(`https://api.printify.com/v1/shops/${SHOP_ID}/products.json`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const productList = document.getElementById('product-list');
        productList.innerHTML = ''; // Clear initial loading text

        data.data.forEach(product => {
            const productDiv = document.createElement('div');
            productDiv.className = 'col-md-4 mb-4'; // Bootstrap column class

            productDiv.innerHTML = `
                <div class="card">
                    <img src="${product.images[0].src}" class="card-img-top" alt="${product.title}">
                    <div class="card-body">
                        <h5 class="card-title">${product.title}</h5>
                        <p class="card-text">${product.description || 'No description available'}</p>
                    </div>
                </div>
            `;
            productList.appendChild(productDiv);
        });
    })
    .catch(error => {
        console.error('Error fetching products:', error);
        document.getElementById('product-list').innerHTML = 'Failed to load products.';
    });
});