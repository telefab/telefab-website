<?php
/**
 * Defines the class for the BSN Widget.
 */

/**
 * The main widget class.
 */
class Better_Section_Nav extends WP_Widget {

	/**
	 * Widget constructor.
	 */
	function __construct() {
		$widget_ops = array(
			'classname' => 'better-section-nav',
			'description' => __( 'Shows page ancestory (parents, grandparents, etc), siblings of ancestory and current page, and immediate children of the current page beneath the current top level page.', 'better-section-nav' ),
		);
		parent::__construct( 'better-section-nav', __( 'Better Section Navigation' ), $widget_ops );
	}

	/**
	 * Output a widget instance.
	 */
	function widget( $args, $instance ) {
		global $post;

		$current_page = $post;

		// Don't show on search or 404 pages.
		if ( is_search() || is_404() ) {
			return false;
		}

		// Don't show on the homepage if this instance is set not to display there.
		if ( is_front_page() && empty( $instance['show_on_home'] ) ) {
			return false;
		}

		if ( ! is_page() ) {
			if ( $post_page = get_option( 'page_for_posts' ) ) {	// phpcs:ignore
				// Treat the posts page as the current page if applicable.
				$current_page = get_page( $post_page );
			} elseif ( $instance['show_on_home'] ) {
				// If want to show on home, and home is the posts page.
				$sub_front_page = true;
			} else {
				return false;
			}
		}

		if ( is_front_page() || isset( $sub_front_page ) ) {
			echo $args['before_widget'] . $args['before_title'] . get_bloginfo( 'name', 'display' ) . $args['after_title']; // phpcs:ignore
			echo '<ul class="' . esc_attr( apply_filters( 'bsn_list_class', 'bsn-list' ) ) . '">';
			$children = wp_list_pages( array(
				'title_li' => '',
				'depth' => 1,
				'sort_column' => $instance['sort_by'],
				'exclude' => $instance['exclude'],
				'echo' => false,
			) );
			echo apply_filters( 'better_section_page_list', $children );	// phpcs:ignore
			echo '</ul>' . $args['after_widget'];	// phpcs:ignore
			return true;
		}

		$exclude_list = $instance['exclude'];
		// Convert list of excluded pages to array.
		$excluded = explode( ',', $exclude_list );
		if ( in_array( $current_page->ID, $excluded, true ) && $instance['hide_on_excluded'] ) {
			// If on excluded page, and setup to hide on excluded pages.
			return false;
		}
		// Get the current page's ancestors either from existing value or by executing function.
		$post_ancestors = get_post_ancestors( $current_page );
		// Get the top page id.
		$top_page = $post_ancestors ? end( $post_ancestors ) : $current_page->ID;

		// Initialize default variables.
		$thedepth = 0;

		if ( empty( $instance['show_all'] ) ) {
			$ancestors_me = implode( ',', $post_ancestors ) . ',' . $current_page->ID;

			// exclude pages not in direct hierarchy
			foreach ( $post_ancestors as $anc_id ) {
				if ( in_array( $anc_id, $excluded, true ) && $instance['hide_on_excluded'] ) {
					// If ancestor excluded, and hide on excluded, leave.
					return false;
				}
				$pageset = get_posts( array(
					'suppress_filters' => false,
					'post_parent' => $anc_id,
					'exclude' => $ancestors_me,
				) );
				foreach ( $pageset as $page ) {
					$excludeset = get_posts( array(
						'suppress_filters' => false,
						'post_parent' => $page->ID,
					) );
					foreach ( $excludeset as $expage ) {
						$exclude_list .= ',' . $expage->ID;
					}
				}
			}
			// Prevents improper grandchildren from showing.
			$thedepth = count( $post_ancestors ) + 1;
		}//end if

		// Get the list of pages, including only those in our page list.
		$children = wp_list_pages( array(
			'title_li' => '',
			'echo' => 0,
			'depth' => $thedepth,
			'child_of' => $top_page,
			'sort_column' => $instance['sort_by'],
			'exclude' => $exclude_list,
		) );

		// If there are no pages in this section, and use hasnt chosen to display widget anyways, leave the function.
		if ( ! $children && ! $instance['show_empty'] ) {
			return false;
		}

		$sect_title = ( $instance['title'] ) ? apply_filters( 'the_title', $instance['title'] ) : apply_filters( 'the_title', get_the_title( $top_page ), $top_page );
		$sect_title = apply_filters( 'better_section_nav_title', $sect_title );
		if ( ! empty( $instance['a_heading'] ) ) {
			$headclass = ( $current_page->ID === $top_page ) ? 'current_page_item' : 'current_page_ancestor';
			if ( $current_page->post_parent === $top_page ) {
				$headclass .= ' current_page_parent';
			}
			$sect_title = '<a href="' . get_page_link( $top_page ) . '" id="toppage-' . $top_page . '" class="' . $headclass . '">' . $sect_title . '</a>';
		}

		echo $args['before_widget'] . $args['before_title'] . $sect_title . $args['after_title'];	// phpcs:ignore
		echo '<ul class="' . esc_attr( apply_filters( 'bsn_list_class', 'bsn-list' ) ) . '">';
		echo apply_filters( 'better_section_page_list', $children ); // phpcs:ignore
		echo '</ul>' . $args['after_widget']; // phpcs:ignore
	}

