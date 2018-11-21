function showSuccessMessage(message, reload_bool) {
    $.alert({
        title: 'Success!',
        content: message,
        type: 'green',
        typeAnimated: true,
        autoClose: 'close|4000',
        buttons: {
            close: function () {
                if (reload_bool) {
                    window.location.reload()
                }
            }
        }
    });
};
function showErrorMessage(title, content) {
    $.confirm({
        title: title,
        content: content,
        type: 'red',
        typeAnimated: true,
        backgroundDismiss: false,
        buttons: {
            "Print Error": function() {
                var mywindow = window.open('', 'PRINT', 'height=400,width=600');

                mywindow.document.write('<html><head><title>' + document.title  + '</title>');
                mywindow.document.write('</head><body >');
                mywindow.document.write('<h1>' + document.title  + '</h1>');
                mywindow.document.write($(".jconfirm-content")[0].innerHTML);
                mywindow.document.write('</body></html>');

                mywindow.document.close(); // necessary for IE >= 10
                mywindow.focus(); // necessary for IE >= 10*/

                mywindow.print();
                mywindow.close();

                return true;
            },
            close: function () {
            }
        }
    });
}     