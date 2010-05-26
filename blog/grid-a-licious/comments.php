<?php // Do not delete these lines
	if ('comments.php' == basename($_SERVER['SCRIPT_FILENAME']))
		die ('Please do not load this page directly. Thanks!');

	if (!empty($post->post_password)) { // if there's a password
		if ($_COOKIE['wp-postpass_' . COOKIEHASH] != $post->post_password) {  // and it doesn't match the cookie
			?>
<p class="nocomments">This post is password protected. Enter the password to view comments.
<p>

			<?php
			return;
		}
	}

	/* This variable is for alternating comment background */
	$oddcomment = 'alt';
?>

<!-- You can start editing here. -->


<div id="contentbox2">
<?php comments_number(__(''), __('1 Comment'), __('% Comments')); ?>
<br /><br /></div>


<div id="contentboxComments">
<?php if ($comments) : ?>

	<?php foreach ($comments as $comment) : ?>
<div class="<?php echo $oddcomment; ?> bubble" id="comment-<?php comment_ID() ?>">
	<blockquote><?php comment_text() ?></blockquote>
	<small><?php comment_author_link() ?> added these words on <a href="#comment-<?php comment_ID() ?>" title=""><?php comment_date('M d y') ?> at <?php comment_time() ?></a> <?php edit_comment_link('e','',''); ?>
	</small>
			<?php if ($comment->comment_approved == '0') : ?>
	<em>Your comment is awaiting moderation.</em>
			<?php endif; ?>
</div>

	<?php /* Changes every other comment to a different class */
		if ('alt' == $oddcomment) $oddcomment = '';
		else $oddcomment = 'alt';
	?>

	<?php endforeach; /* end for each comment */ ?>


 <?php else : // this is displayed if there are no comments so far ?>

	<?php if ('open' == $post->comment_status) : ?>
		<!-- If comments are open, but there are no comments. -->

	 <?php else : // comments are closed ?>
		<!-- If comments are closed. -->
<p class="nocomments">Comments are closed.</p>

	<?php endif; ?>
<?php endif; ?>


<?php if ('open' == $post->comment_status) : ?>

<?php if ( get_option('comment_registration') && !$user_ID ) : ?>
<p>You must be <a href="<?php echo get_option('siteurl'); ?>/wp-login.php?redirect_to=<?php the_permalink(); ?>">logged in</a> to post a comment.
</p>
<?php else : ?>
<form action="<?php echo get_option('siteurl'); ?>/wp-comments-post.php" method="post" id="commentform">

<?php if ( $user_ID ) : ?>
<p></p>
<?php else : ?>
	<p>
		<input type="text" name="author" id="author" value="Name" size="22" tabindex="1" />
	
		<input type="text" name="email" id="email" value="Mail (Required)" size="22" tabindex="2" />
	
		<input type="text" name="url" id="url" value="Website" size="22" tabindex="3" />
	</p>

<?php endif; ?>

<!--<p><small><strong>XHTML:</strong> You can use these tags: <?php echo allowed_tags(); ?></small></p>-->
	<textarea name="comment" id="comment" cols="100%" rows="10" tabindex="4"></textarea>
			<br /><br /><input name="submit" type="image" style="width: 74px; height:24px;" id="submit" tabindex="5" value="Post Comment" />
		<input type="hidden" name="comment_post_ID" value="<?php echo $id; ?>" />
	
<?php do_action('comment_form', $post->ID); ?>
</form>
</div>
<?php endif; // If registration required and not logged in ?>

<?php endif; // if you delete this the sky will fall on your head ?>
