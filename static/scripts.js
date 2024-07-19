$(document).ready(function() {
    $('#city').on('keyup', function() {
        var query = $(this).val();
        if(query.length > 2) {
            $.getJSON("/suggestions?q=" + query, function(data) {
                var suggestions = $("#suggestions");
                suggestions.empty();
                $.each(data, function(key, val) {
                    suggestions.append("<li>" + val + "</li>");
                });
                $("#suggestions-container").show();
            });
        } else {
            $("#suggestions-container").hide();
        }
    });
    $("#suggestions-container").on('click', 'li', function() {
        var selectedCity = $(this).text();
        $('#city').val(selectedCity);
        localStorage.setItem('lastSearchedCity', selectedCity);
        $("#suggestions-container").hide();
    });

    var lastSearchedCity = localStorage.getItem('lastSearchedCity');
    if (lastSearchedCity) {
        $('#city').val(lastSearchedCity);
    }
});

$(document).on('click', function(e) {
    if (!$(e.target).closest('#suggestions-container').length) {
        $("#suggestions-container").hide();
    }
});

