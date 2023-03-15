odoo.define('event_management.event_booking_website',function(require)
{
    var publicWidget = require('web.public.widget');

    publicWidget.registry.PublicWidgetEventBooking = publicWidget.Widget.extend({
     selector: '.website',
     events : {
            'change #to_date': '_onChangeToDate',
     },
      _onChangeToDate: function (ev) {
//            console.log(#to_date);
            var date1 = this.$("#from_date").val();
            var date2 = this.$("#to_date").val();
            var start_date = new Date(date1);
            var end_date = new Date(date2);
            var diffDays = end_date.getTime() - start_date.getTime();
            var result = diffDays / (1000 * 60 * 60 * 24);
            console.log(result);
            $('#duration').val(result);
        }
    });
});
