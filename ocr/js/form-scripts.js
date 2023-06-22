voices = '';


$(document).ready(function () {
    $('#ocr').click(function () {
        $('#working').show();
        var form_data = new FormData($('#ocr_form')[0]);
        $.ajax({
            type: 'POST',
            url: '/ocr',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                try {
                    $('#result').val(data)
                    $('#working').hide();
                }
                catch (err) {
                    $('#working').hide();
                }
                if (data.hasOwnProperty('error')) {
                    $('#working').hide();
                }
            },
        });
    });
    getLanguages();
});

//Get list of optional voices for the requested language


///Get list of supported SST Languages
function getLanguages() {
    $.ajax({
        type: "get",
        url: "languages",
        dataType: "json",
        success: function (data) {
            // data = $.parseJSON(data);
            listItems = '';
            voices = data;
            $.each(data, function (i, item) {
                listItems += "<option value='" + item + "'>" + item + "</option>";

            });
            $("#languages").html(listItems);
        }
    });
}





$(document).on('change', '.btn-file :file', function () {
    var input = $(this),
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [label]);
});


$('.btn-file :file').on('fileselect', function (event, label) {
    var input = $(this).parents('.input-group').find(':text'),
        log = label;
    if (input.length) {
        input.val(log);
    } else {
        if (log) alert(log);
    }
});



function formSuccess(data) {
    submitMSG(true, data)
}

function formError() {
    $("#contactForm").val("Unsupported language");

}

function submitMSG(valid, msg) {
    if (valid) {
        var msgClasses = "h3 text-center tada animated text-success";
    } else {
        var msgClasses = "h3 text-center text-danger";
    }
    $("#lang").val(msg);
}