	/**
	 * Update a widget instance.
	 */
	function update( $new_instance, $old_instance ) {
		$instance = $old_instance;
		$instance['title'] = trim( strip_tags( $new_instance['title'] ) );
		$instance['show_all'] = ! empty( $new_instance['show_all'] ) ? true : false;
		// remove spaces from list
		$instance['exclude'] = str_replace( ' ', '', strip_tags( $new_instance['exclude'] ) );
		$instance['hide_on_excluded'] = ! empty( $new_instance['hide_on_excluded'] ) ? true : false;
		$instance['show_on_home'] = ! empty( $new_instance['show_on_home'] ) ? true : false;
		$instance['show_empty'] = ! empty( $new_instance['show_empty'] ) ? true : false;
		$instance['sort_by'] = ( ! empty( $new_instance['sort_by'] ) && in_array( $new_instance['sort_by'], array( 'post_title', 'menu_order', 'ID' ), true ) ) ? $new_instance['sort_by'] : 'menu_order';
		$instance['a_heading'] = ! empty( $new_instance['a_heading'] ) ? true : false;
		return $instance;
	}

	/**
	 * Display a form with options for a widget instance.
	 */
	function form( $instance ) {
		// Defaults
		$instance = wp_parse_args( (array) $instance, array(
			'show_all'         => false,
			'exclude'          => '',
			'hide_on_excluded' => true,
			'show_on_home'     => false,
			'show_empty'       => false,
			'sort_by'          => 'menu_order',
			'a_heading'        => false,
			'title'            => '',
		) );
		?>
		<p>
			<label for="<?php echo esc_attr( $this->get_field_id( 'title' ) ); ?>"><?php esc_html_e( 'Override Title:' ); ?></label>
			<input type="text" id="<?php echo esc_attr( $this->get_field_id( 'title' ) ); ?>" name="<?php echo esc_attr( $this->get_field_name( 'title' ) ); ?>" value="<?php echo esc_attr( $instance['title'] ); ?>" size="7" class="widefat" /><br />
				<small>Leave blank to use top level page title.</small>
		</p>
		<p>
			<label for="<?php echo esc_attr( $this->get_field_id( 'sort_by' ) ); ?>"><?php esc_html_e( 'Sort pages by:' ); ?></label>
			<select name="<?php echo esc_attr( $this->get_field_name( 'sort_by' ) ); ?>" id="<?php echo esc_attr( $this->get_field_id( 'sort_by' ) ); ?>" class="widefat">
				<option value="post_title"<?php selected( $instance['sort_by'], 'post_title' ); ?>><?php esc_html_e( 'Page title' ); ?></option>
				<option value="menu_order"<?php selected( $instance['sort_by'], 'menu_order' ); ?>><?php esc_html_e( 'Page order' ); ?></option>
				<option value="ID"<?php selected( $instance['sort_by'], 'ID' ); ?>><?php esc_html_e( 'Page ID' ); ?></option>
			</select>
		</p>
		<p>
			<label for="<?php echo esc_attr( $this->get_field_id( 'exclude' ) ); ?>"><?php esc_html_e( 'Exclude:' ); ?></label>
			<input type="text" id="<?php echo esc_attr( $this->get_field_id( 'exclude' ) ); ?>" name="<?php echo esc_attr( $this->get_field_name( 'exclude' ) ); ?>" value="<?php echo esc_attr( $instance['exclude'] ); ?>" size="7" class="widefat" /><br />
			<small>Page IDs, separated by commas.</small>
		</p>
		<p>
			<input class="checkbox" type="checkbox" <?php checked( $instance['show_on_home'] ); ?> id="<?php echo esc_attr( $this->get_field_id( 'show_on_home' ) ); ?>" name="<?php echo esc_attr( $this->get_field_name( 'show_on_home' ) ); ?>" />
			<label for="<?php echo esc_attr( $this->get_field_id( 'show_on_home' ) ); ?>"><?php esc_html_e( 'Show on home page' ); ?></label><br />
			<input class="checkbox" type="checkbox" <?php checked( $instance['a_heading'] ); ?> id="<?php echo esc_attr( $this->get_field_id( 'a_heading' ) ); ?>" name="<?php echo esc_attr( $this->get_field_name( 'a_heading' ) ); ?>" />
			<label for="<?php echo esc_attr( $this->get_field_id( 'a_heading' ) ); ?>"><?php esc_html_e( 'Link heading (top level page)' ); ?></label><br />
			<input class="checkbox" type="checkbox" <?php checked( $instance['show_all'] ); ?> id="<?php echo esc_attr( $this->get_field_id( 'show_all' ) ); ?>" name="<?php echo esc_attr( $this->get_field_name( 'show_all' ) ); ?>" />
			<label for="<?php echo esc_attr( $this->get_field_id( 'show_all' ) ); ?>"><?php esc_html_e( 'Show all pages in section' ); ?></label><br />
			<input class="checkbox" type="checkbox" <?php checked( $instance['show_empty'] ); ?> id="<?php echo esc_attr( $this->get_field_id( 'show_empty' ) ); ?>" name="<?php echo esc_attr( $this->get_field_name( 'show_empty' ) ); ?>" />
			<label for="<?php echo esc_attr( $this->get_field_id( 'show_empty' ) ); ?>"><?php esc_html_e( 'Output even if empty section' ); ?></label><br />
			<input class="checkbox" type="checkbox" <?php checked( $instance['hide_on_excluded'] ); ?> id="<?php echo esc_attr( $this->get_field_id( 'hide_on_excluded' ) ); ?>" name="<?php echo esc_attr( $this->get_field_name( 'hide_on_excluded' ) ); ?>" />
			<label for="<?php echo esc_attr( $this->get_field_id( 'hide_on_excluded' ) ); ?>"><?php esc_html_e( 'No nav on excluded pages' ); ?></label>
		</p>
		<!-- p><small><a href="https://cornershopcreative.com/plugins/better-section-navigation/" target="_blank">Help &amp; Support</a></small></p -->
		<?php
	}
}
