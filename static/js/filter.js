// Credit to giorgitbs | http://jsfiddle.net/giorgitbs/52ak9/1/
$(document).ready(function () {
    
    (function ($) {

        $('#search').keyup(function () {

            var rex = new RegExp($(this).val(), 'i');
            $('.searchable tr').hide();
            $('.searchable tr').filter(function () {

                return rex.test($(this).text());
            }).show();
        })

        $('#filter').keyup(function () {

            var rex = new RegExp($(this).val(), 'i');
            $('.searchable tr').hide();
            $('.searchable tr').filter(function () {

                return rex.test($(this).text());
            }).show();
        })
    }(jQuery));
});