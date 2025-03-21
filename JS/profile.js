// Save weight and height to localStorage
function saveDetails(event) {
    event.preventDefault(); // Prevent form submission
    const weight = document.getElementById("weight").value;
    const height = document.getElementById("height").value;

    // Validate height
    if (height < 50 || height > 300) { // Example: height must be between 50 cm and 300 cm
        displayError("Please enter a valid height between 50 cm and 300 cm.");
        return;
    }

    // Save to localStorage
    localStorage.setItem("userWeight", weight);
    localStorage.setItem("userHeight", height);

    // Redirect to profile page
    window.location.href = "profilepage.html";
}

// Display error message
function displayError(message) {
    const errorElement = document.getElementById("error-message");
    errorElement.textContent = message;
    errorElement.style.display = "block";
}

// Load weight and height from localStorage and display on the profile page
function loadProfileDetails() {
    const weight = localStorage.getItem("userWeight");
    const height = localStorage.getItem("userHeight");

    if (weight && height) {
        document.getElementById("user-weight").textContent = `${weight} kg`;
        document.getElementById("user-height").textContent = `${height} cm`;
    }
}