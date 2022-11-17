$(document).ready(function(){
    $("#add_amount").prop('disabled', true);
    // Function to restrict input to between 1 and 100.
    $("#amount").on('input', function(){
        console.log($("#amount").val().length);
        if($("#amount").val().length > 3){
            $("#amount").val($("#amount").val().substring(0,3));
        }
        if ($("#amount").val() >= 1 && $("#amount").val() <= 100){
            $("#add_amount").prop('disabled', false);
        }
        else{
            $("#add_amount").prop('disabled', true);
        }
    });
});