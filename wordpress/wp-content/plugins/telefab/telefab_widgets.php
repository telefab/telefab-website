<?php
// Custom widgets

class PlaceOpenNow extends WP_Widget {
    
	/**
	 * Sets up the widgets name etc
	 */
	public function __construct() {
		$widget_ops = array( 
			'classname' => "PlaceOpenNow",
			'description' => "Affichage de l'état du Téléfab de Brest (ouvert ou non)",
		);
		parent::__construct( 'PlaceOpenNow', 'Téléfab ouvert', $widget_ops );
	}

	function widget($args, $instance)
    {
        global $wpdb;
        extract($args);
    	echo $before_widget;
    	echo $before_title."Horaires d'ouverture".$after_title;
    	// Get the state of the place
        $places = $wpdb->get_results("SELECT id FROM main_placeopening WHERE start_time <= NOW() AND (end_time IS NULL OR end_time > NOW()) AND place_id = 1 LIMIT 1");
    	$now_open = sizeof($places) > 0;
    	echo "<p>";
    	echo "La salle de Brest du Téléfab est actuellement ";
    	if ($now_open)
    		echo "<span class=\"place_open\">ouverte</span>";
    	else
    		echo "<span class=\"place_closed\">fermée</span>";
    	echo ".";
    	echo "</p>";
        echo "<p><a href=\"/calendrier/\">Les ouvertures prévues sont dans le calendrier</a>.</p>";
    	echo $after_widget;
    }
 
    function update($new_instance, $old_instance)
    {
    }
 
    function form($instance)
    {
    }
}

add_action('widgets_init', function() { return register_widget("PlaceOpenNow"); });

?>