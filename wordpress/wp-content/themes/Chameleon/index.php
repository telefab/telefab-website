<?php get_header(); ?>

<?php get_template_part('includes/breadcrumbs'); ?>

<?php get_template_part('/includes/top_info'); ?>

<div id="content" class="clearfix">
	<div id="left-area">
		<?php get_template_part('includes/entry'); ?>
	</div> 	<!-- end #left-area -->

	<?php get_sidebar(); ?>
</div> <!-- end #content -->

<?php get_footer(); ?>