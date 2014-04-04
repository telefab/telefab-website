tinyMCE.init({
	mode : "textareas",
	theme : "modern",
	language : "fr_FR",
	skin : "lightgray",
	plugins: "code,fullscreen,link,image",
	content_css : "/lab/static/main/css/announcements.css",
	toolbar: "undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | code",
	browser_spellcheck : true,
	relative_urls : false,
	remove_script_host : true,
	height: 300
});
