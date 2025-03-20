const resultElement = document.getElementById("result");
const scannerContainer = document.getElementById("scanner-container");

function initializeScanner() {
    Quagga.init({
        inputStream: {
            type: "LiveStream",
            constraints: {
                facingMode: "environment",
                width: 640,
                height: 480
            },
            target: scannerContainer
        },
        decoder: {
            readers: ["ean_reader"]
        },
        locate: true,
        debug: true
    }, function (err) {
        if (err) {
            console.error("Quagga initialization failed:", err);
            resultElement.innerText = "Грешка при инициализацията на скенера.";
            return;
        }
        console.log("Quagga initialized successfully.");
        Quagga.start();
    });
}

initializeScanner();

Quagga.onDetected(async function (result) {
    if (result && result.codeResult && result.codeResult.code) {
        const barcode = result.codeResult.code;
        console.log("Barcode detected:", barcode);

        Quagga.stop();

        try {
            const openFoodFactsResponse = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
            if (openFoodFactsResponse.ok) {
                const openFoodFactsData = await openFoodFactsResponse.json();
                if (openFoodFactsData.status === 1 && openFoodFactsData.product) {
                    const product = openFoodFactsData.product;

                    let productHTML = `
                        <strong>${product.product_name || 'Няма име'}</strong><br>
                        <img src="${product.image_url || ''}" alt="${product.product_name || 'Няма изображение'}" style="max-width: 200px; margin: 10px 0;"><br>
                        <table>
                            <tr>
                                <th>Калории</th>
                                <td>${product.nutriments['energy-kcal'] || 'Няма информация'} kcal</td>
                            </tr>
                            <tr>
                                <th>Категория</th>
                                <td>${product.categories || 'Няма информация'}</td>
                            </tr>
                            <tr>
                                <th>Съставки</th>
                                <td>${product.ingredients_text || 'Няма информация'}</td>
                            </tr>
                        </table>
                    `;

                    if (product.categories_tags && product.categories_tags.length > 0) {
                        const category = product.categories_tags[0];
                        const similarProductsResponse = await fetch(`https://world.openfoodfacts.org/category/${category}.json`);
                        if (similarProductsResponse.ok) {
                            const similarProductsData = await similarProductsResponse.json();
                            if (similarProductsData.products && similarProductsData.products.length > 0) {
                                productHTML += `<h3>Подобни продукти:</h3><ul>`;
                                similarProductsData.products.slice(0, 5).forEach(similarProduct => {
                                    productHTML += `<li>${similarProduct.product_name || 'Няма име'}</li>`;
                                });
                                productHTML += `</ul>`;
                            }
                        }
                    }

                    resultElement.innerHTML = productHTML;
                    return;
                }
            }
        } catch (error) {
            console.error("Error fetching product data from Open Food Facts:", error);
        }

        resultElement.innerText = "Продуктът не е намерен в базата данни на Open Food Facts.";
    }
});