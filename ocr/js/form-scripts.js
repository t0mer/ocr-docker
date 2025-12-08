voices = '';


$(document).ready(function () {
    $('#ocr').click(function () {
        $('#working').show();
        var imageUrl = $('#imageUrl').val().trim();
        var hasFile = $('#imgInp').val();

        if (!hasFile && !imageUrl) {
            alert('Please select a file (image/PDF/CSV) or provide an image URL.');
            $('#working').hide();
            return;
        }
        var form_data = new FormData($('#ocr_form')[0]);
        $.ajax({
            type: 'POST',
            url: '/ocr',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            xhrFields: {
                responseType: 'blob'
            },
            success: function (data, status, xhr) {
                const disposition = (xhr.getResponseHeader('Content-Disposition') || '').toLowerCase();
                const isCsv = disposition.includes('attachment') && disposition.includes('.csv');

                if (isCsv) {
                    const downloadNameMatch = /filename="?([^";]+)"?/i.exec(xhr.getResponseHeader('Content-Disposition') || '');
                    const downloadName = downloadNameMatch && downloadNameMatch[1] ? downloadNameMatch[1] : 'ocr_results.csv';
                    const blob = new Blob([data], { type: xhr.getResponseHeader('Content-Type') || 'text/csv' });
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = downloadName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                    $('#result').val('Se generó un CSV con los resultados y se descargó automáticamente.');
                    $('#working').hide();
                    return;
                }

                new Response(data).text().then(function (text) {
                    $('#result').val(text);
                }).finally(function () {
                    $('#working').hide();
                });
            },
            error: function () {
                $('#working').hide();
            }
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

