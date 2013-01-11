<?php class ETFromBlogWidget extends WP_Widget
{
    function ETFromBlogWidget(){
		$widget_ops = array('description' => 'Displays Posts from the Blog category');
		$control_ops = array('width' => 400, 'height' => 300);
		parent::WP_Widget(false,$name='ET From The Blog Widget',$widget_ops,$control_ops);
    }

  /* Displays the Widget in the front-end */
    function widget($args, $instance){
		extract($args);
		$title = apply_filters('widget_title', empty($instance['title']) ? 'From The Blog' : $instance['title']);
		$posts_number = empty($instance['posts_number']) ? '' : $instance['posts_number'];
		$blog_category = empty($instance['blog_category']) ? '' : $instance['blog_category'];

		echo $before_widget;

		if ( $title )
		echo $before_title . $title . $after_title;
?>	
	<ul>
		<?php query_posts("showposts=".$posts_number."&cat=".$blog_category);
		if (have_posts()) : while (have_posts()) : the_post(); ?>
			<li><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></li>
		<?php endwhile; endif; wp_reset_query(); ?>
	</ul> <!-- end ul.nav -->
<?php
		echo $after_widget;
	}

  /*Saves the settings. */
    function update($new_instance, $old_instance){
		$instance = $old_instance;
		$instance['title'] = stripslashes($new_instance['title']);
		$instance['posts_number'] = (int) $new_instance['posts_number'];
		$instance['blog_category'] = (int) $new_instance['blog_category'];

		return $instance;
	}

  /*Creates the form for the widget in the back-end. */
    function form($instance){
		//Defaults
		$instance = wp_parse_args( (array) $instance, array('title'=>'From The Blog', 'posts_number'=>'7', 'blog_category'=>'') );

		$title = htmlspecialchars($instance['title']);
		$posts_number = (int) $instance['posts_number'];
		$blog_category = $instance['blog_category'];

		# Title
		echo '<p><label for="' . $this->get_field_id('title') . '">' . 'Title:' . '</label><input class="widefat" id="' . $this->get_field_id('title') . '" name="' . $this->get_field_name('title') . '" type="text" value="' . esc_attr($title) . '" /></p>';
		# Number Of Posts
		echo '<p><label for="' . $this->get_field_id('posts_number') . '">' . 'Number of Posts:' . '</label><input class="widefat" id="' . $this->get_field_id('posts_number') . '" name="' . $this->get_field_name('posts_number') . '" type="text" value="' . esc_attr($posts_number) . '" /></p>';
		# Category ?>
		<?php 
			$cats_array = get_categories('hide_empty=0');
		?>
		<p>
			<label for="<?php echo $this->get_field_id('blog_category'); ?>">Category</label>
			<select name="<?php echo $this->get_field_name('blog_category'); ?>" id="<?php echo $this->get_field_id('blog_category'); ?>" class="widefat">
				<?php foreach( $cats_array as $category ) { ?>
					<option value="<?php echo $category->cat_ID; ?>"<?php selected( $instance['blog_category'], $category->cat_ID ); ?>><?php echo $category->cat_name; ?></option>
				<?php } ?>
			</select>
		</p> 
		<?php
	}

}// end ETFromBlogWidget class

function ETFromBlogWidgetInit() {
  register_widget('ETFromBlogWidget');
}

add_action('widgets_init', 'ETFromBlogWidgetInit');

?>