<?php
require_once("functions.php");
if (!isset($_GET['page']))
	$page="home";
else
	$page=$_GET['page'];
?>
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

    echo '<div class="form-group">
    <label class="control-label">Password:</label>
    <input type="password" class="form-control" name="password">
    </div>';

    echo '<div class="form-group">
    <input class="btn btn-success" type="submit" name="submit" value="Submit">
    </div>';

    echo '</form>';
}
else
{
    $username = addslashes($_POST['username']);
    $password = $_POST['password'];
	$salt = "CS4413SP26";
	$hash = hash('sha256',$password.$salt);
    $sql = "SELECT `auto_id` FROM `accounts` WHERE `logon` = '$hash' and `username` = '$username'";
	$dblink = db_connect("admin");

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