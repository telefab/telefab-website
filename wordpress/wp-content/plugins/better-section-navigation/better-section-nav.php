<?php
/**
 Plugin Name: Better Section Navigation
 Plugin URI: https://cornershopcreative.com/plugins/better-section-navigation/
 Description: Adds a widget (and shortcode and theme function) for section (or
 top level page) based navigation. The title of the widget is the top level
 page within the current page hierarchy. Shows all page siblings (except on the
 top level page), all parents and grandparents (and higher), the siblings of all
 parents and grandparents (up to top level page), and any immediate children of
 the current page. Can also be called via function inside template files or by
 shortcode.
 Version: 1.6
 Author: Cornershop Creative
 Author URI: https://cornershopcreative.com/
 Text Domain: better-section-nav

	Plugin: Copyright 2017 Cornershop Creative (email : plugins@cornershopcreative.com)

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/**
 * Setup some useful constants
 */
// Full filesystem path to this dir
define( 'BSN_PLUGIN_DIR', dirname( __FILE__ ) );

// Option name for exclusion data
define( 'BSN_EP_OPTION_NAME', 'bsn_exclude_pages' );


/**
 * Create and register the widget.
 */
require_once 'class-better-section-nav.php';
add_action( 'widgets_init', function() {
	register_widget( 'SimpleSectionNav' );
	register_widget( 'Better_Section_Nav' );
} );



/**
 * Display section-based navigation.
 *
 * Arguments include: 'show_all' (boolean), 'exclude' (comma delimited list of page IDs),
 * 'show_on_home' (boolean), 'show_empty' (boolean), sort_by (any valid page sort string),
 * 'a_heading' (boolean), 'before_widget' (string), 'after_widget' (strong)
 *
 * @param array|string $args Optional. Override default arguments.
 * @param bool         $echo Optional. Whether or not to output HTML
 *                           immediately. Set to false to return HTML instead.
 * @return string HTML content, if not displaying.
 */
function better_section_nav( $args = '', $echo = true ) {

	$args = wp_parse_args( $args, array(
		'show_all'         => false,
		'exclude'          => '',
		'hide_on_excluded' => true,
		'show_on_home'     => false,
		'show_empty'       => false,
		'sort_by'          => 'menu_order',
		'a_heading'        => false,
		'before_widget'    => '<div>',
		'after_widget'     => '</div>',
		'before_title'     => '<h2 class="widgettitle">',
		'after_title'      => '</h2>',
		'title'            => '',
	) );

	if ( ! $echo ) {
		ob_start();
	}

	the_widget(
		'Better_Section_Nav',
		$args,
		array(
			'before_widget' => $args['before_widget'],
			'after_widget'  => $args['after_widget'],
			'before_title'  => $args['before_title'],
			'after_title'   => $args['after_title'],
		)
	);

	if ( ! $echo ) {
		return ob_get_clean();
	}
}

function simple_section_nav($atts){
	$args = wp_parse_args( $args, array(
		'show_all'         => false,
		'exclude'          => '',
		'hide_on_excluded' => true,
		'show_on_home'     => false,
		'show_empty'       => false,
		'sort_by'          => 'menu_order',
		'a_heading'        => false,
		'before_widget'    => '<div>',
		'after_widget'     => '</div>',
		'before_title'     => '<h2 class="widgettitle">',
		'after_title'      => '</h2>',
		'title'            => '',
	) );

	if ( ! $echo ) {
		ob_start();
	}

	the_widget(
		'SimpleSectionNav',
		$args,
		array(
			'before_widget' => $args['before_widget'],
			'after_widget'  => $args['after_widget'],
			'before_title'  => $args['before_title'],
			'after_title'   => $args['after_title'],
		)
	);

	if ( ! $echo ) {
		return ob_get_clean();
	}
}

/**
 * Shortcode to display section-based navigation.
 *
 * @param array $atts Shortcode attributes.
 */
function better_section_nav_shortcode( $atts ) {

	$args = shortcode_atts( array(
		'show_all'         => false,
		'exclude'          => '',
		'hide_on_excluded' => true,
		'show_on_home'     => false,
		'show_empty'       => false,
		'sort_by'          => 'menu_order',
		'a_heading'        => false,
		'before_widget'    => '<div>',
		'after_widget'     => '</div>',
		'before_title'     => '<h2 class="widgettitle">',
		'after_title'      => '</h2>',
		'title'            => '',
	), $atts );

	return better_section_nav( $args, false );
}
add_shortcode( 'better-section-nav', 'better_section_nav_shortcode' );

function simple_section_nav_shortcode( $atts ) {

	$args = shortcode_atts( array(
		'show_all'         => false,
		'exclude'          => '',
		'hide_on_excluded' => true,
		'show_on_home'     => false,
		'show_empty'       => false,
		'sort_by'          => 'menu_order',
		'a_heading'        => false,
		'before_widget'    => '<div>',
		'after_widget'     => '</div>',
		'before_title'     => '<h2 class="widgettitle">',
		'after_title'      => '</h2>',
		'title'            => '',
	), $atts );

	return simple_section_nav( $args, false );
}
add_shortcode( 'simple-section-nav', 'simple_section_nav_shortcode' );


/**
 * Implement Exclude Pages plugin functionality
 */
require_once 'exclude-pages.php';


/**
 * Register activation hook
 */
register_activation_hook( __FILE__, 'bsn_activate' );

function simple_section_nav_activate() 
{
	if (get_option('ssn_sortby') === false) return false;	//if not upgrading, leave
	
	$show_all = (get_option('ssn_show_all')) ? 1 : 0;
	$exclude =  str_replace(" ","",get_option('ssn_exclude'));
	$hide_on_excluded = (get_option('ssn_hide_on_excluded')) ? 1 : 0;
	$show_on_home = (get_option('ssn_show_on_home')) ? 1 : 0;
	$show_empty = (get_option('ssn_show_empty')) ? 1 : 0;
	$a_heading = (get_option('ssn_a_heading')) ? 1 : 0;
	
	$settings = array('show_all'=>$show_all, 'exclude'=>$exclude, 'hide_on_excluded'=>$hide_on_excluded,'show_on_home'=>$show_on_home,'show_empty'=>$show_empty,'sort_by'=>get_option('ssn_sortby'),'a_heading'=>$a_heading);
	wp_convert_widget_settings('simple-section-nav','widget_simple-section-nav',$settings);
		
	//delete old settings ... done supporting 1.x
	delete_option('ssn_show_all');
	delete_option('ssn_exclude');
	delete_option('ssn_hide_on_excluded');
	delete_option('ssn_show_on_home');
	delete_option('ssn_show_empty');
	delete_option('ssn_sortby');
	delete_option('ssn_a_heading');
}
register_activation_hook(__FILE__, 'simple_section_nav_activate');

