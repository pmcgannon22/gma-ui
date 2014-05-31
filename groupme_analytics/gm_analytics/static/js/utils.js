var Utils =
    {
        renderLoader: function (elem, loadText) {
            this.loadingHtml = '<div class="data-loading" style="width: 100%; height: 100%">'
            + '<div class="text-center"><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span><p class="lead">' + loadText + '</p></div>'
            + '</div>';
            $(elem).html(this.loadingHtml);
            return $(elem);
        },

    };
