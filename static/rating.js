$(document).ready(function () {
  var confirmationToast = new bootstrap.Toast(document.getElementById('confirmationToast'));
  confirmationToast.show();

  var ratingStars = $("#rating").rateYo({
    rating: 0,
    halfStar: true,
    onSet: function (rating, rateYoInstance) {
      var creationInfoId = $("#rating").data("creation-info-id");
      var csrf_token = $("#rating").data("csrf-token");

      rateYoInstance.option("readOnly", true);

      $.ajax({
        type: 'POST',
        url: 'save-rating/',
        data: {
          'rating': rating,
          'creation_info_id': creationInfoId,
          'csrfmiddlewaretoken': csrf_token,
        },
        success: function (data) {
          console.log(data.message);
          var thankYouToast = new bootstrap.Toast(document.getElementById('thankYouToast'));
          thankYouToast.show();
          setTimeout(function () {
            window.location.href = '/logged_in/';
          }, 1000);
        },
        error: function (error) {
          console.error(error);
        }
      });
      
    },
  })
    confirmationToast._config.autohide = false;
  });


document.addEventListener('DOMContentLoaded', function () {
  var btnClose = document.getElementById('btn-close');

  btnClose.addEventListener('click', function () {
      setTimeout(function () {
        window.location.href = '/logged_in/';
      }, 200);
  });
});
