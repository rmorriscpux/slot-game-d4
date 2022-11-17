$(document).ready(function(){
    // Button for game rules.
    $("#show_rules").click(function(){
        $("#game_glass").slideToggle("slow");
    });

    // Buttons for selecting the number of lines.
    // Includes change to the image indicating selected lines.
    $("#line_decrement").click(function(){
        if(parseInt($("#bet").val()) > 1){
            $("#bet").val(parseInt($("#bet").val()) - 1);
        }
        else{
            $("#bet").val(1)
        }
        $("img.reel_lines").attr("src", "/static/img/lines/"+$("#bet").val()+".png")
    });

    $("#line_increment").click(function(){
        if(parseInt($("#bet").val()) < 5){
            $("#bet").val(parseInt($("#bet").val()) + 1);
        }
        else{
            $("#bet").val(5);
        }
        $("img.reel_lines").attr("src", "/static/img/lines/"+$("#bet").val()+".png")
    });
});