/**
 * Specific script for big screens
 * showing announcements
 */

 $(function() {
 	var body = $('body');
 	// Adapt the font size to the screen width
 	function adaptFontSize() {
	 	var baseFontSize = body.width()*35/1366;
	 	body.css('fontSize', Math.floor(baseFontSize) + "px");
	}
	$(window).resize(adaptFontSize);
	adaptFontSize();
	// Display once all is ready
	body.fadeIn();
 });