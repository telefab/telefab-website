<?php
/* This page hooks into the Manage Series page that was automatically added by WordPress custom-taxonomy
*/

//hook into the edit columns on "manage series" page
add_filter('manage_edit-'.ppseries_get_series_slug().'_columns', 'manage_series_columns');
add_filter('manage_'.ppseries_get_series_slug().'_custom_column', 'manage_series_columns_action',1,3);
add_action(''.ppseries_get_series_slug().'_edit_form_fields','edit_series_form_fields', 10,2);
add_action(''.ppseries_get_series_slug().'_add_form_fields', 'add_series_form_fields', 10);
//hooking into insert_term, update_term and delete_term
add_action('created_'.ppseries_get_series_slug().'', 'wp_insert_series', 10, 2);
add_action('edited_'.ppseries_get_series_slug().'', 'wp_update_series', 10, 2);
add_action('delete_'.ppseries_get_series_slug().'', 'wp_delete_series', 10, 2);

// note following function WILL NOT delete the actual image file from the server.  I don't think it's needed at this point.
function wp_delete_series($series_ID, $taxonomy_id) {
	global $wpdb;
	seriesicons_delete($series_ID);
	wp_reset_series_order_meta_cache('',$series_ID,TRUE);
}

function wp_insert_series($series_id, $taxonomy_id) {
	global $_POST;
	$series_icon_loc = '';

	extract($_POST, EXTR_SKIP);
	$series_icon = isset($_POST['series_icon_loc']) ? sanitize_text_field($_POST['series_icon_loc']) : null;

	if ( isset($series_icon) || $series_icon != '' ) {
		$build_path = seriesicons_url();
		$series_icon = str_replace($build_path, '', $series_icon);
	}

	$series_icon = seriesicons_write($series_id, $series_icon);
}

function wp_update_series($series_id, $taxonomy_id) {
	global $_POST;
	extract($_POST, EXTR_SKIP);
	if ( empty($series_icon_loc) ) $series_icon_loc = '';
	if ( empty($delete_image) ) $delete_image = false;

	$series_icon = $series_icon_loc;

	if ( !empty($series_icon) || $series_icon != '' ) {
		$build_path = seriesicons_url();
		$series_icon = str_replace($build_path, '', $series_icon);

	}

	if ($delete_image) {
		seriesicons_delete(absint($series_id));
	} else {
		$series_icon = seriesicons_write(absint($series_id), sanitize_text_field($series_icon));
	}
}

function manage_series_columns($columns) {
	global $orgseries, $pagenow;
	$columns['icon'] = __('Icon', 'organize-series');
	$columns['series_id'] = __('ID', 'organize-series');
	return $columns;
}

function manage_series_columns_action($content, $column_name, $id) {
	global $orgseries;
	$output = $content;	
	if ($column_name == 'icon') {
		
		if ( $series_icon = series_get_icons($id)) {
			$series_url = seriesicons_url();
			$icon = $series_url . $series_icon;
			$output .= '<img src="' . $icon . '" title="' . $series_icon . '" width="50" alt="' . $icon . '" />';
		} else {
			$output .= __('No Series Icon', 'organize-series');
		}
		
	}

	if ($column_name === 'series_id') {
		$output .= $id;
	}
	
	return $output;
}

function add_series_form_fields($taxonomy) {
	global $orgseries;
	?>
	<div class="form-field">
		<div style="float:left;" id="selected-icon"></div>
		<div style="clear:left;"></div>
		<label for="series_icon">
			<input id="series_icon_loc_display" type="text" style="width: 70%;" name="series_icon_loc_display" value="" disabled="disabled" /><input style="float:right; width: 100px;" id="upload_image_button" type="button" value="Select Image" />
			<input id="series_icon_loc" type="hidden" name="series_icon_loc" />
			<p><?php _e('Upload an image for the series.', 'organize-series') ?></p>
		</label>
	</div>
	<?php
}

function edit_series_form_fields($series, $taxonomy) {
	global $orgseries;
	$series_icon = get_series_icon('fit_width=100&fit_height=100&link=0&expand=true&display=0&series='.$series->term_id);
	$icon_loc = series_get_icons($series->term_id);
	if ($icon_loc || $icon_loc != ''){
		$series_icon_loc = seriesicons_url() . $icon_loc;
    }else{
	    $series_icon_loc = '';
    }

	?>
			<tr valign="top">
				<?php if ( $series->term_id != '' ) { ?>
				<th scope="row"><?php _e('Current series icon:', 'organize-series'); ?></th><?php } ?>
				<td>
					<?php if ($series_icon != '') {
                            // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
							echo $series_icon;
						} else {
							echo '<p>'. esc_html__('No icon currently', 'organize-series') .'</p>';
						}
					 ?>
					<div id="selected-icon"></div>
				</td>
			</tr>
			<?php if ( $series_icon != '' ) { ?>
			<tr>
				<th></th>
				<td>
				<p style="width: 50%;"><input style="margin-top: 0px;" name="delete_image" id="delete_image" type="checkbox" value="true" />  <?php _e('Delete image? (note: there will not be an image associated with this series if you select this)', 'organize-series'); ?></p>
				</td>
			</tr>
			<?php } ?>
			<tr valign="top">
				<th scope="row"><?php _e('Series Icon Upload:', 'organize-series') ?></th>
				<td><label for="series_icon">
					<input id="series_icon_loc_display" type="text" size="36" name="series_icon_loc_display" value="" disabled="disabled"/>
					<input id="upload_image_button" type="button" value="Select Image" />
					<p><?php _e('Upload an image for the series.', 'organize-series'); ?></p>
					<input id="series_icon_loc" type="hidden" name="series_icon_loc" />
					</label>
				</td>
			</tr>
	<?php
}  
?>