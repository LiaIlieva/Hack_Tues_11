const resultElement = document.getElementById("result");
const scannerContainer = document.getElementById("scanner-container");
const similarButton = document.getElementById("similar-button");
const rescanButton = document.getElementById("rescan-button");
const analyzeButton = document.getElementById("analyze-button");

// Function to initialize the barcode scanner
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

// Function to restart the scanner
function restartScanner() {
    resultElement.innerHTML = "";
    scannerContainer.style.display = "block";
    rescanButton.style.display = "none";
    similarButton.style.display = "none";
    analyzeButton.style.display = "none";

    Quagga.stop();
    initializeScanner();
}

// Initialize the scanner on page load
initializeScanner();

// Event listener for barcode detection
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

                    //Send the scanned product to the backend
                    await fetch("/product", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(openFoodFactsData)
                    });

                } else {
                    resultElement.innerText = "The product was not found in the Open Food Facts database.";
                }
            } else {
                throw new Error(`Failed to fetch product data: ${openFoodFactsResponse.status}`);
            }
        } catch (error) {
            console.error("Error fetching product data from Open Food Facts:", error);
            resultElement.innerText = "An error occurred while fetching product data.";
        }
    }
});


// Event listener for the rescan button
rescanButton.addEventListener("click", restartScanner);

// Event listener for the analyze button
analyzeButton.addEventListener("click", function () {
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
    
    const evaluationContainer = document.createElement("div");
    evaluationContainer.classList.add("evaluation-result");

    evaluationContainer.innerHTML = `
        <h3>Food Evaluation</h3>
        <div class="evaluation-details">
            <p><strong>Product Name:</strong> ${evaluation.product_name}</p>
            <p><strong>Nutritional Evaluation:</strong> ${evaluation.nutritional_evaluation}</p>
            <p><strong>Ingredient Evaluation:</strong> ${evaluation.ingredient_evaluation}</p>
        </div>
    `;

    resultElement.appendChild(evaluationContainer);
}

// Event listener for the similar button
similarButton.addEventListener("click", function () {
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
    // Create a container for the similar foods
    const similarFoodsContainer = document.createElement("div");
    similarFoodsContainer.classList.add("similar-foods");

    // Add a heading
    similarFoodsContainer.innerHTML = "<h3>Similar Foods:</h3>";

    // Loop through the similar foods and create HTML for each
    similarFoods.forEach(food => {
        const foodItem = document.createElement("div");
        foodItem.classList.add("food-item");

        foodItem.innerHTML = `
            <p><strong>${food.product_name}</strong></p>
            <p><em>Ingredients:</em> ${food.ingredients}</p>
        `;

        similarFoodsContainer.appendChild(foodItem);
    });

    // Append the similar foods container to the result element
    resultElement.appendChild(similarFoodsContainer);
}