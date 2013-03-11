/**
 * Runs the events form
 */

$(function() {
	function add_datepicker(element) {
		// Adds a datepicker
		element.datepicker($.datepicker.regional["fr"]);
	}
	function add_min_select(element) {
		// Adds a dropdown to minutes
		var minutes = [];
		for (var i = 0; i < 4; i++)
			minutes.push("" + (i*15));
		element.autocomplete({
			'source': minutes,
			'autoFocus': false,
			'minLength': 0
		}).focus(function() {
			$(this).autocomplete('search', $(this).val());
		});
	}
	// Adds date helpers
	add_datepicker($('#start_date'));
	add_datepicker($('#end_date'));
	add_min_select($('#start_min'));
	add_min_select($('#end_min'));
})
