<?php
/**
 * Implements the filtering of page lists within Better Section Nav widgets
 *
 * @todo Refactor into a Singleton a la https://code.tutsplus.com/articles/design-patterns-in-wordpress-the-singleton-pattern--wp-31621
 */

/**
 * Takes a pages array and returns it with the excluded pages removed.
 *
 * @param array $pages An array of pages.
 *
 * @return array The original $pages array with excluded pages removed, provided we're not in the admin.
 */
function bsn_exclude_pages( $pages ) {

	// If Admin, or otherwise indicated to not perform exclusions, bail.
	$bail_out = apply_filters( 'ep_admin_bail_out', is_admin() );
	if ( $bail_out ) {
		return $pages;
	}

	// Make sure $pages is what we expect.
	if ( ! is_array( $pages ) ) {
		return $pages;
	}

	$excluded_ids = bsn_get_excluded_ids();

	// Ensure we catch all descendant pages, so that if a parent
	// is hidden, its children are too.
	foreach ( $pages as $key => $page ) {
		// If this page, or one of its ancestor pages is excluded, remove it
		if ( in_array( (int) $page->ID, $excluded_ids, true ) || bsn_is_ancestor_excluded( $page, $excluded_ids, $pages ) ) {
			unset( $pages[ $key ] );
		}
	}

	// Reindex the array, for neatness
	$pages = array_values( $pages );

	return $pages;
}
add_filter( 'get_pages', 'bsn_exclude_pages' );


/**
 * Recurse up an ancestor chain of a given page, checking if one is excluded
 *
 * @param object $page The WP_Post object to check the ancestors of, presumably of type Page.
 * @param array  $excluded_ids A list of the pages to possibly be excluded.
 *
 * @return boolean|int The ID of the "nearest" excluded ancestor, otherwise false.
 */
function bsn_is_ancestor_excluded( $page, $excluded_ids ) {

	// Get an array of ancestor IDs. Empty array if none, thankfully.
	$ancestors = get_post_ancestors( $page );

	// @todo Refactor with something like array_filter, maybe?
	foreach ( $ancestors as $ancestor_id ) {
		if ( in_array( (int) $ancestor_id, $excluded_ids, true ) ) {
			return $ancestor_id;
		}
	}

	// If we made it this far, no ancestors are excluded.
	return false;
}



/**
 * ------- ADMIN STUFF -----------
 */


/**
 * Add our metabox to Pages and load up some CSS and JS
 */
function bsn_ep_admin_init() {

	// Add panels into the editing sidebar(s)
	add_meta_box(
		'bsn_ep_admin_meta_box',
		__( 'Sectional Navigation', 'better-section-nav' ),
		'bsn_ep_admin_meta_box',
		'page',
		'side',
		'low'
	);

}
add_action( 'admin_init', 'bsn_ep_admin_init' );


/**
 * Get an array of all excluded IDs
 *
 * @return array List of all excluded page IDs.
 */
function bsn_get_excluded_ids() {
	return get_option( BSN_EP_OPTION_NAME, array() );
}


/**
 * Get all the exclusions out of the options table, update and re-save.
 *
 * @param int $post_id The ID of the post currently being saved.
 *
 * @return void
 */
function bsn_update_exclusions( $post_id ) {

	// If nonce fail, then default to including the page in the nav
	// (i.e. bomb out here rather than doing anything whatsoever)
	if ( ! isset( $_REQUEST['bsn_ep_nonce'] ) || ! wp_verify_nonce( $_REQUEST['bsn_ep_nonce'], 'bsn_ep_include' ) ) {
		return;
	}

	// Bang (!) to reverse the polarity of the boolean, turning include into exclude
	$exclude_this_page = ! isset( $_POST['bsn_page_included'] );

	$excluded_ids = bsn_get_excluded_ids();

	// If we need to EXCLUDE the page from the navigation...
	if ( $exclude_this_page && ! in_array( $post_id, $excluded_ids, true ) ) {

		// Add the post ID to the array of excluded IDs
		array_push( $excluded_ids, $post_id );

	} elseif ( ! $exclude_this_page && in_array( $post_id, $excluded_ids, true ) ) {

		// Find the post ID in the array of excluded IDs
		$index = array_search( $post_id, $excluded_ids, true );
		// Delete any index found
		if ( false !== $index ) {
			unset( $excluded_ids[ $index ] );
		}
	}

	// Update the option
	bsn_set_excluded_ids( BSN_EP_OPTION_NAME, $excluded_ids );
}
add_action( 'save_post_page', 'bsn_update_exclusions' );


/**
 * Update the excluded IDs list
 *
 * @param string $name The name of the option to update.
 * @param mixed  $value The value to store in the option.
 */
function bsn_set_excluded_ids( $name, $value ) {
	// Insert option
	update_option( $name, $value );
}


