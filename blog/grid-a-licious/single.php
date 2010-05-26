<?php get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>

<div class="eachpost ">
	<div>
		<?php the_title(); ?>
	</div>
</div>	

	<?php 
		$content = get_the_content($more_link_text, $stripteaser, $more_file);
		$content = apply_filters('the_content', $content);
		$content = preg_replace('/<img[^>]+./','', $content);
		$content = str_replace('<p>','',$content);
		$content = str_replace('</p>','<br /><br />',$content);		
		$content = str_replace('<div class="eachpost "><div></div></div>','',$content);
		$content = str_replace('<div class="eachpost twocols"><div></div></div>','',$content);
		$content = str_replace('<div class="eachpost threecols"><div></div></div>','',$content);
		$content = str_replace(']]>', ']]&gt;', $content);
	?>
	<div class="eachpost twocols">
		<div>
       		<h1><?php the_title(); ?></h1>

			<div class="published">Published on <?php the_time('M d, Y'); ?> <?php _e("at"); ?> <?php the_time('g:i a'); ?></em></div>
			<div class="post"><?php echo $content; ?></div>

			<hr />
			Filed under: <?php the_category(',') ?> <?php the_tags('Tags:', ', ', ''); ?> | 


		</div>
	</div>

<div class="main">
	<?php 
		$imgcontent = get_the_content($more_link_text, $stripteaser, $more_file);
		$imgcontent = apply_filters('the_content', $imgcontent);
		$imgcontent = preg_replace('/<p[^>]+./','', $imgcontent);
		$imgcontent = str_replace('<p>','',$imgcontent);
		$imgcontent = str_replace('</p>','',$imgcontent);

		if ( strstr($imgcontent,'<div class="eachpost')) {
			echo $imgcontent; 
		} else {
		
			// gallery not found;
			
			$images = explode("<img ", $imgcontent);			
			if (count($images) != "1") {			
			for ($i=0;$i<count($images);$i++) {
			
				if ($images[$i] != "") {
					$image = str_replace('<img ','<div class="eachpost "><div><img ','<img '.$images[$i]);
					$imagepieces = explode("/>", $image);
					$imageurl = substr($imagepieces[0], 0, -2) . '" /></div></div>';
					
					$imagesrc_temp = explode('src="', $imageurl);
					$imagesrc = explode('"', $imagesrc_temp[1]); // get src
					
					$imagew_temp = explode('width="', $imageurl);
					$imagew = explode('"', $imagew_temp[1]); // get width
					
					$imageh_temp = explode('height="', $imageurl);
					$imageh = explode('"', $imageh_temp[1]); // get height
				
					$upload_path = get_option( 'upload_path' );
					$upload_path = trim($upload_path);
					$img_full_url = $imagesrc[0];

					$temp = substr(strrchr($upload_path, "/"), 1);
			
					list($url, $filename) = explode($temp, $img_full_url);
			
					$img_url = $upload_path . "/" . $filename;
			
					$imagesize = getimagesize($img_url);
					list($width, $height, $type, $attr) = getimagesize($img_url);
					$theClass = "eachpost ";
					if ( $width < "440" ) { $new_width = "200"; $theClass = "eachpost "; } 
						else if ( $width < "660" ) { $new_width = "430"; $theClass = "eachpost twocols"; }
							else { $new_width = "660"; $theClass = "eachpost threecols"; }
			
					$new_height = ($height*$new_width)/$width;

					echo '<div class="'.$theClass.'">
					<div>';
					
					echo '<img src="' . $img_full_url . '" width="' . $new_width . '" height="' . $new_height . '" /></div></div>'; }
		
					
				}
			}
		}	
		?>
</div>


<div class="eachpost twocols">
	<div>
   		<?php if ( comments_open() ) comments_template(); ?>
	</div>
</div>   

<?php endwhile; else: ?>
<div class="warning">
	<p>Sorry, but you are looking for something that isn't here.</p>
</div>
<?php endif; ?>

<div class="navigation_group">
	<div class="alignleft"><?php next_posts_link('&laquo; Older Entries') ?></div>
	<div class="alignright"><?php previous_posts_link('Newer Entries &raquo;') ?></div>
</div>

    <?php get_footer(); ?>

    