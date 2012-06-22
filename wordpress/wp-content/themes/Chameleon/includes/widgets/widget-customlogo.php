<?php class CustomLogoWidget extends WP_Widget
{
    function CustomLogoWidget(){
		$widget_ops = array('description' => 'Displays Logo, Copyright and Additional Information');
		$control_ops = array('width' => 400, 'height' => 300);
		parent::WP_Widget(false,$name='ET Custom Logo Widget',$widget_ops,$control_ops);
    }

  /* Displays the Widget in the front-end */
    function widget($args, $instance){
		extract($args);
		$logoImagePath = empty($instance['logoImagePath']) ? '' : $instance['logoImagePath'];
		$textInfo = empty($instance['textInfo']) ? '' : $instance['textInfo'];

		echo $before_widget;
?>	
<p id="footer-logo"><img alt="" src="<?php echo esc_url($logoImagePath); ?>" /></p>
<p><?php echo $textInfo; ?></p>

<?php
		echo $after_widget;
	}

  /*Saves the settings. */
    function update($new_instance, $old_instance){
		$instance = $old_instance;
		$instance['logoImagePath'] = stripslashes($new_instance['logoImagePath']);
		$instance['textInfo'] = stripslashes($new_instance['textInfo']);

		return $instance;
	}

  /*Creates the form for the widget in the back-end. */
    function form($instance){
		//Defaults
		$instance = wp_parse_args( (array) $instance, array('logoImagePath'=>'', 'textInfo'=>'') );

		$logoImagePath = $instance['logoImagePath'];
		$textInfo = $instance['textInfo'];
		
		# Logo Image
		echo '<p><label for="' . $this->get_field_id('logoImagePath') . '">' . 'Logo Image URL (109x33px):' . '</label><textarea cols="20" rows="2" class="widefat" id="' . $this->get_field_id('logoImagePath') . '" name="' . $this->get_field_name('logoImagePath') . '" >'. esc_url($logoImagePath) .'</textarea></p>';
		# Text
		echo '<p><label for="' . $this->get_field_id('textInfo') . '">' . 'Text:' . '</label><textarea cols="20" rows="5" class="widefat" id="' . $this->get_field_id('textInfo') . '" name="' . $this->get_field_name('textInfo') . '" >'. esc_textarea($textInfo) .'</textarea></p>';
	}

}// end CustomLogoWidget class

function CustomLogoWidgetInit() {
  register_widget('CustomLogoWidget');
}

add_action('widgets_init', 'CustomLogoWidgetInit');

?>