/**
 * Callback function for the metabox on the page edit screen.
 *
 * @return void
 */
function bsn_ep_admin_meta_box() {

	$nearest_excluded_ancestor = bsn_current_excluded_ancestor_id(); ?>

	<?php if ( $nearest_excluded_ancestor ) : ?>

		<p>
			<label for="bsn_page_included" class="selectit">
				<input type="checkbox" name="bsn_ancestor_included" id="bsn_ancestor_included" disabled="disabled" />
				<?php esc_html_e( 'Include this page in lists of pages', 'better-section-nav' ); ?>
			</label>
		</p>

		<p class="bsn_exclude_alert"><em>
			<?php
				printf(
					/* translators: placeholder is admin url for editing ancestor */
					wp_kses_post( __( 'Note: An ancestor of this page is excluded, so this page is too (<a href="%s" title="edit the excluded ancestor">edit ancestor</a>).', 'better-section-nav' ) ),
					esc_attr( admin_url( "post.php?action=edit&amp;post=$nearest_excluded_ancestor" ) )
				);
			?>
			</em>
		</p>

	<?php else : ?>

		<p>
			<label for="bsn_page_included" class="selectit">
				<input type="checkbox" name="bsn_page_included" id="bsn_page_included" <?php checked( true, bsn_current_page_included() ); ?> />
				<?php esc_html_e( 'Include this page in lists of pages', 'better-section-nav' ); ?>
			</label>
		</p>

		<?php wp_nonce_field( 'bsn_ep_include', 'bsn_ep_nonce' ); ?>

	<?php endif; ?>

	<p id="bsn_custom_menu_alert"><em>
	<?php
	if ( current_user_can( 'edit_theme_options' ) ) {
		printf(
			/* translators: placeholder is URL for edit menus screen */
			wp_kses_post( __( 'Regardless of this setting, this page can appear in explicitly created <a href="%s">menus</a>.', 'better-section-nav' ) ),
			esc_attr( admin_url( 'nav-menus.php' ) )
		);
	} else {
		esc_html_e( 'Note: This page can still appear in explicitly created menus.', 'better-section-nav' );
	}
	?>
	</em></p>

	<?php
}


/**
 * Checks if the currently-edited page has been excluded.
 *
 * @return bool Whether or not the page is already excluded.
 */
function bsn_current_page_included() {

	global $post;

	// New post? Include by default.
	if ( ! $post->ID ) {
		return true;
	}

	$excluded_ids = bsn_get_excluded_ids();
	// If there's an array of exclusions and we're in it, return true.
	if ( ! empty( $excluded_ids ) && in_array( (int) $post->ID, $excluded_ids, true ) ) {
		return false;
	} else {
		// Include by default
		return true;
	}

}


/**
 * Check the ancestors for the page we're editing (defined by global $post_ID var),
 * return the ID if the nearest one which is excluded (if any)
 *
 * @return bool|int Post ID of nearest ancestor, or false.
 */
function bsn_current_excluded_ancestor_id() {

	global $post, $wpdb;

	// New post? No problem.
	if ( ! $post->ID ) {
		return false;
	}

	$excluded_ids = bsn_get_excluded_ids();

	return bsn_is_ancestor_excluded( $post->ID, $excluded_ids );
}


/**
 * -------- Template Tags to selectively disable excluding pages -----
 */

// Make sure is_plugin_active() exists.
include_once( ABSPATH . 'wp-admin/includes/plugin.php' );

if ( ! function_exists( 'pause_exclude_pages' ) && ! is_plugin_active( 'exclude-pages/exclude_pages.php' ) ) {
	/**
	 * Template tag to stop exclusion, copied from Exclude Pages
	 */
	function pause_exclude_pages() {
		remove_filter( 'get_pages', 'bsn_exclude_pages' );
	}
}

if ( ! function_exists( 'resume_exclude_pages' ) && ! is_plugin_active( 'exclude-pages/exclude_pages.php' ) ) {
	/**
	 * Turn it back on.
	 */
	function resume_exclude_pages() {
		add_filter( 'get_pages', 'bsn_exclude_pages' );
	}
}


/**
 * Port settings over from https://wordpress.org/plugins/exclude-pages/
 */
function bsn_activate() {

	$current_bsn_pages = get_option( BSN_EP_OPTION_NAME, false );
	$old_ep_pages = get_option( 'ep_exclude_pages', false );

	// If our option doesn't exist, but the other plugin's does, convert them.
	if ( false === $current_bsn_pages && false !== $old_ep_pages ) {
		$excluded_ids = array_map( 'intval', explode( ',', $old_ep_pages ) );
		if ( count( $excluded_ids ) ) {
			add_option( BSN_EP_OPTION_NAME, $excluded_ids );
		}
	}

}
