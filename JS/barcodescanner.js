const resultElement = document.getElementById("result");
const scannerContainer = document.getElementById("scanner-container");
const rescanButton = document.getElementById("rescan-button");

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
            resultElement.innerText = "Error initializing the scanner.";
            return;
        }
        console.log("Quagga initialized successfully.");
        Quagga.start();
    });
}

function restartScanner() {
    resultElement.innerHTML = "";
    scannerContainer.style.display = "block"; 
    rescanButton.style.display = "none";

    Quagga.stop();
    initializeScanner();
}

initializeScanner();

Quagga.onDetected(async function (result) {
    if (result && result.codeResult && result.codeResult.code) {
        const barcode = result.codeResult.code;
        console.log("Barcode detected:", barcode);

        Quagga.stop();

        scannerContainer.style.display = "none";
        rescanButton.style.display = "block";

        try {
            const openFoodFactsResponse = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
            if (openFoodFactsResponse.ok) {
                const openFoodFactsData = await openFoodFactsResponse.json();
                if (openFoodFactsData.status === 1 && openFoodFactsData.product) {
                    const product = openFoodFactsData.product;

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
                    return;
                }
            }
        } catch (error) {
            console.error("Error fetching product data from Open Food Facts:", error);
        }

        resultElement.innerText = "The product was not found in the Open Food Facts database.";
    }
});

rescanButton.addEventListener("click", restartScanner);