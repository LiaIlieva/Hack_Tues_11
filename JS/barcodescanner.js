const resultElement = document.getElementById("result");
const scannerContainer = document.getElementById("scanner-container");
const similarButton = document.getElementById("similar-button");
const rescanButton = document.getElementById("rescan-button");
const analyzeButton = document.getElementById("analyze-button");

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
    similarButton.style.display = "none";
    analyzeButton.style.display = "none";

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
        similarButton.style.display = "block";
        analyzeButton.style.display = "block";

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

similarButton.addEventListener("click", function() {
    // Make a GET request to the /get-similar-food route
    fetch(`/get-similar-food`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            // Display the similar foods
            displaySimilarFoods(data.similar_foods);
        } else {
            console.error("Failed to fetch similar foods:", data.error);
            alert("Failed to fetch similar foods. Please try again.");
        }
    })
    .catch(error => {
        console.error("Error fetching similar foods:", error);
        alert("An error occurred while fetching similar foods.");
    });
});

// Function to display similar foods
function displaySimilarFoods(similarFoods) {
    let similarFoodsHTML = "<h3>Similar Foods:</h3>";
    similarFoods.forEach(food => {
        similarFoodsHTML += `
            <div>
                <strong>${food.product_name}</strong><br>
                <em>Ingredients:</em> ${food.ingredients}<br><br>
            </div>
        `;
    });

    // Display the similar foods in the result element or another container
    resultElement.innerHTML += similarFoodsHTML;
}

analyzeButton.addEventListener("click", function() {
    // Make a GET request to the /analyze-food route
    fetch(`/analyze-food`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            // Display the evaluation result
            displayEvaluation(data.evaluation);
        } else {
            console.error("Failed to analyze food:", data.error);
            alert("Failed to analyze food. Please try again.");
        }
    })
    .catch(error => {
        console.error("Error analyzing food:", error);
        alert("An error occurred while analyzing the food.");
    });
});

// Function to display the evaluation result
function displayEvaluation(evaluation) {
    let evaluationHTML = "<h3>Food Evaluation:</h3>";
    evaluationHTML += `
        <div>
            <strong>Product Name:</strong> ${evaluation.product_name}<br>
            <strong>Nutritional Evaluation:</strong> ${evaluation.nutritional_evaluation}<br>
            <strong>Ingredient Evaluation:</strong> ${evaluation.ingredient_evaluation}<br>
        </div>
    `;

    // Display the evaluation in the result element or another container
    resultElement.innerHTML += evaluationHTML;
}