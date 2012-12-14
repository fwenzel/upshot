$(function() {

$('a[href$=dmg]').click(function() {
    var parts = $(this).attr('href').split('/');
    var file = parts[parts.length - 1];
    _gaq.push(['_trackEvent', 'Downloads', 'DMG', file]);
});

});
