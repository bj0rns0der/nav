require([], function() {

    var tableSelector = '#subnet-matrix';
    var family = 4;
    var color_mapping = {
        80: 'usage-high',
        50: 'usage-medium',
        10: 'usage-low',
        0: ' usage-vlow'
    };

    
    /**
     * Fetch the usages for all elements
     */
    function fetchUsage(nextUrl) {
        var url = nextUrl || getUrl();
        var request = $.getJSON(url);
        request.done(handleData);
    }


    function getUrl() {
        var page_size = 10;  // Results per query
        return NAV.urls.api_prefix_usage_list + '?family=' + family + '&page_size=' + page_size;
    }
    
    
    /**
     * Handles the responsedata
     */
    function handleData(data) {
        if (data.next) {
            fetchUsage(data.next);
        }

        var $table = $('#subnet-matrix');

        // For each result, modify the cell based on the result data
        for (var i = 0, l = data.results.length; i < l; i++) {
            var result = data.results[i];

            var $element = $table.find('[data-netaddr="' + result.prefix + '"]');

            console.log(result);
            if (is_v4()) {
                // Add correct class based on usage
                $element.removeClass(getColorClasses).addClass(getClass(result));
                if ($element.attr('colspan') <= 4) {
                    // This is a small cell
                    addToTitle($element.find('a'), result);
                } else {
                    // Add link and text for usage
                    $element.append(createLink(result));
                }
            } else {
                $element.attr('style', 'background-color: ' + getIpv6Color(result));
            }
        }
    }


    /**
     * Remove the classes used to setting colors
     */
    function getColorClasses(index, classString) {
        return classString.split(/\s+/).filter(function(klass) {
            return klass.match(/^(subnet|usage)/);
        }).join(' ');
    }


    /**
     * Returns correct css-class based on usage
     */
    function getClass(result) {
        var values = Object.keys(color_mapping).map(Number).sort();
        values.reverse();
        for (var i = 0; i < values.length; i++) {
            var value = values[i];
            if (result.usage >= value) {
                return color_mapping[value];
            }
        }

        return 'subnet-other';
    }


    /**
     * Creates a link for usage text
     */
    function createLink(data) {
        return $('<a>')
            .attr('href', data.url_machinetracker)
            .attr('title', addresString(data) + 'Click to see addresses in Machine Tracker.')
            .html(usageString(data));
    }


    /**
     * String used for listing active vs max addresses
     */
    function addresString(data) {
        return 'Usage: ' + data.active_addresses + ' of max ' + data.max_hosts + ' addresses. ';
    }
    

    /**
     * String used for displaying usage 
     */
    function usageString(data) {
        return '(' + data.usage.toFixed(0) + '%' + ')';
    }


    function addToTitle($element, data) {
        var toAdd = $element.attr('title') + ' - ' + addresString(data) +
                'Click to see the report for this prefix.';
        
        $element.attr('title', toAdd);
    }


    function is_v4() {return family === 4;}
    function is_v6() {return family === 6;}


    function doubleLog(count) {
        return Math.log(Math.log(count + 1) + 1);
    }
    

    /**
     * Returns a color based on active addresses using a mysterious formula
     */
    function getIpv6Color(result) {
        var smallNumber1 = doubleLog(result.active_addresses);
        var smallNumber2 = doubleLog(Math.pow(2, 64));
        var new_color = 256 - parseInt(255 * smallNumber1 / smallNumber2) - 1;
        var asHex = new_color.toString(16);
        return "#ff" + asHex + asHex;
    }



    // On page load, fetch all usages
    $(function() {
        family = Number($(tableSelector).data('family'));
        fetchUsage();
    });


});
