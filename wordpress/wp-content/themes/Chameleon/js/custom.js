jQuery.noConflict();

jQuery(document).ready(function(){
	var et_theme_folder = jQuery("meta[name=et_theme_folder]").attr('content'),
		$et_top_menu = jQuery('ul#top-menu > li > ul'),
		et_disable_toptier = jQuery("meta[name=et_disable_toptier]").attr('content');

	jQuery('ul.nav').superfish({ 
		delay:       600,                            // one second delay on mouseout 
		animation:   {opacity:'show',height:'show'},  // fade-in and slide-down animation 
		speed:       'fast',                          // faster animation speed 
		autoArrows:  true,                           // disable generation of arrow mark-up 
		dropShadows: false                            // disable drop shadows 
	});

		
	var $footer_widget = jQuery("#footer-widgets .footer-widget");
	if ( $footer_widget.length ) {
		$footer_widget.each(function (index, domEle) {
			if ((index+1)%4 == 0) jQuery(domEle).addClass("last").after("<div class='clear'></div>");
		});
	}

	et_search_bar();

	function et_search_bar(){
		var $searchform = jQuery('#additional-info div#search-form'),
			$searchinput = $searchform.find("input#searchinput"),
			searchvalue = $searchinput.val();
			
		$searchinput.focus(function(){
			if (jQuery(this).val() === searchvalue) jQuery(this).val("");
		}).blur(function(){
			if (jQuery(this).val() === "") jQuery(this).val(searchvalue);
		});
	}

	if ( et_disable_toptier == 1 ) jQuery("ul.nav > li > ul").prev("a").attr("href","#");

	var $comment_form = jQuery('form#commentform');
	$comment_form.find('input:text, textarea').focus(function(){
		if (jQuery(this).val() === jQuery(this).next('label').text()) jQuery(this).val("");
	}).blur(function(){
		if (jQuery(this).val() === "") jQuery(this).val( jQuery(this).next('label').text() );
	});

	$comment_form.find('input#submit').click(function(){
		if (jQuery("input#url").val() === jQuery("input#url").next('label').text()) jQuery("input#url").val("");
	});


	jQuery('.service .thumb a').hover(function(){
		jQuery(this).find('img').stop(true,true).fadeTo('fast',0.8).end().find('span').fadeTo('fast',1);
	},function(){
		jQuery(this).find('img').stop(true,true).fadeTo('fast',1).end().find('span').fadeTo('fast',0);
	});

	$multi_media_bar = jQuery('#et-multi-media #media-slides');
	if ( $multi_media_bar.length ) {
		$multi_media_bar.cycle({
			fx: 'fade',
			timeout: 0,
			speed: 500,
			cleartypeNoBg: true,
			prev:   'a#left-multi-media',
			next:   'a#right-multi-media'
		});
	}

	$multi_media_bar.find('.thumb a').hover(function(){
		jQuery(this).find('img').stop(true,true).fadeTo(400,0.7).end().find('span').fadeTo(400,1);
		jQuery(this).parent('.thumb').find('.media-description').stop(true,true).css({'display':'block','opacity':0}).animate({opacity:1, bottom:'53px'},400);
	},function(){
		jQuery(this).find('img').stop(true,true).fadeTo(400,1).end().find('span').fadeTo(400,0);
		jQuery(this).parent('.thumb').find('.media-description').stop(true,true).animate({opacity:0, bottom:'63px'},400);
	});

	$comment_form.find('input, textarea').each(function(index,domEle){
		var $et_current_input = jQuery(domEle),
			$et_comment_label = $et_current_input.siblings('label'),
			et_comment_label_value = $et_current_input.siblings('label').text();
		if ( $et_comment_label.length ) {
			$et_comment_label.hide();
			if ( $et_current_input.siblings('span.required') ) { 
				et_comment_label_value += $et_current_input.siblings('span.required').text();
				$et_current_input.siblings('span.required').hide();
			}
			$et_current_input.val(et_comment_label_value);
		}
	}).live('focus',function(){
		var et_label_text = jQuery(this).siblings('label').text();
		if ( jQuery(this).siblings('span.required').length ) et_label_text += jQuery(this).siblings('span.required').text();
		if (jQuery(this).val() === et_label_text) jQuery(this).val("");
	}).live('blur',function(){
		var et_label_text = jQuery(this).siblings('label').text();
		if ( jQuery(this).siblings('span.required').length ) et_label_text += jQuery(this).siblings('span.required').text();
		if (jQuery(this).val() === "") jQuery(this).val( et_label_text );
	});

	$comment_form.find('input#submit').click(function(){
		if (jQuery("input#url").val() === jQuery("input#url").siblings('label').text()) jQuery("input#url").val("");
	});
});