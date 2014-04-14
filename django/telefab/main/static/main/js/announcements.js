/**
 * Specific script for big screens
 * showing announcements
 */

 $(function() {
 	var body = $('body');
 	// Adapt the font size to the screen width
 	function adaptFontSize() {
	 	var baseFontSize = (body.width() - 800) * (35 - 30) / (1366 - 800) + 30;
	 	body.css('fontSize', Math.floor(baseFontSize) + "px");
	}
	$(window).resize(adaptFontSize);
	adaptFontSize();
	// Display once all is ready
	body.show();
 });