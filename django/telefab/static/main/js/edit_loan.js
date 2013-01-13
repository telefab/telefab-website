/**
 * Runs the loans form to add/remove equipments
 */

$(function() {
	// Pointers used everywhere
	var sections_list = $('.booking_sections');
	var section_sample = null; 
	var sections_counter = sections_list.find('.booking_section').length;


	// Equipment names list for autocomplete
	var equipment_names = [];
	for (var i = 0; i < equipment_data.length; i++)
		equipment_names[i] = {
			"label": equipment_data[i].name + " (" + equipment_data[i].quantity + ")",
			"value": equipment_data[i].name,
		}

	// Function to get equipment data from a booking section, or null if not known
	function get_equipment_data(booking_el) {
		var name = booking_el.find('.equipment_name').val();
		for (var i = 0; i < equipment_data.length; i++)
			if (equipment_data[i].name == name)
				return equipment_data[i];
		return null;

	}

	// Function to update the equipment id depending on the name. Returns if the element was found.
	function check_equipment_id(name_el)
	{
		var id = -1;
		var booking_el = name_el.parents('.booking_section')
		if (name_el.val().length == 0) {
			id = 0;
		} else {
			var data = get_equipment_data(booking_el);
			if (data != null)
				id = data.id;
		}
		booking_el.find('.equipment_id').val(id);
		return id >= 0;
	}

	// Function to add autocomplete equipment name to an element
	function add_autocomplete(element) {
		element.autocomplete({
			'source': equipment_names,
			'autoFocus': true,
			'change': function() {check_equipment_id(element)}
		});
	}

	// Button to add some equipment
	$('.add_equipment').click(function(){
		// Clone the new section
		var new_section = section_sample.clone(true);
		// Rename the unique identifiers
		sections_counter = sections_counter + 1;
		new_section.find('input').each(function(){
			var name = $(this).attr('class') + sections_counter;
			$(this).attr('name', name);
			$(this).attr('id', name);
			$(this).prev('label').attr('for', name);
		});
		// Add autocomplete
		add_autocomplete(new_section.find('.equipment_name'));
		// Append to the DOM
		sections_list.append(new_section);
		return false;
	});
	// Buttons to delete an equipment
	$('.delete_equipment').click(function(){
		var section = $(this).parents('.booking_section');
		section.find('.equipment_remove').val(1);
		section.hide();
		return false;
	})
	// Buttons to browse the equipments list
	$('.browse_equipments').click(function(){
		var section = $(this).parents('.booking_section');
		var select_dialog;
		window.browse_equipment_select = function(name) {
			// Function called by the iframe to select an equipment
			// Set the name and id
			var name_el = section.find(".equipment_name");
			name_el.val(name);
			check_equipment_id(name_el);
			// Close the dialog
			select_dialog.dialog('close');
		}
		// Open the iframe with equipment lists
		select_dialog = $('<iframe />').attr('src', '/lab/choix/materiel').dialog({
			modal: true,
			resizable: false,
			draggable: false,
			title: "Sélectionner un équipement",
			width: 800,
			height: 600,
			open: function (event,ui) {$(this).css("width","780px")}
		});
		return false;
	});

	// Clones the section sample with all the events and makes it fully ready to use as a new section
	section_sample = sections_list.find('.booking_section').first().clone(true);
	section_sample.removeClass('edit_disabled');
	section_sample.find('.equipment_name').attr('disabled', false);
	section_sample.find('.equipment_name').val('');
	section_sample.find('.equipment_quantity').val('1');
	section_sample.find('.equipment_booking_id').val('');
	section_sample.find('.equipment_id').val('');

	// Adds autocomplete to existing elements
	add_autocomplete(sections_list.find('.equipment_name'));

	// Check the whole form on submit
	$('form').submit(function() {
		// Check the return date
		var date = $('#scheduled_return_date').datepicker('getDate');
		if (date == null) {
			$('<p />').text("Merci d'indiquer une date de retour indicative.").dialog({
				modal: true,
				resizable: false,
				draggable: false,
				title: "Erreur"
			});
			return false;
		}
		var today = new Date();
		today.setHours(0);
		today.setMinutes(0);
		today.setSeconds(0);
		today.setMilliseconds(0);
		if (date < today) {
			$('<p />').text("La date de retour prévue ne peut pas être déjà passée.").dialog({
				modal: true,
				resizable: false,
				draggable: false,
				title: "Erreur"
			});
			return false;
		}
		// Check each equipment
		var ok = true;
		var bookings = 0;
		sections_list.find('.booking_section').each(function() {
			// Ignore removed elements
			if (parseInt($(this).find('.equipment_remove').val()) > 0)
				return true
			// Update the id (check the name)
			var name_el = $(this).find(".equipment_name");
			if (!check_equipment_id(name_el)) {
				$('<p />').text("L'équipement \"" + name_el.val() + "\" est inconnu.").dialog({
					modal: true,
					resizable: false,
					draggable: false,
					title: "Erreur"
				});
				ok = false;
				return false;
			}
			// Check the quantity of each equipment
			var data = get_equipment_data($(this));
			if (parseInt($(this).find('.equipment_quantity').val()) > data.quantity) {
				$('<p />').text("Vous ne pouvez pas emprunter plus de " + data.quantity + " exemplaire(s) de " + data.name + ".").dialog({
					modal: true,
					resizable: false,
					draggable: false,
					title: "Erreur"
				});
				ok = false;
				return false;
			}
			bookings++;
		});
		if (!ok)
			return false;
		// Check that there is at least 1 equipment
		if (bookings == 0) {
			$('<p />').text("Merci d'indiquer ce que vous voulez emprunter en cliquant sur \"Ajouter un équipement\".").dialog({
				modal: true,
				resizable: false,
				draggable: false,
				title: "Erreur"
			});
			return false;
		}
	});

	// Adds datepicker to the return date
	$('#scheduled_return_date').datepicker($.datepicker.regional["fr"]);
})