(function () {
    document.addEventListener('DOMContentLoaded', function () {
        var reloadParameter = '__devserver';

        var linkElements = document.getElementsByTagName('link');
        var cssLinkElements = [];

        for (var linkElement in linkElements) {
            if (linkElements.hasOwnProperty(linkElement)) {
                linkElement = linkElements[linkElement];
                var linkHref = linkElement.href || '';
                if (/\.css$/i.exec(linkHref)) {
                    cssLinkElements.push({
                        'e': linkElement,
                        'q': linkHref.indexOf('?') !== -1 ? '&' : '?',
                        'c': 0
                    });
                }
            }
        }

        function reload () {
            for (var cssLinkElement in cssLinkElements) {
                if (cssLinkElements.hasOwnProperty(cssLinkElement)) {
                    cssLinkElement = cssLinkElements[cssLinkElement];
                    if (cssLinkElement['c'] === 0) {
                        cssLinkElement['e'].href += cssLinkElement['q'] + reloadParameter + '=' + cssLinkElement['c'].toString();
                    } else {
                        cssLinkElement['e'].href = cssLinkElement['e'].href.substring(
                            0,
                            cssLinkElement['e'].href.lastIndexOf(reloadParameter) + reloadParameter.length + 1
                        ) + cssLinkElement['c'].toString();
                    }
                    cssLinkElement['c']++;
                }
            }
        }
    });
})();
