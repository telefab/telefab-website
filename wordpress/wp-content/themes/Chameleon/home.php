<?php get_header(); ?>

<?php if ( get_option('chameleon_featured') == 'on' ) get_template_part('includes/featured'); ?>		

<?php if ( get_option('chameleon_quote') == 'on' ) { ?>
	<div id="category-name"> 
		<div id="category-inner"> 
		<?php if ( get_option('chameleon_quote_one') <> '' ) { ?>
			<h3>"<?php echo esc_html(get_option('chameleon_quote_one')); ?>"</h3>
		<?php } ?>
		<?php if ( get_option('chameleon_quote_two') <> '' ) { ?>
			<p><?php echo esc_html(get_option('chameleon_quote_two')); ?></p>
		<?php } ?>	
        </div>
	</div> <!-- end .category-name -->
<?php } ?>

<div id="content-area">

	<?php if ( get_option('chameleon_blog_style') == 'false' ) { ?>
	
		<?php if ( get_option('chameleon_display_blurbs') == 'on' ){ ?>
			<div id="services" class="clearfix">
				<?php for ($i=1; $i <= 3; $i++) { ?>
					<?php query_posts('page_id=' . get_pageId(html_entity_decode(get_option('chameleon_home_page_'.$i)))); while (have_posts()) : the_post(); ?>
						<?php 
							global $more; $more = 0;
						?>
						<div class="service<?php if ( $i == 3 ) echo ' last'; ?>">
							<h3 class="title"><?php the_title(); ?></h3>
							
							<?php
								$thumb = '';
								$width = 232;
								$height = 117;
								if ( 'on' == get_option('chameleon_responsive_layout') ){
									$width = 376;
									$height = 160;
								}
								$classtext = 'item-image';
								$titletext = get_the_title();
								$thumbnail = get_thumbnail($width,$height,$classtext,$titletext,$titletext,false,'etservice');
								$thumb = $thumbnail["thumb"];
								$et_service_link = get_post_meta($post->ID,'etlink',true) ? get_post_meta($post->ID,'etlink',true) : get_permalink();
							?>
							<?php if ( $thumb <> '' ) { ?>
								<div class="thumb">
									<a href="<?php echo $et_service_link; ?>">
										<?php print_thumbnail($thumb, $thumbnail["use_timthumb"], $titletext, $width, $height, $classtext); ?>
										<span class="more-icon"></span>
									</a>
								</div> <!-- end .thumb -->
							<?php } ?>
							
							<?php the_content(''); ?>
						</div> <!-- end .service -->
					<?php endwhile; wp_reset_query(); ?>
				<?php } ?>
			</div> <!-- end #services -->
		<?php } ?>
		
		<div id="from-blog">			
			<?php if ( !function_exists('dynamic_sidebar') || !dynamic_sidebar('Homepage') ) : ?> 
			<?php endif; ?>
		</div> <!-- end #from-blog -->
		
		<?php if ( get_option('chameleon_display_media') == 'on' ) { ?>
			<div id="multi-media-bar">
				<h3 class="title"><?php esc_html_e('Multi Media Bar','Chameleon'); ?></h3>
				<div id="et-multi-media" class="clearfix">
					<a id="left-multi-media" href="#"><?php esc_html_e('Previous','Chameleon'); ?></a>
					<a id="right-multi-media" href="#"<?php esc_html_e('Next','Chameleon'); ?>></a>
					<div id="media-slides">
						<?php 
							$args=array(
								'showposts' => (int) get_option('chameleon_posts_media'),
								'category__not_in' => (array) get_option('chameleon_exlcats_media')
							);
							query_posts($args);
							$media_current_post = 1;
							$media_open = false;
							$et_videos_output = '';
						?>
						<?php if (have_posts()) : while (have_posts()) : the_post(); ?>
							<?php 
								$width = 48;
								$height = 48;
								$titletext = get_the_title();
								$thumbnail = get_thumbnail($width,$height,'multi-media-image',$titletext,$titletext,true,'Media');
								$thumb = $thumbnail["thumb"];
								$et_medialink = get_permalink($post->ID);
								$et_videolink = '';
								$et_media_description = get_post_meta($post->ID,'et_media_description',true) ? get_post_meta($post->ID,'et_media_description',true) : truncate_post(90,false);
							?>
							<?php if ( $media_current_post == 1 || ($media_current_post - 1) % 7 == 0 ) { 
								$media_open = true; ?>
								<div class="media-slide">
							<?php } ?>
									<div class="thumb<?php if ( $media_current_post % 7 == 0 ) echo ' last'; ?>">
										<?php if ( $et_medialink <> '' ) { ?>
											<a href="<?php echo esc_url($et_medialink); ?>">
										<?php } elseif ( $et_videolink <> '' ) { ?>
											<?php
												global $wp_embed;
												$et_video_id = 'et_video_post_' . $post->ID;
												$et_videos_output .= '<div id="'. esc_attr( $et_video_id ) .'">' . apply_filters( 'the_content', $wp_embed->shortcode( '', $et_videolink ) ) . '</div>';
											?>
											
											<a href="<?php echo esc_url( '#' . $et_video_id ); ?>" class="et-video fancybox" title="<?php echo esc_attr( $titletext ); ?>">
										<?php } else { ?>
											<a href="<?php echo esc_attr($thumbnail["fullpath"]); ?>" rel="media" class="fancybox" title="<?php echo esc_attr($titletext); ?>">
										<?php } ?>
												<?php print_thumbnail($thumb, $thumbnail["use_timthumb"], $titletext, $width, $height, 'multi-media-image'); ?>
											</a>
										<div class="media-description">
											<p><?php echo $et_media_description; ?></p>
											<span class="media-arrow"></span>
										</div>
									</div> 	<!-- end .thumb -->
							<?php if ( $media_current_post % 7 == 0 ) { 
								$media_open = false; ?>
								</div> <!-- end .media-slide -->
							<?php } ?>
							
							<?php $media_current_post++;
						endwhile; ?>
						<?php endif; wp_reset_query(); ?>
						
						<?php if ( $media_open ) { ?>
							</div> <!-- end .media-slide -->
						<?php } ?>
					</div> <!-- end #media-slides -->
				</div> <!-- end #et-multi-media -->
			</div> <!-- end #multi-media-bar -->
			
			<?php if ( '' != $et_videos_output ) echo '<div class="et_embedded_videos">' . $et_videos_output . '</div>'; ?>
		<?php } ?>
			
		<div class="clear"></div>
		
	<?php } else { ?>
		<div id="left-area">
			<?php get_template_part('includes/entry','home'); ?>
		</div> 	<!-- end #left-area -->

		<?php get_sidebar(); ?>
		<div class="clear"></div>
	<?php } ?>
	
</div> <!-- end #content-area -->

<?php get_footer(); ?>