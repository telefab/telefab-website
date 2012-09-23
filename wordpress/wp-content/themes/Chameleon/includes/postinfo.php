<?php if (!is_single() && get_option('chameleon_postinfo1') ) { ?>
	<p class="meta-info"><?php esc_html_e('Posted','Chameleon'); ?> <?php if (in_array('author', get_option('chameleon_postinfo1'))) { ?> <?php esc_html_e('by','Chameleon'); ?> <?php the_author_posts_link(); ?><?php }; ?><?php if (in_array('date', get_option('chameleon_postinfo1'))) { ?> <?php esc_html_e('on','Chameleon'); ?> <?php the_time(esc_attr(get_option('chameleon_date_format'))) ?><?php }; ?><?php if (in_array('categories', get_option('chameleon_postinfo1'))) { ?> <?php esc_html_e('in','Chameleon'); ?> <?php the_category(', ') ?><?php }; ?><?php if (in_array('comments', get_option('chameleon_postinfo1'))) { ?> | <?php comments_popup_link(esc_html__('0 comments','Chameleon'), esc_html__('1 comment','Chameleon'), '% '.esc_html__('comments','Chameleon')); ?><?php }; ?></p>
<?php } elseif (is_single() && get_option('chameleon_postinfo2') ) { ?>
	<p class="description">
		<?php global $query_string;
		$new_query = new WP_Query($query_string);
		while ($new_query->have_posts()) $new_query->the_post(); ?>
			<?php esc_html_e('Posted','Chameleon'); ?> <?php if (in_array('author', get_option('chameleon_postinfo2'))) { ?> <?php esc_html_e('by','Chameleon'); ?> <?php the_author_posts_link(); ?><?php }; ?><?php if (in_array('date', get_option('chameleon_postinfo2'))) { ?> <?php esc_html_e('on','Chameleon'); ?> <?php the_time(esc_attr(get_option('chameleon_date_format'))) ?><?php }; ?><?php if (in_array('categories', get_option('chameleon_postinfo2'))) { ?> <?php esc_html_e('in','Chameleon'); ?> <?php the_category(', ') ?><?php }; ?><?php if (in_array('comments', get_option('chameleon_postinfo2'))) { ?> | <?php comments_popup_link(esc_html__('0 comments','Chameleon'), esc_html__('1 comment','Chameleon'), '% '.esc_html__('comments','Chameleon')); ?><?php }; ?>
		<?php wp_reset_postdata() ?>
	</p>
<?php }; ?>