jQuery(window).load(function($){
	var $featured = jQuery('#featured'),
		et_featured_slider_auto = jQuery("meta[name=et_featured_slider_auto]").attr('content'),
		et_featured_auto_speed = jQuery("meta[name=et_featured_auto_speed]").attr('content'),
		$et_mobile_nav_button = jQuery('#mobile_nav'),
		$et_nav = jQuery('ul#top-menu'),
		et_container_width = jQuery('#container').width(),
		$cloned_nav;

	if ( $featured.length ){
		et_slider_settings = {

			controlsContainer: '#featured #controllers_wrapper',
			slideshow: false
		}

		if ( '1' === et_featured_slider_auto ) {
			et_slider_settings.slideshow = true;
			et_slider_settings.slideshowSpeed = et_featured_auto_speed;
		}

		et_slider_settings.pauseOnHover = true;

		$featured.flexslider( et_slider_settings );
	}

	if ( ! jQuery('html#ie7').length ) {
		$et_nav.clone().attr('id','mobile_menu').removeClass().appendTo( $et_mobile_nav_button );
		$cloned_nav = $et_mobile_nav_button.find('> ul');

		$et_mobile_nav_button.click( function(){
			if ( jQuery(this).hasClass('closed') ){
				jQuery(this).removeClass( 'closed' ).addClass( 'opened' );
				$cloned_nav.slideDown( 500 );
			} else {
				jQuery(this).removeClass( 'opened' ).addClass( 'closed' );
				$cloned_nav.slideUp( 500 );
			}
			return false;
		} );

		$et_mobile_nav_button.find('a').click( function(event){
			event.stopPropagation();
		} );

		jQuery(window).resize( function(){
			if ( et_container_width != jQuery('#container').width() ) {
				et_container_width = jQuery('#container').width();

				et_mobile_navigation_fix();
				et_footer_widgets_fix();
			}
		});

		et_mobile_navigation_fix();
		et_footer_widgets_fix();
	}

	function et_mobile_navigation_fix(){
		var et_left;

		if ( et_container_width <= 480 ){
			et_left = ( et_container_width - $et_mobile_nav_button.innerWidth() ) / 2;
			if ( et_container_width <= 300 ){
				et_left = et_left - 31;
			} else {
				et_left = et_left - 52;
			}
			$cloned_nav.css( 'left', '-' + et_left + 'px' );
		}
	}

	function et_footer_widgets_fix(){
		var $footer_widget = jQuery("#footer-widgets .footer-widget"),
			footer_columns_num;

		footer_columns_num = et_container_width <= 768 ? 3 : 4;

		if ( $footer_widget.length ) {
			$footer_widget.removeClass('last').closest('#footer-widgets').find('div.clear').remove();

			$footer_widget.each(function (index, domEle) {
				if ((index+1)%footer_columns_num == 0) jQuery(domEle).addClass("last").after("<div class='clear'></div>");
			});
		}
	}
});