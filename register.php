<?php

echo '<div class="container">';
echo '<div class="slider-container">';
echo '<div class="intro-text">';
echo '<div class="intro-lead-in">Contact Form</div>';

echo '<section id="about" class="light-bg">';
echo '<div class="container">';
echo '<div class="row">';
echo '<div class="col-lg-12 text-center">';
echo '<div class="section-title">';
if (!isset($_POST['submit']))
{
	echo '<form method="POST" action="">';
	echo '<div class="form-group">
<label class="control-label">Username:</label>
<input type="text" class="form-control" name="username" value="'.($_SESSION['username'] ?? '').'">
</div>';
	
	echo '<div class="form-group has-error">
<label class="control-label">Password:</label>
<input type="password" class="form-control" name="password" value="'.($_SESSION['password'] ?? '').'">
<span class="help-block">Password cannot be blank!</span>
</div>
<div class="form-group">
<input class="btn btn-success" type="submit" name="submit" value="submit">
</div>';
echo '</form>';
}
else
{
	$username=addslashes($_POST['username']);
	$password= $_POST['password'];
	$salt="CS4413SP26";
	$hash=hash("sha256",$password.$salt);
	$sql="Select `auto_id` from `accounts` where `logon`='$hash' and `username` = '$username'";
	$dblink=db_connect("admin");
	$result=$dblink->query($sql) or 
		die ("Something went wrong with $sql".$dblink->error);
	if ($result->num_rows<=0)//did not get a match
	redirect("index.php?page=login&errMsg=InvalidAcctInfo");
	else
	{
		$salt=microtime();
		$sid=hash('sha256',$salt.$password);
		$sql="Update `accounts` set `sid`='$sid' where `logon`='$hash' and `username`= '$username'";
		$dblink->query($sql) or 
			die ("Something went wrong with $sql". $dblink->error);
		redirect("index.php?page=results&sid=$sid");
	}
	
}
echo '</section>';
echo '</div>';
echo '</div>';
echo '</div>';
echo '</div>';
echo '</div>';
echo '</div>';
echo '</div>';

?>