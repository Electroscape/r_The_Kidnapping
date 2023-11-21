$(".option").click(function () {
    $(".option").removeClass("active");
    $(".gameContentClass").addClass("d-none");
    $(this).addClass("active");
    let opNum = this.id.at(-1);
    $("#gameContent" + opNum).removeClass("d-none");
    $(".txt-vertical").css("color", "black");
    $(this).find(".txt-vertical").css("color", "transparent");
});