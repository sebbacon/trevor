<?php get_header(); ?>

<div class="navigation_group">
	<?php next_posts_link('<div class="eachpost "><div>&mdash;Older</div></div>') ?>
	<?php previous_posts_link('<div class="eachpost "><div>Newer&mdash;</div></div>') ?>
</div>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>
	<?php 
			
			$upload_path = get_option( 'upload_path' );
			$upload_path = trim($upload_path);
			
			$img_full_url = post_image();
		
			if ($img_full_url != "") {	
				
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
					<div>'; ?>
		
			<?php  if ( $img_full_url != "" ) {
					echo '<img src="' . $img_full_url . '" width="' . $new_width . '" height="' . $new_height . '" /><br /><br />'; } 
					
			} else { 
				echo '<div class="eachpost ">
						<div>'; } ?>

			<a href="<?php the_permalink() ?>" rel="bookmark"><?php the_title(); ?></a>

			<div class="contentIndex"><?php 

			ob_start();
   			the_content('Read the full post',true);
  			$postOutput = preg_replace('/<img[^>]+./','', ob_get_contents());
   			$postOutput = str_replace('<div class="eachpost "><div></div></div>','',$postOutput);
   			$postOutput = str_replace('<div class="eachpost twocols"><div></div></div>','',$postOutput);
  			$postOutput = str_replace('<div class="eachpost threecols"><div></div></div>','',$postOutput);
	   
   			ob_end_clean();
   			echo $postOutput; ?>
   			
   			</div>

			<small>
			
			<?
			
			
			?>
			
			<a href="<?php comments_link(); ?>"><?php comments_number('','1 Comment','% Comments'); ?></a></small>

  	 </div>
  </div> 
    
    <?php if ( comments_open() ) comments_template(); ?>

<?php endwhile; else: ?>
<div class="warning">
	<p>Sorry, but you are looking for something that isn't here.</p>
</div>
<?php endif; ?>

<div class="navigation_group">
	<?php next_posts_link('<div class="eachpost "><div>&mdash;Older</div></div>') ?>
	<?php previous_posts_link('<div class="eachpost "><div>Newer&mdash;</div></div>') ?>
</div>

    <?php get_footer(); ?>

    
