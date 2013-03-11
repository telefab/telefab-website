/**
 * Select an equipment in equipment list in an iframe
 */

$(function() {
	// Make the "select" links call the parent window
	$('.select_equipment').click(function() {
		window.parent.browse_equipment_select($(this).attr('data-name'));
		return false;
	});
});