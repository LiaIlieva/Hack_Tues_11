Quagga.onDetected(async function (result) {
    if (result && result.codeResult && result.codeResult.code) {
        const barcode = result.codeResult.code;
        console.log("Barcode detected:", barcode);

        Quagga.stop();

        scannerContainer.style.display = "none";
        rescanButton.style.display = "block";
        similarButton.style.display = "block";
        analizeButton.style.display = "block";

        try {
            // Fetch product data from Open Food Facts
            const openFoodFactsResponse = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
            if (openFoodFactsResponse.ok) {
                const openFoodFactsData = await openFoodFactsResponse.json();
                if (openFoodFactsData.status === 1 && openFoodFactsData.product) {
                    const product = openFoodFactsData.product;

                    // Prepare the product data to send to the backend
                    const productData = {
                        product_name: product.product_name || 'No name available',
                        product: product.brands || 'No brand available',
                        ingredients_text: product.ingredients_text || 'No ingredients available',
                        nutriments: product.nutriments || {},
                        code: barcode,
                        status: 1  // Indicates the product was found
                    };

                    // Send the product data to the backend
                    const backendResponse = await fetch('/product', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(productData),
                    });

                    if (backendResponse.ok) {
                        const backendData = await backendResponse.json();
                        console.log('Product saved successfully:', backendData);

                        // Display the product information
                        let productHTML = `
                            <strong>${product.product_name || 'No name available'}</strong><br>
                            <center><img src="${product.image_url || ''}" alt="${product.product_name || 'No image available'}" style="max-width: 200px; margin: 10px 0;"><br></center>
                            <table>
                                <tr>
                                    <th>Calories/100g</th>
                                    <td>${product.nutriments['energy-kcal'] || 'No information available'} kcal</td>
                                </tr>
                                <tr>
                                    <th>Category</th>
                                    <td>${product.categories || 'No information available'}</td>
                                </tr>
                                <tr>
                                    <th>Ingredients</th>
                                    <td>${product.ingredients_text || 'No information available'}</td>
                                </tr>
                            </table>
                        `;

                        resultElement.innerHTML = productHTML;
                    } else {
                        console.error('Failed to save product:', backendResponse.statusText);
                        resultElement.innerText = "Failed to save product. Please try again.";
                    }
                } else {
                    resultElement.innerText = "The product was not found in the Open Food Facts database.";
                }
            } else {
                resultElement.innerText = "Failed to fetch product from Open Food Facts.";
            }
        } catch (error) {
            console.error("Error:", error);
            resultElement.innerText = "An error occurred. Please try again.";
        }
    }
});