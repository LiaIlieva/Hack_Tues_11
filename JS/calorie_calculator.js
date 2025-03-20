$(".calculator input").on("input change", function (event) {
    var parameterName = $(this).attr("id").split("calc-")[1];
    var centimeters = $(this).val()

    switch (parameterName) {
        case "height":
            $("#calc-height_value").html("Height: " + centimeters + " cm");
            break;
        case "weight":
            var kg = $(this).val();
            $("#calc-weight_value").html("Weight: " + kg + " kg");
            break;
        case "age":
            $("#calc-age_value").html("Age: " + $(this).val());
            break;
        case "cardio":
            $("#calc-cardio_value").html("Cardio: " + $(this).val() + " hours per week");
            break;
        case "walking":
            $("#calc-walking_value").html("Walking: " + $(this).val() + " hours per week");
            break;
    }

    var height = parseInt($("#calc-height").val(), 10);
    var age = parseInt($("#calc-age").val(), 10);
    var weight = parseInt($("#calc-weight").val(), 10);
    var walking = parseInt($("#calc-walking").val(), 10);
    var cardio = parseInt($("#calc-cardio").val(), 10);
    var gender = $(".calculator input[name='gender']:checked").val();

    var bmr = parseInt(10 * weight + 6.25 * height - 5 * age, 10) + (gender === "male" ? 5 : -161);
    bmr = bmr * 1.2;
    bmr += walking * 60 * (.03 * weight * 1 / 0.45) / 7;
    bmr += cardio * 60 * (.07 * weight * 1 / 0.45) / 7;
    bmr = Math.floor(bmr);

    var targetGainWeight = Math.round((bmr + 300) / 100) * 100;
    var targetMaintain = Math.round((bmr) / 100) * 100;
    var targetLoseWeight = Math.round((bmr - 500) / 100) * 100;

    $("#calc-target-gain span").html(targetGainWeight + " calories");
    $("#calc-target-maintain span").html(targetMaintain + " calories");
    $("#calc-target-lose span").html(targetLoseWeight + " calories");
});