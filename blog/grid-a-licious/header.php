<!DOCTYPE html 
      PUBLIC "-//W3C//DTD HTML 4.01//EN"
      "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en-US">
<head profile="http://www.w3.org/2005/10/profile">
<link rel="icon" 
      type="image/png" 
      href="http://www.whatevertrevor.co.uk/blog/wp-content/uploads/2009/11/WTfavicon2.png">


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title><?php bloginfo('name'); ?>: <?php bloginfo('description'); ?></title>
<link href="<?php bloginfo('stylesheet_url'); ?>" rel="stylesheet" type="text/css" media="screen" />
<link rel="alternate" type="application/rss+xml" title="<?php bloginfo('name'); ?> RSS Feed" href="<?php bloginfo('rss2_url'); ?>" />
<link rel="alternate" type="application/rss+xml" title="RSS 2.0" href="<?php bloginfo('rss2_url'); ?>" />
<link rel="alternate" type="text/xml" title="RSS .92" href="<?php bloginfo('rss_url'); ?>" />
<link rel="alternate" type="application/atom+xml" title="Atom 1.0" href="<?php bloginfo('atom_url'); ?>" />
<link rel="pingback" href="<?php bloginfo('pingback_url'); ?>" />

<script type="text/javascript" src="<?php bloginfo('stylesheet_directory'); ?>/scripts/jquery-1.2.6.pack.js"></script>
<script type="text/javascript" src="<?php bloginfo('stylesheet_directory'); ?>/scripts/grid-a-licious.js"></script>

</head>
<body>

<div class="eachpost " id="menuItem" style="background-color:#3c3c6f;">
<div>
<a href="<?php bloginfo('url'); ?>">
<img style="margin:0;padding:0;"
src="http://www.trev.whatevertrevor.co.uk/wp-content/uploads/2009/11/WT-TREV-LOGOFINALFINAL.png"
border="none">
</a>
</div>
</div>

<div class="eachpost " id="menuItem">
	<div id="signup">
<form action="http://whatevertrevor.createsend.com/t/r/s/ijdhhi/" method="post">
   <label for="ijdhhi-ijdhhi">Enter Email To Get Monday Updates</label><br /><input type="text" name="cm-ijdhhi-ijdhhi" id="ijdhhi-ijdhhi" /> <input type="submit" value="go" id="subscribe" />
</form>

<!--	 <?php wp_dropdown_pages('show_option_none=Select Page'); ?>
	<script type="text/javascript">
    var dropdownf = document.getElementById("page_id");
    function onPageChange() {
		if ( dropdownf.options[dropdownf.selectedIndex].value > 0 ) {
			location.href = "<?php echo get_option('home');
?>/?page_id="+dropdownf.options[dropdownf.selectedIndex].value;
		}
    }
    dropdownf.onchange = onPageChange;
</script>
-->
	</div>
</div>	

<div class="eachpost " id="menuItem">
	<div>
	<?php wp_dropdown_categories('show_option_none=Select Category'); ?>

	<script type="text/javascript"><!--
    var dropdown = document.getElementById("cat");
    function onCatChange() {
		if ( dropdown.options[dropdown.selectedIndex].value > 0 ) {
			location.href = "<?php echo get_option('home');
?>/?cat="+dropdown.options[dropdown.selectedIndex].value;
		}
    }
    dropdown.onchange = onCatChange;
--></script>
	</div>
</div>	
<div id="allposts"></div>

