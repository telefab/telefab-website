<?php
// Custom widgets

class PlaceOpenNow extends WP_Widget {
    
	function PlaceOpenNow() {
		parent::WP_Widget(false, $name = 'Téléfab ouvert', array("description" => "Affichage de l'état du Téléfab de Brest (ouvert ou non)"));
	}

	function widget($args, $instance)
    {
        global $wpdb;
        extract($args);
    	echo $before_widget;
    	echo $before_title."Horaires d'ouverture".$after_title;
    	// Get the state of the place
        $places = $wpdb->get_results("SELECT now_open FROM main_place");
    	$now_open = $places[0]->now_open;
    	echo "<p>";
    	echo "Le Téléfab Brest est actuellement ";
    	if ($now_open)
    		echo "<span class=\"place_open\">ouvert</span>";
    	else
    		echo "<span class=\"place_closed\">fermé</span>";
    	echo ".";
    	echo "</p>";
        echo "<p><a href=\"/lab/calendrier\">Les ouvertures prévues sont dans le calendrier</a>.</p>";
    	echo $after_widget;
    }
 
    function update($new_instance, $old_instance)
    {
    }
 
    function form($instance)
    {
    }
}

add_action('widgets_init', create_function('', 'return register_widget("PlaceOpenNow");'));

?>