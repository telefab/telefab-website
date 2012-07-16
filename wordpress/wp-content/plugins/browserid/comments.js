function browserid_comment(post_id) {
	navigator.id.getVerifiedEmail(function(assertion) {
		if (assertion) {
			var form = jQuery('#browserid_' + post_id).closest('form');
			form.append('<input type="hidden" name="browserid_comment" value="' + post_id + '" />');
			form.append('<input type="hidden" name="browserid_assertion" value="' + assertion + '" />');
			form.find('[type=submit]').click();
		}
		else
			alert(browserid_comments.browserid_failed);
	});
	return false;
}
