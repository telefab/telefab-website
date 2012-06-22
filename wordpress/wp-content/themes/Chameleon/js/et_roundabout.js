jQuery(document).ready(function(){
	var	et_featured_slider_auto = jQuery("meta[name=et_featured_slider_auto]").attr('content'),
	et_featured_auto_speed = jQuery("meta[name=et_featured_auto_speed]").attr('content');
	
	var $featured_slider = jQuery('#featured-modest'),
	$featured_slides = $featured_slider.find('.slide'),
	slides_pos = [],
	slides_zindex = [],
	et_animation_running = false,
	pause_scroll = false,
	featured_animation = 'easeInOutQuad'; //'easeInOutQuad','easeInOutQuint', 'easeInOutQuart'
	
	$featured_slider.css('backgroundImage','none');
	
	if ($featured_slider.length) {
		$featured_slides.css('display','block').each(function(index, domEle){ 
			var $this_slide = jQuery(domEle);
			
			if ( index === 0 ) { 
				$this_slide.find('a.main img').attr({
					width: '462',
					height: '306'
				});
				$this_slide.find('img.bottom-shadow').attr('width','462');
			} else { 
				$this_slide.find('a.main img').attr({
					width: '354',
					height: '234'
				});
				$this_slide.find('img.bottom-shadow').attr('width','354');
			}
			
			slides_pos[index] = {
				width: $this_slide.width(),
				top: parseInt($this_slide.css('top')),
				left: parseInt($this_slide.css('left')),
				opacity: $this_slide.css('opacity')
			};
			slides_zindex[index] = $this_slide.css('zIndex');
			$this_slide.animate(slides_pos[index],100);
			
			jQuery(domEle).data('slide_pos',index);
		});
		
		jQuery('.next-block a').live('click',function(event){
			event.preventDefault();
			if (!et_animation_running) rotate_slide('next');
			if ( typeof(et_auto_animation) !== 'undefined' ) clearInterval(et_auto_animation);
		});
		
		jQuery('.prev-block a').live('click',function(event){
			event.preventDefault();
			if (!et_animation_running) rotate_slide('prev');
			if ( typeof(et_auto_animation) !== 'undefined' ) clearInterval(et_auto_animation);
		});
					
		$featured_slides.hover(function(){
			if ( !et_animation_running ) {
				if ( jQuery(this).hasClass('active-block') )
					jQuery(this).find('.featured-link').stop(true, true).animate({'opacity':'show'},300);
				else {
					jQuery(this).find('.gotoslide').stop(true, true).animate({'opacity':'show'},300);
				}
			}
			pause_scroll = true;
		},function(){
			if ( !et_animation_running ) {
				if ( jQuery(this).hasClass('active-block') )
					jQuery(this).find('.featured-link').stop(true, true).animate({'opacity':'hide'},300);
				else {
					jQuery(this).find('.gotoslide').stop(true, true).animate({'opacity':'hide'},300);
				}
			}
			pause_scroll = false;
		});
		
		jQuery('.active-block').live('click',function(event){
			window.location = jQuery(this).find('a.main').attr('href');
		});
		
		function rotate_slide(direction){
			et_animation_running = true;
			
			jQuery('.gotoslide').css('display','none');
			
			$featured_slides.removeClass('active-block');
			$featured_slides.removeClass('next-block');
			$featured_slides.removeClass('prev-block');
			
			$featured_slides.each(function(index, domEle){
				var $this_slide = jQuery(domEle),
					next_slide_num = $this_slide.data('slide_pos');
					
				if ( direction === 'next' ){
					if ( next_slide_num === 0 ) next_slide_num = $featured_slides.length-1;
					else next_slide_num = next_slide_num - 1;
				} else {
					next_slide_num = next_slide_num + 1;
					if ( next_slide_num === $featured_slides.length ) next_slide_num = 0;
				}
				
				$this_slide.stop(true, true).animate(slides_pos[next_slide_num],600,featured_animation);
				if ( next_slide_num != 0 ) {
					$this_slide.find('a.main img').stop(true, true).animate({'width':'354px','height':'234px'},600,featured_animation);
					$this_slide.find('img.bottom-shadow').stop(true, true).animate({'width':'354px'},600,featured_animation);
				}
				else { 
					$this_slide.addClass('active-block');
					$this_slide.find('a.main img').stop(true, true).animate({'width':'462px','height':'306px'},600,featured_animation);
					$this_slide.find('img.bottom-shadow').stop(true, true).animate({'width':'462px'},600,featured_animation);
				}
				
				if ( next_slide_num === 1 ) $this_slide.addClass('next-block');
				if ( next_slide_num === ($featured_slides.length-1) ) $this_slide.addClass('prev-block');
				
				setTimeout(function(){
					$this_slide.css({zIndex: slides_zindex[next_slide_num]});
				},300);
									
				$this_slide.data('slide_pos',next_slide_num);
			});
			
			et_animation_running = false;
		}
		
		if ( et_featured_slider_auto == 1 ) {
			et_auto_animation = setInterval(function(){
				if ( !pause_scroll ) rotate_slide('next');
			}, et_featured_auto_speed);
		}
	}
});